def parse_text(file_path: str) -> str:
    """TXT/MD 파일에서 텍스트를 읽어 반환합니다."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read() 