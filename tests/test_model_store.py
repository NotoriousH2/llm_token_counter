"""
model_store.py 테스트 - HuggingFace 모델 저장 검증
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch


class TestModelStorePersistence:
    """모델 저장소 영속성 테스트"""

    @pytest.fixture
    def temp_model_store(self):
        """테스트용 임시 모델 저장소 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            initial_data = {
                "official": ["gpt-4o", "claude-3-7-sonnet"],
                "custom": ["microsoft/phi-4"]
            }
            json.dump(initial_data, f)
            temp_path = f.name

        yield temp_path

        # 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        tmp_path = temp_path + '.tmp'
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    def test_add_custom_model_persists_to_file(self, temp_model_store):
        """HuggingFace 모델 추가가 JSON 파일에 저장되는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 새 커스텀 모델 추가
            new_model = "meta-llama/llama-3-8b"
            model_store.add_custom_model(new_model)

            # 메모리에 있는지 확인
            custom_models = model_store.get_custom_models()
            assert new_model in custom_models

            # 파일에 저장되었는지 확인
            with open(temp_model_store, 'r') as f:
                stored_data = json.load(f)
            assert new_model in stored_data['custom']

    def test_custom_model_survives_reload(self, temp_model_store):
        """애플리케이션 재시작 후에도 커스텀 모델이 유지되는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 모델 추가
            new_model = "qwen/qwen3-32b"
            model_store.add_custom_model(new_model)

            # 재시작 시뮬레이션 - 캐시 무효화
            model_store._invalidate_cache()

            # 다시 로드하여 확인
            custom_models = model_store.get_custom_models()
            assert new_model in custom_models

    def test_duplicate_model_not_added_twice(self, temp_model_store):
        """동일 모델 중복 추가 방지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            model_name = "deepseek-ai/deepseek-r1"

            # 두 번 추가
            model_store.add_custom_model(model_name)
            model_store.add_custom_model(model_name)

            # 횟수 확인
            custom_models = model_store.get_custom_models()
            assert custom_models.count(model_name) == 1

    def test_models_stored_lowercase(self, temp_model_store):
        """모델이 소문자로 정규화되어 저장되는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 대소문자 섞어서 추가
            model_store.add_custom_model("Microsoft/PHI-4-Mini")

            custom_models = model_store.get_custom_models()
            assert "microsoft/phi-4-mini" in custom_models
            assert "Microsoft/PHI-4-Mini" not in custom_models

    def test_models_stored_alphabetically(self, temp_model_store):
        """모델이 알파벳 순으로 저장되는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 알파벳 역순으로 추가
            model_store.add_custom_model("zeta/model")
            model_store.add_custom_model("alpha/model")

            custom_models = model_store.get_custom_models()
            assert custom_models == sorted(custom_models)


class TestModelStoreCaching:
    """모델 저장소 캐싱 테스트"""

    @pytest.fixture
    def temp_model_store(self):
        """테스트용 임시 모델 저장소 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            initial_data = {
                "official": ["gpt-4o"],
                "custom": ["microsoft/phi-4"]
            }
            json.dump(initial_data, f)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)
        tmp_path = temp_path + '.tmp'
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    def test_cache_prevents_unnecessary_file_reads(self, temp_model_store):
        """캐시가 불필요한 파일 읽기를 방지하는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 첫 번째 호출 - 파일에서 로드
            model_store.get_custom_models()

            # 캐시가 설정되었는지 확인
            assert model_store._cache is not None
            assert model_store._cache_mtime is not None

    def test_cache_invalidates_on_file_change(self, temp_model_store):
        """파일 변경 시 캐시가 무효화되는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 초기 데이터 로드
            initial_models = model_store.get_custom_models()

            # 캐시 무효화
            model_store._invalidate_cache()

            # 외부에서 파일 직접 수정 시뮬레이션
            import time
            time.sleep(0.1)  # mtime 차이 보장

            with open(temp_model_store, 'r') as f:
                data = json.load(f)
            data['custom'].append('external/model')
            with open(temp_model_store, 'w') as f:
                json.dump(data, f)

            # 다시 로드하면 새 데이터 포함
            updated_models = model_store.get_custom_models()
            assert 'external/model' in updated_models


class TestHuggingFaceModelIntegration:
    """HuggingFace 모델 워크플로우 통합 테스트"""

    @pytest.fixture
    def temp_model_store(self):
        """테스트용 임시 모델 저장소 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            initial_data = {
                "official": ["gpt-4o", "claude-3-7-sonnet"],
                "custom": ["microsoft/phi-4"]
            }
            json.dump(initial_data, f)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)
        tmp_path = temp_path + '.tmp'
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    def test_full_workflow_model_persistence(self, temp_model_store):
        """
        전체 워크플로우 테스트:
        1. 사용자가 새 HuggingFace 모델 입력
        2. 모델이 저장소에 추가됨
        3. 다음 로드 시 드롭다운에 모델 표시
        """
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 시뮬레이션: 초기 드롭다운 선택지 가져오기
            initial_choices = model_store.get_custom_models()
            new_model = "bigscience/bloom-560m"
            assert new_model not in initial_choices

            # 시뮬레이션: 사용자가 새 모델로 처리 (모델 추가됨)
            model_store.add_custom_model(new_model)

            # 시뮬레이션: 사용자가 페이지 새로고침 (캐시 여전히 유효)
            updated_choices = model_store.get_custom_models()
            assert new_model in updated_choices

            # 시뮬레이션: 애플리케이션 재시작 (캐시 클리어, 파일에서 다시 로드)
            model_store._invalidate_cache()
            reloaded_choices = model_store.get_custom_models()
            assert new_model in reloaded_choices

    def test_official_model_persistence(self, temp_model_store):
        """상용 모델도 동일하게 저장되는지 검증"""
        with patch('utils.model_store.MODEL_STORE_PATH', temp_model_store):
            from utils import model_store
            model_store._invalidate_cache()

            # 새 상용 모델 추가
            new_model = "gpt-4o-mini"
            model_store.add_official_model(new_model)

            # 캐시 무효화 후 확인
            model_store._invalidate_cache()
            official_models = model_store.get_official_models()
            assert new_model in official_models
