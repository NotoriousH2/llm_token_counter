"""
File parsing service - unified interface for parsing uploaded files
"""
import os
from typing import BinaryIO
import tempfile

from api.config import SETTINGS
from parsers import parse_pdf, parse_docx, parse_text


class FileTooLargeError(Exception):
    """Raised when file exceeds maximum size"""
    pass


class UnsupportedFileTypeError(Exception):
    """Raised when file type is not supported"""
    pass


SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}


def validate_file_size(file_size: int) -> None:
    """
    Validate file size

    Args:
        file_size: File size in bytes

    Raises:
        FileTooLargeError: If file exceeds maximum size
    """
    max_size = SETTINGS.get_max_file_size_bytes()
    if file_size > max_size:
        file_size_mb = file_size / (1024 * 1024)
        raise FileTooLargeError(
            f"File size is {file_size_mb:.1f}MB. Maximum supported size is {SETTINGS.max_file_size_mb}MB."
        )


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension and return it

    Args:
        filename: Original filename

    Returns:
        File extension (lowercase)

    Raises:
        UnsupportedFileTypeError: If file type is not supported
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {ext}. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return ext


def parse_file(file_path: str, extension: str) -> str:
    """
    Parse file content based on extension

    Args:
        file_path: Path to the file
        extension: File extension (lowercase with dot)

    Returns:
        Extracted text content
    """
    if extension == ".pdf":
        return parse_pdf(file_path)
    elif extension == ".docx":
        return parse_docx(file_path)
    elif extension in [".txt", ".md"]:
        return parse_text(file_path)
    else:
        raise UnsupportedFileTypeError(f"Unsupported file type: {extension}")


async def parse_uploaded_file(file: BinaryIO, filename: str) -> str:
    """
    Parse an uploaded file

    Args:
        file: File-like object with file content
        filename: Original filename

    Returns:
        Extracted text content

    Raises:
        FileTooLargeError: If file is too large
        UnsupportedFileTypeError: If file type is not supported
    """
    # Validate extension first
    ext = validate_file_extension(filename)

    # Read file content
    content = file.read()

    # Validate size
    validate_file_size(len(content))

    # Write to temp file and parse
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return parse_file(tmp_path, ext)
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def get_supported_extensions() -> list[str]:
    """Get list of supported file extensions"""
    return list(SUPPORTED_EXTENSIONS)
