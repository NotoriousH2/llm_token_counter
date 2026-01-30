from functools import lru_cache
import os
from .pdf_parser import parse_pdf as _parse_pdf
from .docx_parser import parse_docx as _parse_docx
from .text_parser import parse_text as _parse_text

# 최대 캐시 크기 설정
MAX_CACHE_SIZE = 100


@lru_cache(maxsize=MAX_CACHE_SIZE)
def _cached_parse(path: str, mtime: float, parser_type: str) -> str:
    """
    통합 캐시 파서 - LRU 캐시로 메모리 사용량 제한

    Args:
        path: 파일 경로
        mtime: 파일 수정 시간 (캐시 무효화용)
        parser_type: 파서 종류 ("pdf", "docx", "text")

    Returns:
        파싱된 텍스트 내용
    """
    if parser_type == "pdf":
        return _parse_pdf(path)
    elif parser_type == "docx":
        return _parse_docx(path)
    elif parser_type == "text":
        return _parse_text(path)
    raise ValueError(f"Unknown parser type: {parser_type}")


def parse_pdf(path: str) -> str:
    """PDF 파일 파싱 (LRU 캐시 적용)"""
    mtime = os.path.getmtime(path)
    return _cached_parse(path, mtime, "pdf")


def parse_docx(path: str) -> str:
    """DOCX 파일 파싱 (LRU 캐시 적용)"""
    mtime = os.path.getmtime(path)
    return _cached_parse(path, mtime, "docx")


def parse_text(path: str) -> str:
    """텍스트/마크다운 파일 파싱 (LRU 캐시 적용)"""
    mtime = os.path.getmtime(path)
    return _cached_parse(path, mtime, "text")


def clear_parser_cache() -> None:
    """파서 캐시 초기화 (테스트용)"""
    _cached_parse.cache_clear()


def get_cache_info():
    """캐시 통계 정보 반환"""
    return _cached_parse.cache_info()
