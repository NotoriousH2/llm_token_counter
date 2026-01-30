"""
다국어 지원을 위한 언어 리소스 관리 모듈
"""

# 언어 코드 정의
KOREAN = "kor"
ENGLISH = "eng"

# 언어별 텍스트 리소스
TEXT_RESOURCES = {
    # 제목 및 설명
    "title": {
        KOREAN: "## LLM 토큰 카운터 (https://github.com/NotoriousH2/llm_token_counter)",
        ENGLISH: "## LLM Token Counter (https://github.com/NotoriousH2/llm_token_counter)"
    },
    "subtitle": {
        KOREAN: "템플릿 변환에 필요한 비용은 포함하지 않습니다. Ex) GPT, Claude 종류는 7토큰 추가",
        ENGLISH: "Template conversion costs are not included. Ex) GPT, Claude types add 7 tokens"
    },

    # 모델 유형 섹션
    "model_type_label": {
        KOREAN: "모델 유형",
        ENGLISH: "Model Type"
    },
    "commercial_model": {
        KOREAN: "상용 모델",
        ENGLISH: "Commercial Model"
    },
    "huggingface_model": {
        KOREAN: "허깅페이스 모델", 
        ENGLISH: "Huggingface Model"
    },

    # 입력 방식 섹션
    "input_mode_commercial": {
        KOREAN: "상용 모델 입력 방식",
        ENGLISH: "Commercial Model Input Method"
    },
    "input_mode_huggingface": {
        KOREAN: "허깅페이스 모델 입력 방식",
        ENGLISH: "Huggingface Model Input Method"
    },
    "select_from_list": {
        KOREAN: "목록에서 선택",
        ENGLISH: "Select from List"
    },
    "direct_input": {
        KOREAN: "직접 입력",
        ENGLISH: "Direct Input"
    },

    # 모델 선택 섹션
    "commercial_model_select": {
        KOREAN: "상용 모델 선택",
        ENGLISH: "Select Commercial Model"
    },
    "huggingface_model_select": {
        KOREAN: "허깅페이스 모델 선택",
        ENGLISH: "Select Huggingface Model"
    },
    "model_id_input_commercial": {
        KOREAN: "모델 ID 직접 입력",
        ENGLISH: "Enter Model ID Directly"
    },
    "model_id_placeholder_commercial": {
        KOREAN: "예: gemini-2.5-pro-exp-03-25",
        ENGLISH: "e.g. gemini-2.5-pro-exp-03-25"
    },
    "model_id_input_huggingface": {
        KOREAN: "모델 ID 직접 입력",
        ENGLISH: "Enter Model ID Directly"
    },
    "model_id_placeholder_huggingface": {
        KOREAN: "username/model-name",
        ENGLISH: "username/model-name"
    },

    # 입력 방식 섹션
    "input_method": {
        KOREAN: "입력 방식",
        ENGLISH: "Input Method"
    },
    "text_input": {
        KOREAN: "텍스트 입력",
        ENGLISH: "Text Input"
    },
    "file_upload": {
        KOREAN: "파일 업로드",
        ENGLISH: "File Upload"
    },
    "text_input_label": {
        KOREAN: "텍스트 입력",
        ENGLISH: "Enter Text"
    },
    "file_upload_label": {
        KOREAN: "파일 업로드 (.pdf, .txt, .md, .docx)",
        ENGLISH: "Upload File (.pdf, .txt, .md, .docx)"
    },

    # 결과 섹션
    "result_title": {
        KOREAN: "## 결과",
        ENGLISH: "## Results"
    },
    "calculate_button": {
        KOREAN: "토큰 수 계산하기",
        ENGLISH: "Calculate Tokens"
    },
    "process_status": {
        KOREAN: "처리 상태",
        ENGLISH: "Process Status"
    },
    "token_count": {
        KOREAN: "총 토큰 수",
        ENGLISH: "Total Token Count"
    },

    # 히스토리 테이블
    "history_input": {
        KOREAN: "입력",
        ENGLISH: "Input"
    },
    "history_model": {
        KOREAN: "모델",
        ENGLISH: "Model"
    },
    "history_count": {
        KOREAN: "토큰 수",
        ENGLISH: "Token Count"
    },

    # 언어 선택
    "language_setting": {
        KOREAN: "언어 설정",
        ENGLISH: "Language Setting"
    },
    "korean": {
        KOREAN: "English",
        ENGLISH: "Korean"
    },
    "english": {
        KOREAN: "Korean",
        ENGLISH: "English"
    },
    
    # 로그 메시지
    "commercial_token_mode": {
        KOREAN: "상용 모델 '{}' 토큰 계산 모드",
        ENGLISH: "Commercial model '{}' token calculation mode"
    },
    "processing_file": {
        KOREAN: "파일 처리 중...",
        ENGLISH: "Processing file..."
    },
    "unsupported_file": {
        KOREAN: "지원하지 않는 파일 형식입니다.",
        ENGLISH: "Unsupported file format."
    },
    "file_parsing_complete": {
        KOREAN: "파일 파싱 완료.",
        ENGLISH: "File parsing complete."
    },
    "file_parsing_error": {
        KOREAN: "파일 파싱 에러: {}",
        ENGLISH: "File parsing error: {}"
    },
    "calculating_tokens": {
        KOREAN: "토큰 계산 중...",
        ENGLISH: "Calculating tokens..."
    },
    "unsupported_commercial_model": {
        KOREAN: "지원하지 않는 상용 모델입니다.",
        ENGLISH: "Unsupported commercial model."
    },
    "complete": {
        KOREAN: "완료.",
        ENGLISH: "Complete."
    },
    "loading_tokenizer": {
        KOREAN: "모델 '{}' 토크나이저 로드 중...",
        ENGLISH: "Loading tokenizer for model '{}'..."
    },
    "tokenizer_load_complete": {
        KOREAN: "토크나이저 로드 완료.",
        ENGLISH: "Tokenizer loading complete."
    },
    "tokenizer_load_error": {
        KOREAN: "토크나이저 로드 에러: {}",
        ENGLISH: "Tokenizer loading error: {}"
    },
    "select_model_type": {
        KOREAN: "모델 타입을 선택해주세요.",
        ENGLISH: "Please select a model type."
    },
    "select_input_method": {
        KOREAN: "입력 방식을 선택해주세요.",
        ENGLISH: "Please select an input method."
    },

    # API 키 관련 에러 메시지
    "api_key_missing_anthropic": {
        KOREAN: "Anthropic API 키가 설정되지 않았습니다. .env 파일에 ANTHROPIC_API_KEY를 설정해주세요.",
        ENGLISH: "Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env file."
    },
    "api_key_missing_google": {
        KOREAN: "Google API 키가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY를 설정해주세요.",
        ENGLISH: "Google API key not configured. Please set GOOGLE_API_KEY in .env file."
    },
    "api_key_missing_openai": {
        KOREAN: "OpenAI API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 설정해주세요.",
        ENGLISH: "OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
    },

    # 파일 관련 에러 메시지
    "file_too_large": {
        KOREAN: "파일 크기가 {:.1f}MB입니다. 최대 {}MB까지 지원됩니다.",
        ENGLISH: "File size is {:.1f}MB. Maximum supported size is {}MB."
    },
    "file_not_found": {
        KOREAN: "파일을 찾을 수 없습니다: {}",
        ENGLISH: "File not found: {}"
    },
    "file_upload_required": {
        KOREAN: "파일을 업로드해주세요.",
        ENGLISH: "Please upload a file."
    },

    # 모델 관련 에러 메시지
    "model_name_empty": {
        KOREAN: "모델 이름이 비어있습니다. 모델을 선택하거나 입력해주세요.",
        ENGLISH: "Model name is empty. Please select or enter a model name."
    },
    "model_name_invalid": {
        KOREAN: "잘못된 모델 이름 형식입니다: {}",
        ENGLISH: "Invalid model name format: {}"
    },

    # API별 에러 메시지
    "api_error_anthropic": {
        KOREAN: "Anthropic API 오류: {}",
        ENGLISH: "Anthropic API error: {}"
    },
    "api_error_google": {
        KOREAN: "Google API 오류: {}",
        ENGLISH: "Google API error: {}"
    },
    "api_error_openai": {
        KOREAN: "OpenAI/tiktoken 오류: {}",
        ENGLISH: "OpenAI/tiktoken error: {}"
    },

    # 입력 관련 에러 메시지
    "text_input_empty": {
        KOREAN: "텍스트가 비어있습니다. 텍스트를 입력해주세요.",
        ENGLISH: "Text input is empty. Please enter some text."
    },

    # 새 UI 관련 텍스트
    "quick_start": {
        KOREAN: "**빠른 시작**: 모델 선택 → 텍스트 입력 → 계산 버튼 클릭",
        ENGLISH: "**Quick Start**: Select model → Enter text → Click calculate"
    },
    "tab_commercial": {
        KOREAN: "상용 모델",
        ENGLISH: "Commercial Models"
    },
    "tab_huggingface": {
        KOREAN: "허깅페이스 모델",
        ENGLISH: "HuggingFace Models"
    },
    "tab_text_input": {
        KOREAN: "텍스트 입력",
        ENGLISH: "Text Input"
    },
    "tab_file_upload": {
        KOREAN: "파일 업로드",
        ENGLISH: "File Upload"
    },
    "model_select_label": {
        KOREAN: "모델 선택",
        ENGLISH: "Select Model"
    },
    "model_placeholder_commercial": {
        KOREAN: "모델 선택 또는 직접 입력 (예: gpt-4o, claude-3-5-sonnet)",
        ENGLISH: "Select or type model (e.g., gpt-4o, claude-3-5-sonnet)"
    },
    "model_placeholder_huggingface": {
        KOREAN: "모델 선택 또는 직접 입력 (예: meta-llama/llama-4)",
        ENGLISH: "Select or type model (e.g., meta-llama/llama-4)"
    },
    "text_placeholder": {
        KOREAN: "여기에 텍스트를 붙여넣으세요.\n예: 안녕하세요, 토큰 계산 테스트입니다.",
        ENGLISH: "Paste your text here.\nExample: Hello, this is a token count test."
    },
    "estimated_cost": {
        KOREAN: "예상 비용",
        ENGLISH: "Est. Cost"
    },
    "context_window": {
        KOREAN: "컨텍스트 사용률",
        ENGLISH: "Context Usage"
    },
    "tokens_label": {
        KOREAN: "토큰",
        ENGLISH: "Tokens"
    },
    "recent_history": {
        KOREAN: "최근 기록",
        ENGLISH: "Recent History"
    },
    "cost_unknown": {
        KOREAN: "가격 정보 없음",
        ENGLISH: "Price info N/A"
    },
    "context_unknown": {
        KOREAN: "컨텍스트 정보 없음",
        ENGLISH: "Context info N/A"
    }
}

class LanguageManager:
    """다국어 지원을 위한 언어 관리 클래스"""
    
    def __init__(self, language_code=KOREAN):
        """
        언어 관리자 초기화
        
        Args:
            language_code (str): 언어 코드 (기본값: KOREAN)
        """
        self.language_code = language_code
    
    def set_language(self, language_code):
        """
        사용 언어 설정
        
        Args:
            language_code (str): 언어 코드 (KOREAN 또는 ENGLISH)
        """
        if language_code in [KOREAN, ENGLISH]:
            self.language_code = language_code
    
    def get_text(self, key, format_args=None):
        """
        지정된 키에 해당하는 현재 언어의 텍스트 반환
        
        Args:
            key (str): 텍스트 리소스 키
            format_args: 포맷팅할 인자들 (선택사항)
            
        Returns:
            str: 현재 언어에 해당하는 텍스트
        """
        if key not in TEXT_RESOURCES:
            return key
        
        text = TEXT_RESOURCES[key].get(self.language_code, key)
        
        if format_args is not None:
            if isinstance(format_args, (list, tuple)):
                return text.format(*format_args)
            else:
                return text.format(format_args)
        
        return text

# 기본 언어 관리자 인스턴스 생성
language_manager = LanguageManager() 