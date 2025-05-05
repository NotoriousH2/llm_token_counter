import pdfplumber

def parse_pdf(file_path: str) -> str:
    """PDF 파일의 모든 페이지에서 텍스트를 추출하여 반환합니다."""
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text) 