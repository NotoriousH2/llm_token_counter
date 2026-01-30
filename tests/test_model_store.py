"""
model_store.py 테스트 - HuggingFace 모델 저장 검증
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch

from api.services import model_store as api_model_store


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


class TestModelStoreUsageCount:
    """usage_count 기능 테스트"""

    @pytest.fixture
    def temp_model_store(self):
        """테스트용 임시 모델 저장소 생성 (구 형식)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Old format with string arrays
            initial_data = {
                "official": ["gpt-4o", "claude-3-7-sonnet"],
                "custom": ["microsoft/phi-4", "qwen/qwen3-8b"]
            }
            json.dump(initial_data, f)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)
        tmp_path = temp_path + '.tmp'
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    @pytest.fixture
    def temp_model_store_new_format(self):
        """테스트용 임시 모델 저장소 생성 (신 형식)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # New format with objects
            initial_data = {
                "official": [
                    {"name": "gpt-4o", "usage_count": 5},
                    {"name": "claude-3-7-sonnet", "usage_count": 3}
                ],
                "custom": [
                    {"name": "microsoft/phi-4", "usage_count": 10},
                    {"name": "qwen/qwen3-8b", "usage_count": 2}
                ]
            }
            json.dump(initial_data, f)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)
        tmp_path = temp_path + '.tmp'
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    def test_migrate_string_array_to_object(self, temp_model_store):
        """구 형식에서 신 형식으로 마이그레이션"""
        with patch('api.services.model_store.MODEL_STORE_PATH', temp_model_store):
            api_model_store.invalidate_cache()

            # Load triggers migration
            api_model_store.get_custom_models()

            # Check file has new format
            with open(temp_model_store, 'r') as f:
                data = json.load(f)

            # Should be objects with usage_count
            assert isinstance(data['official'][0], dict)
            assert 'name' in data['official'][0]
            assert 'usage_count' in data['official'][0]
            assert data['official'][0]['usage_count'] == 0

    def test_add_existing_model_increments_usage(self, temp_model_store_new_format):
        """이미 존재하는 모델 추가 시 usage_count 증가"""
        with patch('api.services.model_store.MODEL_STORE_PATH', temp_model_store_new_format):
            api_model_store.invalidate_cache()

            # Get initial usage count
            with open(temp_model_store_new_format, 'r') as f:
                initial_data = json.load(f)

            initial_count = next(
                m['usage_count'] for m in initial_data['custom']
                if m['name'] == 'microsoft/phi-4'
            )

            # Add existing model
            result = api_model_store.add_custom_model("microsoft/phi-4")
            assert result is False  # Not a new model

            # Check usage_count increased
            with open(temp_model_store_new_format, 'r') as f:
                updated_data = json.load(f)

            updated_count = next(
                m['usage_count'] for m in updated_data['custom']
                if m['name'] == 'microsoft/phi-4'
            )
            assert updated_count == initial_count + 1

    def test_get_custom_models_sorted_by_usage(self, temp_model_store_new_format):
        """custom 모델이 usage_count 내림차순 정렬"""
        with patch('api.services.model_store.MODEL_STORE_PATH', temp_model_store_new_format):
            api_model_store.invalidate_cache()

            # microsoft/phi-4 has 10, qwen/qwen3-8b has 2
            custom_models = api_model_store.get_custom_models()

            # Should be sorted by usage_count descending
            assert custom_models[0] == "microsoft/phi-4"
            assert custom_models[1] == "qwen/qwen3-8b"

    def test_get_custom_models_limited_to_20(self):
        """custom 모델이 최대 20개로 제한"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Create 30 custom models
            custom = [{"name": f"org/model-{i}", "usage_count": 30 - i} for i in range(30)]
            initial_data = {"official": [], "custom": custom}
            json.dump(initial_data, f)
            temp_path = f.name

        try:
            with patch('api.services.model_store.MODEL_STORE_PATH', temp_path):
                api_model_store.invalidate_cache()

                custom_models = api_model_store.get_custom_models()
                assert len(custom_models) == 20

                # Should be top 20 by usage_count
                assert custom_models[0] == "org/model-0"  # usage_count 30
                assert custom_models[19] == "org/model-19"  # usage_count 11
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            tmp_path = temp_path + '.tmp'
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_new_model_starts_with_usage_count_1(self, temp_model_store_new_format):
        """새 모델 추가 시 usage_count=1"""
        with patch('api.services.model_store.MODEL_STORE_PATH', temp_model_store_new_format):
            api_model_store.invalidate_cache()

            # Add new model
            new_model = "deepseek-ai/deepseek-v3"
            result = api_model_store.add_custom_model(new_model)
            assert result is True  # Is a new model

            # Check usage_count is 1
            with open(temp_model_store_new_format, 'r') as f:
                data = json.load(f)

            new_entry = next(
                m for m in data['custom']
                if m['name'] == new_model
            )
            assert new_entry['usage_count'] == 1
