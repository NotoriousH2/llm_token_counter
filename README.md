# LLM Token Counter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [English Readme (영문 설명서)](readme_eng.md)

**[🚀 (Live Demo Link)](https://notolab.64bit.kr/tokenizer/)**

텍스트를 직접 입력하거나 파일을 업로드하여, 다양한 LLM(대규모 언어 모델)에서의 토큰 수를 계산합니다.

> **v2.0 업데이트**: FastAPI + React 아키텍처로 전환. WebSocket 기반 실시간 모델 동기화, REST API 지원.

![image](https://github.com/user-attachments/assets/587968fc-612b-4268-9683-d2c16889f42b)


## 개요

이 도구는 주어진 텍스트나 문서 파일이 여러 LLM에서 몇 개의 토큰으로 처리되는지 계산하는 간단한 웹 인터페이스를 제공합니다. 토큰 수를 이해하는 것은 API 비용 예측, 컨텍스트 창(Context Window) 제한 관리, 프롬프트 최적화 등에 매우 중요합니다.

## 주요 기능

* **다양한 모델 지원**: 다음 모델들의 토큰 수를 계산할 수 있습니다:
    * **상용 모델**: GPT 시리즈 (OpenAI), Claude 시리즈 (Anthropic), Gemini 시리즈 (Google) 등.
    * **허깅페이스 모델**: 허깅페이스 허브(Hugging Face Hub)에서 제공하는 모든 토크나이저.
* **유연한 입력 방식**:
    * 인터페이스에 직접 텍스트 붙여넣기.
    * 파일 업로드 (`.pdf`, `.docx`, `.txt`, `.md`).
* **쉬운 모델 선택**:
    * 드롭다운에서 모델 선택 또는 직접 입력 가능 (검색 및 커스텀 입력 지원).
    * 새로 사용한 모델은 자동으로 목록에 추가됨.
* **비용 및 컨텍스트 정보**: 토큰 수와 함께 예상 비용($)과 컨텍스트 윈도우 사용률(%) 표시.
* **직관적인 탭 기반 UI**: 모델 유형(상용/허깅페이스)과 입력 방식(텍스트/파일)을 탭으로 구분하여 간편하게 사용.
* **계산 기록**: 최근 토큰 수 계산 기록 확인 가능.
* **다국어 지원**: 인터페이스 언어를 한국어와 영어로 전환 가능.
* **캐싱**: 로드된 허깅페이스 토크나이저와 파싱된 파일 내용을 효율적으로 캐싱하여 재사용 시 속도 향상.

## 토크나이저란 무엇입니까?

토크나이저(Tokenizer)는 우리가 사용하는 자연어 텍스트(예: "Hello, World!")를 LLM이 이해할 수 있는 작은 단위인 **토큰(Token)**으로 분리하는 도구입니다. 토큰은 단어, 단어의 일부(subword), 구두점 등이 될 수 있습니다.

예를 들어, "tokenizer is important"라는 문장은 모델에 따라 다음과 같이 토큰화될 수 있습니다:
`["token", "izer", " is", " important"]`

모델마다 사용하는 토크나이저가 다르기 때문에, 같은 텍스트라도 모델별로 토큰의 수나 형태가 달라질 수 있습니다.


특히, 비영어권 데이터의 경우, 모델에 따라 토큰 수가 매우 다르게 나타나기도 합니다.

![image](https://github.com/user-attachments/assets/21cc8ace-2ccd-4109-afbe-e954c82eaaf9)

## 토크나이저가 왜 중요합니까?

토크나이저는 LLM 생태계에서 여러 가지 중요한 역할을 합니다:

1.  **모델 입력 처리**: LLM은 텍스트를 직접 이해하는 것이 아니라, 텍스트를 숫자 시퀀스(토큰 ID)로 변환하여 입력으로 받습니다. 토크나이저는 이 변환 과정의 첫 단계를 담당합니다.
2.  **성능 및 효율성**: 텍스트를 어떻게 토큰으로 나누느냐에 따라 모델의 학습 효율성과 성능이 달라질 수 있습니다. 효율적인 토크나이저는 더 적은 토큰으로 많은 정보를 표현하여 계산 비용을 절감할 수 있습니다.
3.  **비용 및 컨텍스트 길이 제한**:
    * **비용**: 대부분의 LLM API는 처리된 토큰 수(입력 및 출력 모두)를 기준으로 비용을 청구합니다.
    * **컨텍스트 창**: 모델은 한 번에 처리할 수 있는 최대 토큰 수(Context Window)에 제한이 있습니다.
    * 토큰 수를 아는 것은 비용을 정확하게 예측하고 입력이 모델의 제한 내에 맞는지 확인하는 데 도움이 됩니다.

이 `llm_token_counter` 프로젝트는 다양한 모델의 토크나이저를 사용하여 입력 텍스트의 토큰 수를 쉽게 계산해주므로, 사용자는 비용을 예측하고 모델의 컨텍스트 제한 내에서 효율적으로 작업을 계획할 수 있습니다.

## 설치 및 설정

1.  **저장소 복제(Clone):**
    ```bash
    git clone [https://github.com/NotoriousH2/llm-token-counter.git](https://github.com/NotoriousH2/llm-token-counter.git) # YourUsername을 실제 사용자명으로 변경하세요
    cd llm-token-counter
    ```

2.  **가상 환경 생성 (권장):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows에서는 `venv\Scripts\activate` 사용
    ```

3.  **필요한 라이브러리 설치:**
   
    ```bash
    pip install -r requirements.txt
    ```

4.  **API 키 설정 (권장):**
    * 프로젝트 루트 디렉토리에 `.env` 라는 이름의 파일을 생성합니다.
    * 사용하려는 서비스의 API 키를 추가합니다:
        ```dotenv
        # .env 파일 내용
        OPENAI_API_KEY="your_openai_api_key"
        GOOGLE_API_KEY="your_google_api_key"
        ANTHROPIC_API_KEY="your_anthropic_api_key"
        HUGGINGFACE_HUB_TOKEN="your_huggingface_read_token" # 비공개/제한된 HF 모델 접근 시 필요
        ```
    * 이 키들은 해당 상용 모델의 토큰 수를 계산하고, 허깅페이스 허브의 비공개/제한된 모델에 접근하는 데 사용됩니다.

## 사용 방법

### v2.0 (FastAPI + React) - 권장

1.  **프론트엔드 빌드** (최초 1회):
    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

2.  **서버 실행:**
    ```bash
    PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 7860
    ```

3.  **인터페이스 접속:**
    * 웹 브라우저를 열고 `http://127.0.0.1:7860` 또는 `http://0.0.0.0:7860`로 접속합니다.

4.  **API 문서:**
    * Swagger UI: `http://localhost:7860/tokenizer/api/docs`
    * ReDoc: `http://localhost:7860/tokenizer/api/redoc`

### v1.0 (Gradio) - 레거시

1.  **서버 실행:**
    ```bash
    python src/server.py
    ```

2.  **인터페이스 접속:**
    * 웹 브라우저를 열고 터미널에 표시된 URL(보통 `http://127.0.0.1:7860` 또는 `http://0.0.0.0:7860`)로 접속합니다.

3.  **토큰 수 계산:**
    * **모델 유형 탭** (상용 모델 또는 허깅페이스 모델)을 선택합니다.
    * **모델 선택**: 드롭다운에서 모델을 선택하거나, 직접 모델 ID를 입력합니다 (검색 가능).
    * **입력 방식 탭** (텍스트 입력 또는 파일 업로드)을 선택합니다.
        * "텍스트 입력" 탭: 텍스트 상자에 텍스트를 붙여넣습니다.
        * "파일 업로드" 탭: `.pdf`, `.docx`, `.txt`, 또는 `.md` 파일을 업로드합니다.
    * **토큰 수 계산하기** 버튼을 클릭합니다.
    * 결과 섹션에서 **토큰 수**, **예상 비용**, **컨텍스트 사용률**을 확인합니다.
    * 계산 결과는 최근 기록 테이블에도 추가됩니다.

## 지원 모델

* **상용 모델**: OpenAI(GPT 시리즈), Anthropic(Claude 시리즈), Google(Gemini 시리즈)의 일반적인 모델들을 지원합니다. 각 토큰 계산 라이브러리(`tiktoken`, `anthropic`, `genai`)에서 인식하는 모델 ID를 직접 입력하여 다른 모델도 추가할 수 있습니다. 새로 사용된 모델은 드롭다운 목록에 추가됩니다.
* **허깅페이스 모델**: 허깅페이스 허브에서 사용 가능한 모든 모델 식별자(예: `meta-llama/Llama-2-7b-chat-hf`)를 지원합니다. 처음 사용할 때는 토크나이저 다운로드를 위해 인터넷 연결이 필요합니다. 비공개 또는 접근 제한(gated) 모델의 경우 `.env` 파일에 `HUGGINGFACE_HUB_TOKEN` 설정이 필요할 수 있습니다. 새로 사용된 모델은 드롭다운 목록에 추가됩니다.
* 모델 목록은 `src/utils/models.json` 파일에서 관리되며, 사용 시 자동으로 업데이트됩니다.

## 지원 파일 형식

* PDF (`.pdf`)
* 워드 문서 (`.docx`)
* 텍스트 파일 (`.txt`)
* 마크다운 파일 (`.md`)

## 설정

설정 옵션은 환경 변수 또는 `.env` 파일을 통해 관리할 수 있습니다. 주요 설정은 다음과 같습니다:

* `ANTHROPIC_API_KEY`: Anthropic API 키.
* `OPENAI_API_KEY`: OpenAI API 키.
* `GOOGLE_API_KEY`: Google API 키.
* `HUGGINGFACE_HUB_TOKEN`: 허깅페이스 허브 토큰 (보통 읽기 권한이면 충분).
* `CACHE_DIR`: 허깅페이스 모델/토크나이저 캐시 디렉토리 (기본값: `~/.cache/huggingface`).
* `PORT`: Gradio 서버 실행 포트 (기본값: `7860`).
* `HOST`: 서버 호스트 주소 (기본값: `0.0.0.0`).
* `LANGUAGE`: 기본 인터페이스 언어 (`kor` 또는 `eng`, 기본값: `kor`).

자세한 내용은 `src/utils/config.py` 파일을 참조하세요.

## 다국어 지원

사용자 인터페이스는 한국어와 영어를 모두 지원합니다. 애플리케이션 우측 상단의 버튼을 사용하여 언어를 전환할 수 있습니다.

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다. ```

**참고:**

1.  `https://github.com/YourUsername/llm-token-counter.git` 부분을 실제 깃허브 저장소 주소로 변경해주세요.
2.  `requirements.txt` 파일을 프로젝트 루트에 생성하고 필요한 모든 파이썬 패키지 목록을 포함시켜야 합니다.
3.  MIT 라이선스 외 다른 라이선스를 선택했다면, 해당 라이선스 정보로 수정하고 `LICENSE` 파일을 프로젝트 루트에 추가해주세요.

이제 이 내용을 `README.md` 파일로 저장하시면 됩니다.
