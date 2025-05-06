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