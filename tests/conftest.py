"""
pytest 설정 파일 - src 디렉토리를 Python path에 추가
"""
import sys
import os

# src 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
