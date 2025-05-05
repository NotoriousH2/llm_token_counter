from docx import Document

def parse_docx(file_path: str) -> str:
    """DOCX 파일의 모든 단락에서 텍스트를 추출하여 반환합니다."""
    doc = Document(file_path)
    texts = [para.text for para in doc.paragraphs]
    return "\n".join(texts) 