from .pdf_parser import parse_pdf as _parse_pdf
from .docx_parser import parse_docx as _parse_docx
from .text_parser import parse_text as _parse_text
import os

_cache = {}

def parse_pdf(path: str) -> str:
    m = os.path.getmtime(path)
    key = (path, m)
    if key in _cache:
        return _cache[key]
    r = _parse_pdf(path)
    _cache[key] = r
    return r

def parse_docx(path: str) -> str:
    m = os.path.getmtime(path)
    key = (path, m)
    if key in _cache:
        return _cache[key]
    r = _parse_docx(path)
    _cache[key] = r
    return r

def parse_text(path: str) -> str:
    m = os.path.getmtime(path)
    key = (path, m)
    if key in _cache:
        return _cache[key]
    r = _parse_text(path)
    _cache[key] = r
    return r 