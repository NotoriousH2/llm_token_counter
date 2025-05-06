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

def process_input(model_type, official_select_mode, official_dropdown, official_input, custom_select_mode, custom_dropdown, custom_input, input_mode, text_input, uploaded_file, history_state):
    logs = []
    # 모델 타입 결정 및 모델명 선택
    if model_type == language_manager.get_text("commercial_model"):
        # 입력 모드에 따라 드롭다운 또는 직접 입력 사용
        if official_select_mode == language_manager.get_text("select_from_list"):
            model_name_raw = official_dropdown
        else:
            model_name_raw = official_input.strip()
        model_name = model_name_raw.strip()
        lower_name = model_name.lower()
        model_name = lower_name
        logs.append(language_manager.get_text("commercial_token_mode", model_name))
        # 입력 방식 처리
        if input_mode == language_manager.get_text("file_upload"):
            logs.append(language_manager.get_text("processing_file"))
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            try:
                if ext == ".pdf":
                    data = parse_pdf(uploaded_file.name)
                elif ext == ".docx":
                    data = parse_docx(uploaded_file.name)
                elif ext in [".txt", ".md"]:
                    data = parse_text(uploaded_file.name)
                else:
                    logs.append(language_manager.get_text("unsupported_file"))
                    return "\n".join(logs), "", None, None, history_state, None
                logs.append(language_manager.get_text("file_parsing_complete"))
            except Exception as e:
                logs.append(language_manager.get_text("file_parsing_error", str(e)))
                return "\n".join(logs), "", None, None, history_state, None
        elif input_mode == language_manager.get_text("text_input"):
            data = text_input or ""
        else:
            return language_manager.get_text("select_input_method"), "", None, None, history_state, None
        logs.append(language_manager.get_text("calculating_tokens"))
        # 상용 모델별 토큰 계산
        if "claude" in model_name.lower():
            client = anthropic.Anthropic()
            response = client.messages.count_tokens(
                model=model_name.lower().replace('.','-')+'-latest',
                system="",
                messages=[{"role":"user","content":data}],
            )
            print(response)
            count = response.input_tokens - 7
            
            # 템플릿 비용 7토큰 제거
        elif "gemini" in model_name.lower():
            client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))
            response = client.models.count_tokens(
                model=model_name.lower(),
                contents=data
            )
            count = response.total_tokens
        elif "gpt" in model_name.lower():
            print(model_name)
            encoder = tiktoken.encoding_for_model(model_name.lower())
            count = len(encoder.encode(data))
        else:
            logs.append(language_manager.get_text("unsupported_commercial_model"))
            return "\n".join(logs), "", None, None, history_state, None
        logs.append(language_manager.get_text("complete"))
        # 모델 저장 완료 후, 히스토리 업데이트
        updated_official = get_official_models()
        updated_custom = get_custom_models()
        display_input = uploaded_file.name.split('/')[-1].split('\\')[-1] if input_mode == language_manager.get_text("file_upload") else (text_input if len(text_input) <= 10 else text_input[:10] + '...')
        new_row = [display_input, model_name, count]
        add_official_model(lower_name)
        new_history = ([new_row] + history_state)[:5]
        return "\n".join(logs), str(count), gr.update(choices=updated_official), gr.update(choices=updated_custom), new_history, gr.update(value=new_history)
    elif model_type == language_manager.get_text("huggingface_model"):
        # 입력 모드에 따라 드롭다운 또는 직접 입력 사용
        if custom_select_mode == language_manager.get_text("select_from_list"):
            model_name_raw = custom_dropdown
        else:
            model_name_raw = custom_input.strip()
        model_name = model_name_raw.strip()
        lower_name = model_name.lower()
        model_name = lower_name
        logs.append(language_manager.get_text("loading_tokenizer", model_name))
        try:
            tokenizer = load_tokenizer(model_name)
            logs.append(language_manager.get_text("tokenizer_load_complete"))
            add_custom_model(lower_name)
        except Exception as e:
            logs.append(language_manager.get_text("tokenizer_load_error", str(e)))
            return "\n".join(logs), "", None, None, history_state, None
        # 입력 처리
        if input_mode == language_manager.get_text("file_upload"):
            logs.append(language_manager.get_text("processing_file"))
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            try:
                if ext == ".pdf":
                    data = parse_pdf(uploaded_file.name)
                elif ext == ".docx":
                    data = parse_docx(uploaded_file.name)
                elif ext in [".txt", ".md"]:
                    data = parse_text(uploaded_file.name)
                else:
                    logs.append(language_manager.get_text("unsupported_file"))
                    return "\n".join(logs), "", None, None, history_state, None
                logs.append(language_manager.get_text("file_parsing_complete"))
            except Exception as e:
                logs.append(language_manager.get_text("file_parsing_error", str(e)))
                return "\n".join(logs), "", None, None, history_state, None
        elif input_mode == language_manager.get_text("text_input"):
            data = text_input or ""
        else:
            return language_manager.get_text("select_input_method"), "", None, None, history_state, None
        logs.append(language_manager.get_text("calculating_tokens"))
        count = count_tokens(tokenizer, data)
        logs.append(language_manager.get_text("complete"))
        # 모델 저장 완료 후, 히스토리 업데이트
        updated_official = get_official_models()
        updated_custom = get_custom_models()
        display_input = uploaded_file.name.split('/')[-1].split('\\')[-1] if input_mode == language_manager.get_text("file_upload") else (text_input if len(text_input) <= 10 else text_input[:10] + '...')
        new_row = [display_input, model_name, count]
        new_history = ([new_row] + history_state)[:5]
        return "\n".join(logs), str(count), gr.update(choices=updated_official), gr.update(choices=updated_custom), new_history, gr.update(value=new_history)
    else:
        # 오류 반환 시에는 히스토리와 테이블 unchanged
        return language_manager.get_text("select_model_type"), "", None, None, history_state, None

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
                gr.update(visible=False), # official_model_input
                gr.update(visible=not is_commercial), # custom_select_mode
                gr.update(visible=not is_commercial), # custom_model_dropdown
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