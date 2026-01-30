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
from utils.pricing import calculate_cost, get_context_usage, format_context_window
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


# ==================== 파일 파싱 헬퍼 ====================

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


# ==================== 히스토리 헬퍼 ====================

def create_history_entry(text_input: str, uploaded_file, model_name: str, count: int, is_file_mode: bool) -> list:
    """
    히스토리 항목 생성

    Args:
        text_input: 텍스트 입력값
        uploaded_file: 업로드된 파일
        model_name: 모델 이름
        count: 토큰 수
        is_file_mode: 파일 모드 여부

    Returns:
        [display_input, model_name, count] 형식의 리스트
    """
    if is_file_mode and uploaded_file:
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
    try:
        encoder = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # gpt-5 등 새 모델은 gpt-4o와 같은 토크나이저 사용
        encoder = tiktoken.encoding_for_model("gpt-4o")
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

        elif "gpt" in model_name or model_name.startswith("o1") or model_name.startswith("o3"):
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
        elif "gpt" in model_name or model_name.startswith("o"):
            logger.error(f"tiktoken error: {e}")
            raise Exception(language_manager.get_text("api_error_openai", str(e)))
        raise


def is_commercial_model(model_name: str) -> bool:
    """모델이 상용 모델인지 확인"""
    keywords = ["claude", "gemini", "gpt", "o1", "o3"]
    return any(kw in model_name for kw in keywords) or model_name.startswith("o1") or model_name.startswith("o3")


# ==================== 결과 포맷팅 헬퍼 ====================

def format_cost_display(model_name: str, token_count: int) -> str:
    """비용 표시 문자열 생성"""
    cost = calculate_cost(model_name, token_count)
    if cost is None:
        return language_manager.get_text("cost_unknown")
    if cost < 0.01:
        return f"~${cost:.6f}"
    return f"~${cost:.4f}"


def format_context_display(model_name: str, token_count: int) -> str:
    """컨텍스트 사용률 표시 문자열 생성"""
    result = get_context_usage(model_name, token_count)
    if result is None:
        return language_manager.get_text("context_unknown")
    usage_percent, context_window = result
    formatted_window = format_context_window(context_window)
    return f"{usage_percent:.2f}% of {formatted_window}"


# ==================== 메인 처리 함수 ====================

def process_input_new(model_name_raw: str, text_input: str, uploaded_file,
                      is_commercial: bool, is_file_mode: bool, history_state: list):
    """
    토큰 카운팅 메인 처리 함수 (새 UI용)

    Args:
        model_name_raw: 선택된 모델 이름
        text_input: 텍스트 입력 (텍스트 모드일 때)
        uploaded_file: 업로드된 파일 (파일 모드일 때)
        is_commercial: 상용 모델 탭인지 여부
        is_file_mode: 파일 입력 모드인지 여부
        history_state: 현재 히스토리 상태
    """
    logs = []

    try:
        # 모델 이름 검증
        model_name = validate_model_name(model_name_raw)

        # 입력 데이터 가져오기
        if is_file_mode:
            data = parse_uploaded_file(uploaded_file, logs)
        else:
            if not text_input or not text_input.strip():
                raise InputEmptyError(language_manager.get_text("text_input_empty"))
            data = text_input

        if is_commercial:
            logs.append(language_manager.get_text("commercial_token_mode", model_name))
            count = count_tokens_commercial(model_name, data, logs)
            add_official_model(model_name)
        else:
            logs.append(language_manager.get_text("loading_tokenizer", model_name))
            try:
                tokenizer = load_tokenizer(model_name)
                logs.append(language_manager.get_text("tokenizer_load_complete"))
                add_custom_model(model_name)
            except Exception as e:
                logger.error(f"Tokenizer load error for {model_name}: {e}")
                logs.append(language_manager.get_text("tokenizer_load_error", str(e)))
                return (
                    "\n".join(logs),
                    "",
                    language_manager.get_text("cost_unknown"),
                    language_manager.get_text("context_unknown"),
                    gr.update(choices=get_official_models()),
                    gr.update(choices=get_custom_models()),
                    history_state,
                    gr.update(value=history_state)
                )

            logs.append(language_manager.get_text("calculating_tokens"))
            count = count_tokens(tokenizer, data)

        logs.append(language_manager.get_text("complete"))

        # 결과 생성
        cost_display = format_cost_display(model_name, count)
        context_display = format_context_display(model_name, count)

        # 히스토리 업데이트
        new_row = create_history_entry(text_input, uploaded_file, model_name, count, is_file_mode)
        new_history = update_history(history_state, new_row)

        return (
            "\n".join(logs),
            str(count),
            cost_display,
            context_display,
            gr.update(choices=get_official_models()),
            gr.update(choices=get_custom_models()),
            new_history,
            gr.update(value=new_history)
        )

    except ValidationError as e:
        logs.append(str(e))
        return (
            "\n".join(logs),
            "",
            "",
            "",
            None,
            None,
            history_state,
            None
        )
    except Exception as e:
        logger.error(f"Unexpected error in process_input: {e}")
        logs.append(str(e))
        return (
            "\n".join(logs),
            "",
            "",
            "",
            None,
            None,
            history_state,
            None
        )


def toggle_language():
    """언어 설정 토글 기능"""
    current_lang = language_manager.language_code
    new_lang = ENGLISH if current_lang == KOREAN else KOREAN
    language_manager.set_language(new_lang)
    SETTINGS.language = new_lang
    return new_lang


def create_interface():
    """새로운 탭 기반 UI 생성"""
    # 현재 언어 코드 설정
    language_manager.set_language(SETTINGS.language)

    with gr.Blocks() as demo:
        # 타이틀 및 안내
        title_md = gr.Markdown(language_manager.get_text("title"))
        quick_start_md = gr.Markdown(language_manager.get_text("quick_start"))

        # 언어 설정 (우측 상단에 배치)
        with gr.Row():
            with gr.Column(scale=4):
                pass
            with gr.Column(scale=1):
                language_label = gr.Markdown(language_manager.get_text("language_setting"))
                language_btn = gr.Button(
                    language_manager.get_text("korean" if language_manager.language_code == KOREAN else "english")
                )

        # 히스토리 상태
        history_state = gr.State(INITIAL_HISTORY)

        # 모델 유형 탭
        with gr.Tabs() as model_tabs:
            # ===== 상용 모델 탭 =====
            with gr.Tab(language_manager.get_text("tab_commercial"), id="commercial") as commercial_tab:
                commercial_model_dropdown = gr.Dropdown(
                    label=language_manager.get_text("model_select_label"),
                    choices=get_official_models(),
                    value=get_official_models()[0] if get_official_models() else None,
                    allow_custom_value=True,
                    filterable=True,
                    info=language_manager.get_text("model_placeholder_commercial")
                )

                # 입력 방식 탭 (상용 모델)
                with gr.Tabs() as commercial_input_tabs:
                    with gr.Tab(language_manager.get_text("tab_text_input"), id="commercial_text"):
                        commercial_text_input = gr.Textbox(
                            label=language_manager.get_text("text_input_label"),
                            placeholder=language_manager.get_text("text_placeholder"),
                            lines=6
                        )
                    with gr.Tab(language_manager.get_text("tab_file_upload"), id="commercial_file"):
                        commercial_file_input = gr.File(
                            label=language_manager.get_text("file_upload_label"),
                            file_types=[".pdf", ".txt", ".md", ".docx"]
                        )

                commercial_count_button = gr.Button(
                    language_manager.get_text("calculate_button"),
                    variant="primary",
                    size="lg"
                )

            # ===== 허깅페이스 모델 탭 =====
            with gr.Tab(language_manager.get_text("tab_huggingface"), id="huggingface") as huggingface_tab:
                huggingface_model_dropdown = gr.Dropdown(
                    label=language_manager.get_text("model_select_label"),
                    choices=get_custom_models(),
                    value=get_custom_models()[0] if get_custom_models() else None,
                    allow_custom_value=True,
                    filterable=True,
                    info=language_manager.get_text("model_placeholder_huggingface")
                )

                # 입력 방식 탭 (허깅페이스 모델)
                with gr.Tabs() as huggingface_input_tabs:
                    with gr.Tab(language_manager.get_text("tab_text_input"), id="huggingface_text"):
                        huggingface_text_input = gr.Textbox(
                            label=language_manager.get_text("text_input_label"),
                            placeholder=language_manager.get_text("text_placeholder"),
                            lines=6
                        )
                    with gr.Tab(language_manager.get_text("tab_file_upload"), id="huggingface_file"):
                        huggingface_file_input = gr.File(
                            label=language_manager.get_text("file_upload_label"),
                            file_types=[".pdf", ".txt", ".md", ".docx"]
                        )

                huggingface_count_button = gr.Button(
                    language_manager.get_text("calculate_button"),
                    variant="primary",
                    size="lg"
                )

        # ===== 결과 영역 =====
        with gr.Group():
            result_markdown = gr.Markdown(language_manager.get_text("result_title"))

            # 토큰, 비용, 컨텍스트 3열 표시
            with gr.Row():
                with gr.Column(scale=1):
                    count_output = gr.Textbox(
                        label=language_manager.get_text("tokens_label"),
                        interactive=False,
                        container=True
                    )
                with gr.Column(scale=1):
                    cost_output = gr.Textbox(
                        label=language_manager.get_text("estimated_cost"),
                        interactive=False,
                        container=True
                    )
                with gr.Column(scale=1):
                    context_output = gr.Textbox(
                        label=language_manager.get_text("context_window"),
                        interactive=False,
                        container=True
                    )

            status_output = gr.Textbox(
                label=language_manager.get_text("process_status"),
                lines=2,
                interactive=False
            )

        # 히스토리 테이블
        with gr.Group():
            history_label = gr.Markdown(language_manager.get_text("recent_history"))
            history_table = gr.DataFrame(
                value=INITIAL_HISTORY,
                headers=[
                    language_manager.get_text("history_input"),
                    language_manager.get_text("history_model"),
                    language_manager.get_text("history_count")
                ],
                interactive=False
            )

        # ===== 상용 모델 버튼 이벤트 =====
        # 텍스트 모드
        def process_commercial_text(model, text, history):
            return process_input_new(model, text, None, True, False, history)

        # 파일 모드
        def process_commercial_file(model, file, history):
            return process_input_new(model, "", file, True, True, history)

        # 상용 모델 - 텍스트 입력 후 계산
        commercial_count_button.click(
            fn=lambda model, text, file, history: (
                process_commercial_file(model, file, history) if file is not None
                else process_commercial_text(model, text, history)
            ),
            inputs=[
                commercial_model_dropdown,
                commercial_text_input,
                commercial_file_input,
                history_state
            ],
            outputs=[
                status_output,
                count_output,
                cost_output,
                context_output,
                commercial_model_dropdown,
                huggingface_model_dropdown,
                history_state,
                history_table
            ]
        )

        # ===== 허깅페이스 모델 버튼 이벤트 =====
        def process_huggingface_text(model, text, history):
            return process_input_new(model, text, None, False, False, history)

        def process_huggingface_file(model, file, history):
            return process_input_new(model, "", file, False, True, history)

        huggingface_count_button.click(
            fn=lambda model, text, file, history: (
                process_huggingface_file(model, file, history) if file is not None
                else process_huggingface_text(model, text, history)
            ),
            inputs=[
                huggingface_model_dropdown,
                huggingface_text_input,
                huggingface_file_input,
                history_state
            ],
            outputs=[
                status_output,
                count_output,
                cost_output,
                context_output,
                commercial_model_dropdown,
                huggingface_model_dropdown,
                history_state,
                history_table
            ]
        )

        # ===== 언어 변경 이벤트 =====
        def update_ui_language(lang):
            """UI 언어 업데이트"""
            return [
                language_manager.get_text("title"),
                language_manager.get_text("quick_start"),
                language_manager.get_text("language_setting"),
                language_manager.get_text("korean") if lang == KOREAN else language_manager.get_text("english"),
                gr.update(
                    label=language_manager.get_text("model_select_label"),
                    info=language_manager.get_text("model_placeholder_commercial")
                ),
                gr.update(
                    label=language_manager.get_text("model_select_label"),
                    info=language_manager.get_text("model_placeholder_huggingface")
                ),
                gr.update(label=language_manager.get_text("text_input_label"),
                          placeholder=language_manager.get_text("text_placeholder")),
                gr.update(label=language_manager.get_text("file_upload_label")),
                gr.update(label=language_manager.get_text("text_input_label"),
                          placeholder=language_manager.get_text("text_placeholder")),
                gr.update(label=language_manager.get_text("file_upload_label")),
                language_manager.get_text("calculate_button"),
                language_manager.get_text("calculate_button"),
                language_manager.get_text("result_title"),
                gr.update(label=language_manager.get_text("tokens_label")),
                gr.update(label=language_manager.get_text("estimated_cost")),
                gr.update(label=language_manager.get_text("context_window")),
                gr.update(label=language_manager.get_text("process_status")),
                language_manager.get_text("recent_history"),
                gr.update(headers=[
                    language_manager.get_text("history_input"),
                    language_manager.get_text("history_model"),
                    language_manager.get_text("history_count")
                ])
            ]

        language_btn.click(
            toggle_language,
            outputs=gr.State(language_manager.language_code)
        ).then(
            update_ui_language,
            inputs=gr.State(language_manager.language_code),
            outputs=[
                title_md,
                quick_start_md,
                language_label,
                language_btn,
                commercial_model_dropdown,
                huggingface_model_dropdown,
                commercial_text_input,
                commercial_file_input,
                huggingface_text_input,
                huggingface_file_input,
                commercial_count_button,
                huggingface_count_button,
                result_markdown,
                count_output,
                cost_output,
                context_output,
                status_output,
                history_label,
                history_table
            ]
        )

        # ===== 페이지 로드 시 모델 목록 새로고침 =====
        def refresh_model_lists():
            """페이지 로드 시 최신 모델 목록 반환"""
            official = get_official_models()
            custom = get_custom_models()
            return (
                gr.update(choices=official, value=official[0] if official else None),
                gr.update(choices=custom, value=custom[0] if custom else None)
            )

        demo.load(
            fn=refresh_model_lists,
            outputs=[commercial_model_dropdown, huggingface_model_dropdown]
        )

    return demo
