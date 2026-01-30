import os
import gradio as gr
import anthropic
from google import genai
from core.tokenizer_loader import load_tokenizer
from core.token_counter import count_tokens
from parsers import parse_pdf, parse_docx, parse_text
from utils.config import SETTINGS
from utils.logger import get_logger
from utils.languages import language_manager, KOREAN, ENGLISH
import tiktoken
from dotenv import load_dotenv
from utils.model_store import get_official_models, get_custom_models, add_official_model, add_custom_model

load_dotenv()
logger = get_logger(__name__)

# 최초 실행시 표시할 최근 기록 (5개)
INITIAL_HISTORY = [
    ["안녕하세요", "gpt-4o", 2],
    ["안녕하세요", "claude-3-7-sonnet", 7],
    ["안녕하세요", "gemini-2.0-flash", 2],
    ["안녕하세요", "qwen/qwen3-8b", 3],
    ["안녕하세요", "deepseek-r1", 6],
]


# ==================== 커스텀 예외 클래스 ====================

class ValidationError(Exception):
    """기본 유효성 검사 에러"""
    pass


class APIKeyMissingError(ValidationError):
    """API 키 누락 에러"""
    pass


class FileSizeExceededError(ValidationError):
    """파일 크기 초과 에러"""
    pass


class ModelNameError(ValidationError):
    """모델 이름 에러"""
    pass


class InputEmptyError(ValidationError):
    """입력 비어있음 에러"""
    pass


# ==================== 유효성 검사 헬퍼 ====================

def validate_model_name(model_name: str) -> str:
    """
    모델 이름 검증 및 정규화

    Args:
        model_name: 원본 모델 이름

    Returns:
        정규화된 모델 이름 (lowercase, strip)

    Raises:
        ModelNameError: 모델 이름이 비어있거나 유효하지 않을 때
    """
    if not model_name or not model_name.strip():
        raise ModelNameError(language_manager.get_text("model_name_empty"))

    normalized = model_name.strip().lower()

    if len(normalized) < 2:
        raise ModelNameError(language_manager.get_text("model_name_invalid", normalized))

    return normalized


def validate_api_key_for_model(model_name: str) -> None:
    """
    모델에 필요한 API 키 존재 여부 확인

    Args:
        model_name: 정규화된 모델 이름

    Raises:
        APIKeyMissingError: API 키가 설정되지 않았을 때
    """
    if "claude" in model_name:
        if not SETTINGS.has_anthropic_key():
            raise APIKeyMissingError(language_manager.get_text("api_key_missing_anthropic"))
    elif "gemini" in model_name:
        if not SETTINGS.has_google_key():
            raise APIKeyMissingError(language_manager.get_text("api_key_missing_google"))


def validate_file_size(file_path: str) -> None:
    """
    파일 크기 검증

    Args:
        file_path: 파일 경로

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        FileSizeExceededError: 파일 크기가 제한을 초과할 때
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(language_manager.get_text("file_not_found", file_path))

    file_size = os.path.getsize(file_path)
    max_size = SETTINGS.get_max_file_size_bytes()

    if file_size > max_size:
        file_size_mb = file_size / (1024 * 1024)
        raise FileSizeExceededError(
            language_manager.get_text("file_too_large", (file_size_mb, SETTINGS.max_file_size_mb))
        )


# ==================== 파일 파싱 헬퍼 (중복 제거) ====================

def parse_uploaded_file(uploaded_file, logs: list) -> str:
    """
    업로드된 파일 파싱

    Args:
        uploaded_file: Gradio 파일 업로드 객체
        logs: 로그 메시지 리스트

    Returns:
        파싱된 텍스트

    Raises:
        InputEmptyError: 파일이 없을 때
        FileSizeExceededError: 파일 크기 초과
        ValueError: 지원하지 않는 형식
        Exception: 파싱 에러
    """
    if uploaded_file is None:
        raise InputEmptyError(language_manager.get_text("file_upload_required"))

    file_path = uploaded_file.name

    # 파일 크기 검증
    validate_file_size(file_path)

    logs.append(language_manager.get_text("processing_file"))
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            data = parse_pdf(file_path)
        elif ext == ".docx":
            data = parse_docx(file_path)
        elif ext in [".txt", ".md"]:
            data = parse_text(file_path)
        else:
            raise ValueError(language_manager.get_text("unsupported_file"))

        logs.append(language_manager.get_text("file_parsing_complete"))
        return data

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"File parsing error: {e}")
        raise Exception(language_manager.get_text("file_parsing_error", str(e)))


def get_input_data(input_mode: str, text_input: str, uploaded_file, logs: list) -> str:
    """
    입력 모드에 따른 데이터 가져오기

    Args:
        input_mode: 입력 모드 ("텍스트 입력" 또는 "파일 업로드")
        text_input: 텍스트 입력값
        uploaded_file: 업로드된 파일
        logs: 로그 메시지 리스트

    Returns:
        처리할 텍스트 데이터

    Raises:
        InputEmptyError: 입력이 비어있을 때
        Exception: 파일 파싱 에러
    """
    if input_mode == language_manager.get_text("file_upload"):
        return parse_uploaded_file(uploaded_file, logs)
    elif input_mode == language_manager.get_text("text_input"):
        if not text_input or not text_input.strip():
            raise InputEmptyError(language_manager.get_text("text_input_empty"))
        return text_input
    else:
        raise ValueError(language_manager.get_text("select_input_method"))


# ==================== 히스토리 헬퍼 (중복 제거) ====================

def create_history_entry(input_mode: str, text_input: str, uploaded_file, model_name: str, count: int) -> list:
    """
    히스토리 항목 생성

    Args:
        input_mode: 입력 모드
        text_input: 텍스트 입력값
        uploaded_file: 업로드된 파일
        model_name: 모델 이름
        count: 토큰 수

    Returns:
        [display_input, model_name, count] 형식의 리스트
    """
    if input_mode == language_manager.get_text("file_upload") and uploaded_file:
        display_input = uploaded_file.name.split('/')[-1].split('\\')[-1]
    else:
        display_input = text_input if len(text_input or '') <= 10 else (text_input[:10] + '...')

    return [display_input, model_name, count]


def update_history(history_state: list, new_row: list) -> list:
    """
    히스토리 업데이트 (최대 5개 유지)

    Args:
        history_state: 현재 히스토리
        new_row: 새 항목

    Returns:
        업데이트된 히스토리
    """
    return ([new_row] + history_state)[:5]


def create_success_response(logs: list, count: int, history_state: list, new_row: list):
    """
    성공 응답 생성

    Args:
        logs: 로그 메시지 리스트
        count: 토큰 수
        history_state: 현재 히스토리
        new_row: 새 히스토리 항목

    Returns:
        Gradio 출력용 튜플
    """
    updated_official = get_official_models()
    updated_custom = get_custom_models()
    new_history = update_history(history_state, new_row)

    return (
        "\n".join(logs),
        str(count),
        gr.update(choices=updated_official),
        gr.update(choices=updated_custom),
        new_history,
        gr.update(value=new_history)
    )


def create_error_response(message: str, history_state: list):
    """
    에러 응답 생성

    Args:
        message: 에러 메시지
        history_state: 현재 히스토리 (변경 없음)

    Returns:
        Gradio 출력용 튜플
    """
    return (message, "", None, None, history_state, None)


# ==================== 토큰 카운팅 헬퍼 ====================

def count_tokens_claude(model_name: str, data: str) -> int:
    """
    Anthropic API로 토큰 수 계산

    Args:
        model_name: Claude 모델 이름
        data: 텍스트

    Returns:
        토큰 수
    """
    client = anthropic.Anthropic(api_key=SETTINGS.anthropic_api_key)
    response = client.messages.count_tokens(
        model=model_name.replace('.', '-'),
        system="",
        messages=[{"role": "user", "content": data}],
    )
    # 템플릿 비용 7토큰 제거
    return response.input_tokens - 7


def count_tokens_gemini(model_name: str, data: str) -> int:
    """
    Google Gemini API로 토큰 수 계산

    Args:
        model_name: Gemini 모델 이름
        data: 텍스트

    Returns:
        토큰 수
    """
    client = genai.Client(api_key=SETTINGS.google_api_key)
    response = client.models.count_tokens(
        model=model_name,
        contents=data
    )
    return response.total_tokens


def count_tokens_gpt(model_name: str, data: str) -> int:
    """
    tiktoken으로 GPT 토큰 수 계산

    Args:
        model_name: GPT 모델 이름
        data: 텍스트

    Returns:
        토큰 수
    """
    encoder = tiktoken.encoding_for_model(model_name)
    return len(encoder.encode(data))


def count_tokens_commercial(model_name: str, data: str, logs: list) -> int:
    """
    상용 모델 토큰 수 계산

    Args:
        model_name: 정규화된 모델 이름
        data: 텍스트
        logs: 로그 메시지 리스트

    Returns:
        토큰 수

    Raises:
        APIKeyMissingError: API 키 누락
        ValueError: 지원하지 않는 모델
        Exception: API 에러
    """
    logs.append(language_manager.get_text("calculating_tokens"))

    try:
        if "claude" in model_name:
            validate_api_key_for_model(model_name)
            return count_tokens_claude(model_name, data)

        elif "gemini" in model_name:
            validate_api_key_for_model(model_name)
            return count_tokens_gemini(model_name, data)

        elif "gpt" in model_name:
            return count_tokens_gpt(model_name, data)

        else:
            raise ValueError(language_manager.get_text("unsupported_commercial_model"))

    except (APIKeyMissingError, ValueError):
        raise
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise Exception(language_manager.get_text("api_error_anthropic", str(e)))
    except Exception as e:
        if "gemini" in model_name:
            logger.error(f"Google API error: {e}")
            raise Exception(language_manager.get_text("api_error_google", str(e)))
        elif "gpt" in model_name:
            logger.error(f"tiktoken error: {e}")
            raise Exception(language_manager.get_text("api_error_openai", str(e)))
        raise


# ==================== 메인 처리 함수 ====================

def process_input(model_type, official_select_mode, official_dropdown, official_input,
                  custom_select_mode, custom_dropdown, custom_input,
                  input_mode, text_input, uploaded_file, history_state):
    """
    토큰 카운팅 메인 처리 함수

    헬퍼 함수를 사용하여:
    - 입력 유효성 검사
    - 파일 파싱 (중복 제거됨)
    - 모델별 토큰 카운팅
    - 히스토리 업데이트 (중복 제거됨)
    - 구체적인 예외 처리
    """
    logs = []

    try:
        if model_type == language_manager.get_text("commercial_model"):
            # 모델 이름 가져오기 및 검증
            if official_select_mode == language_manager.get_text("select_from_list"):
                model_name_raw = official_dropdown
            else:
                model_name_raw = official_input

            model_name = validate_model_name(model_name_raw)
            logs.append(language_manager.get_text("commercial_token_mode", model_name))

            # 입력 데이터 가져오기 (헬퍼 함수 사용 - 중복 제거)
            data = get_input_data(input_mode, text_input, uploaded_file, logs)

            # 토큰 수 계산 (구체적인 예외 처리 포함)
            count = count_tokens_commercial(model_name, data, logs)
            logs.append(language_manager.get_text("complete"))

            # 모델 저장 및 히스토리 업데이트 (헬퍼 함수 사용 - 중복 제거)
            add_official_model(model_name)
            new_row = create_history_entry(input_mode, text_input, uploaded_file, model_name, count)
            return create_success_response(logs, count, history_state, new_row)

        elif model_type == language_manager.get_text("huggingface_model"):
            # 모델 이름 가져오기 및 검증
            if custom_select_mode == language_manager.get_text("select_from_list"):
                model_name_raw = custom_dropdown
            else:
                model_name_raw = custom_input

            model_name = validate_model_name(model_name_raw)
            logs.append(language_manager.get_text("loading_tokenizer", model_name))

            # 토크나이저 로드
            try:
                tokenizer = load_tokenizer(model_name)
                logs.append(language_manager.get_text("tokenizer_load_complete"))
                add_custom_model(model_name)  # 성공 후 모델 저장
            except Exception as e:
                logger.error(f"Tokenizer load error for {model_name}: {e}")
                logs.append(language_manager.get_text("tokenizer_load_error", str(e)))
                return create_error_response("\n".join(logs), history_state)

            # 입력 데이터 가져오기 (헬퍼 함수 사용 - 중복 제거)
            data = get_input_data(input_mode, text_input, uploaded_file, logs)

            # 토큰 수 계산
            logs.append(language_manager.get_text("calculating_tokens"))
            count = count_tokens(tokenizer, data)
            logs.append(language_manager.get_text("complete"))

            # 히스토리 업데이트 (헬퍼 함수 사용 - 중복 제거)
            new_row = create_history_entry(input_mode, text_input, uploaded_file, model_name, count)
            return create_success_response(logs, count, history_state, new_row)

        else:
            return create_error_response(
                language_manager.get_text("select_model_type"),
                history_state
            )

    except ValidationError as e:
        # 모든 유효성 검사 에러 통합 처리
        logs.append(str(e))
        return create_error_response("\n".join(logs), history_state)
    except Exception as e:
        # 예상치 못한 에러
        logger.error(f"Unexpected error in process_input: {e}")
        logs.append(str(e))
        return create_error_response("\n".join(logs), history_state)


def toggle_language():
    """언어 설정 토글 기능"""
    current_lang = language_manager.language_code
    new_lang = ENGLISH if current_lang == KOREAN else KOREAN
    language_manager.set_language(new_lang)
    SETTINGS.language = new_lang
    return new_lang


def update_ui_language(lang):
    """UI 언어 업데이트"""
    return [
        language_manager.get_text("title"),
        language_manager.get_text("subtitle"),
        gr.update(label=language_manager.get_text("model_type_label"),
                  choices=[language_manager.get_text("commercial_model"), language_manager.get_text("huggingface_model")],
                  value=language_manager.get_text("commercial_model")),
        gr.update(label=language_manager.get_text("input_mode_commercial"),
                  choices=[language_manager.get_text("select_from_list"), language_manager.get_text("direct_input")],
                  value=language_manager.get_text("select_from_list")),
        gr.update(label=language_manager.get_text("commercial_model_select")),
        gr.update(label=language_manager.get_text("model_id_input_commercial"),
                  placeholder=language_manager.get_text("model_id_placeholder_commercial")),
        gr.update(label=language_manager.get_text("input_mode_huggingface"),
                  choices=[language_manager.get_text("select_from_list"), language_manager.get_text("direct_input")],
                  value=language_manager.get_text("select_from_list")),
        gr.update(label=language_manager.get_text("huggingface_model_select")),
        gr.update(label=language_manager.get_text("model_id_input_huggingface"),
                  placeholder=language_manager.get_text("model_id_placeholder_huggingface")),
        gr.update(label=language_manager.get_text("input_method"),
                  choices=[language_manager.get_text("text_input"), language_manager.get_text("file_upload")],
                  value=language_manager.get_text("text_input")),
        gr.update(label=language_manager.get_text("text_input_label")),
        gr.update(label=language_manager.get_text("file_upload_label")),
        language_manager.get_text("result_title"),
        language_manager.get_text("calculate_button"),
        gr.update(label=language_manager.get_text("process_status")),
        gr.update(label=language_manager.get_text("token_count")),
        gr.update(headers=[
            language_manager.get_text("history_input"),
            language_manager.get_text("history_model"),
            language_manager.get_text("history_count")
        ]),
        language_manager.get_text("language_setting"),
        language_manager.get_text("korean") if lang == KOREAN else language_manager.get_text("english")
    ]


def create_interface():
    # 현재 언어 코드 설정
    language_manager.set_language(SETTINGS.language)

    with gr.Blocks() as demo:
        # UI 컴포넌트를 언어 리소스에서 가져오기
        title_md = gr.Markdown(language_manager.get_text("title"))
        subtitle_md = gr.Markdown(language_manager.get_text("subtitle"))

        # 언어 설정 (우측 상단에 배치)
        with gr.Row():
            with gr.Column(scale=4):
                pass
            with gr.Column(scale=1):
                language_label = gr.Markdown(language_manager.get_text("language_setting"))
                language_btn = gr.Button(language_manager.get_text("korean" if language_manager.language_code == KOREAN else "english"))

        with gr.Row():
            with gr.Column():
                # 모델 유형(Radio)
                model_type = gr.Radio(
                    label=language_manager.get_text("model_type_label"),
                    choices=[language_manager.get_text("commercial_model"), language_manager.get_text("huggingface_model")],
                    value=language_manager.get_text("commercial_model")
                )

                # 상용 모델 입력 방식 선택
                official_select_mode = gr.Radio(
                    label=language_manager.get_text("input_mode_commercial"),
                    choices=[language_manager.get_text("select_from_list"), language_manager.get_text("direct_input")],
                    value=language_manager.get_text("select_from_list"),
                    visible=True
                )
                official_model_dropdown = gr.Dropdown(
                    label=language_manager.get_text("commercial_model_select"),
                    choices=get_official_models(),
                    value=get_official_models()[0],
                    visible=True
                )
                official_model_input = gr.Textbox(
                    label=language_manager.get_text("model_id_input_commercial"),
                    placeholder=language_manager.get_text("model_id_placeholder_commercial"),
                    visible=False
                )

                # 허깅페이스 모델 입력 방식 선택
                custom_select_mode = gr.Radio(
                    label=language_manager.get_text("input_mode_huggingface"),
                    choices=[language_manager.get_text("select_from_list"), language_manager.get_text("direct_input")],
                    value=language_manager.get_text("select_from_list"),
                    visible=False
                )
                custom_model_dropdown = gr.Dropdown(
                    label=language_manager.get_text("huggingface_model_select"),
                    choices=get_custom_models(),
                    value=get_custom_models()[0],
                    visible=False
                )
                custom_model_input = gr.Textbox(
                    label=language_manager.get_text("model_id_input_huggingface"),
                    placeholder=language_manager.get_text("model_id_placeholder_huggingface"),
                    visible=False
                )

                input_mode = gr.Radio(
                    label=language_manager.get_text("input_method"),
                    choices=[language_manager.get_text("text_input"), language_manager.get_text("file_upload")],
                    value=language_manager.get_text("text_input")
                )
                text_input = gr.Textbox(
                    label=language_manager.get_text("text_input_label"),
                    lines=8,
                    visible=True
                )
                file_input = gr.File(
                    label=language_manager.get_text("file_upload_label"),
                    file_types=[".pdf", ".txt", ".md", ".docx"],
                    visible=False
                )

            with gr.Column():
                result_markdown = gr.Markdown(language_manager.get_text("result_title"))
                count_button = gr.Button(language_manager.get_text("calculate_button"))
                status_output = gr.Textbox(label=language_manager.get_text("process_status"), lines=4, interactive=False)
                count_output = gr.Textbox(label=language_manager.get_text("token_count"), interactive=False)
                # 최근 기록 테이블 및 상태
                history_state = gr.State(INITIAL_HISTORY)
                history_table = gr.DataFrame(
                    value=INITIAL_HISTORY,
                    headers=[
                        language_manager.get_text("history_input"),
                        language_manager.get_text("history_model"),
                        language_manager.get_text("history_count")
                    ],
                    interactive=False
                )

        # 언어 변경 이벤트 핸들링
        language_btn.click(
            toggle_language,
            outputs=gr.State(language_manager.language_code)
        ).then(
            update_ui_language,
            inputs=gr.State(language_manager.language_code),
            outputs=[
                title_md, subtitle_md,
                model_type,
                official_select_mode,
                official_model_dropdown,
                official_model_input,
                custom_select_mode,
                custom_model_dropdown,
                custom_model_input,
                input_mode,
                text_input,
                file_input,
                result_markdown,
                count_button,
                status_output,
                count_output,
                history_table,
                language_label,
                language_btn
            ]
        )

        # 모델 유형 토글
        def toggle_model_type(mode):
            is_commercial = mode == language_manager.get_text("commercial_model")
            return (
                gr.update(visible=is_commercial),  # official_select_mode
                gr.update(visible=is_commercial),  # official_model_dropdown
                gr.update(visible=False),  # official_model_input
                gr.update(visible=not is_commercial),  # custom_select_mode
                gr.update(visible=not is_commercial),  # custom_model_dropdown
                gr.update(visible=False)  # custom_model_input
            )

        model_type.change(
            toggle_model_type,
            inputs=[model_type],
            outputs=[official_select_mode, official_model_dropdown, official_model_input, custom_select_mode, custom_model_dropdown, custom_model_input]
        )

        # 상용 모델 입력 방식 토글
        def toggle_official_input_mode(mode):
            is_dropdown = mode == language_manager.get_text("select_from_list")
            return (
                gr.update(visible=is_dropdown),
                gr.update(visible=not is_dropdown)
            )

        official_select_mode.change(
            toggle_official_input_mode,
            inputs=[official_select_mode],
            outputs=[official_model_dropdown, official_model_input]
        )

        # 허깅페이스 모델 입력 방식 토글
        def toggle_custom_input_mode(mode):
            is_dropdown = mode == language_manager.get_text("select_from_list")
            return (
                gr.update(visible=is_dropdown),
                gr.update(visible=not is_dropdown)
            )

        custom_select_mode.change(
            toggle_custom_input_mode,
            inputs=[custom_select_mode],
            outputs=[custom_model_dropdown, custom_model_input]
        )

        # 입력 방식 선택
        def toggle_input_mode(mode):
            is_text = mode == language_manager.get_text("text_input")
            return (
                gr.update(visible=is_text),
                gr.update(visible=not is_text)
            )

        input_mode.change(
            toggle_input_mode,
            inputs=[input_mode],
            outputs=[text_input, file_input]
        )

        # 토큰 계산 실행
        count_button.click(
            fn=process_input,
            inputs=[
                model_type, official_select_mode, official_model_dropdown, official_model_input,
                custom_select_mode, custom_model_dropdown, custom_model_input,
                input_mode, text_input, file_input, history_state
            ],
            outputs=[
                status_output, count_output,
                official_model_dropdown, custom_model_dropdown,
                history_state, history_table
            ]
        )

    return demo
