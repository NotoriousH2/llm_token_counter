"""Tests for /api/models endpoints"""
import pytest


class TestGetModels:
    """Tests for GET /api/models"""

    def test_get_models_success(self, client):
        """Test getting model list"""
        response = client.get("/api/models")

        assert response.status_code == 200
        data = response.json()

        assert "official" in data
        assert "custom" in data
        assert "version" in data

        assert isinstance(data["official"], list)
        assert isinstance(data["custom"], list)
        assert isinstance(data["version"], int)

    def test_get_models_contains_default_models(self, client):
        """Test that default models are present"""
        response = client.get("/api/models")
        data = response.json()

        # Should have some models
        assert len(data["official"]) > 0 or len(data["custom"]) > 0


class TestAddModel:
    """Tests for POST /api/models"""

    def test_add_official_model(self, client):
        """Test adding an official model"""
        response = client.post(
            "/api/models",
            json={"name": "test-model-official", "type": "official"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "test-model-official" in data["official"]

    def test_add_custom_model(self, client):
        """Test adding a custom model"""
        response = client.post(
            "/api/models",
            json={"name": "test-org/test-model", "type": "custom"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "test-org/test-model" in data["custom"]

    def test_add_model_normalizes_name(self, client):
        """Test that model names are normalized to lowercase"""
        response = client.post(
            "/api/models",
            json={"name": "TEST-MODEL-UPPER", "type": "official"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "test-model-upper" in data["official"]

    def test_add_model_invalid_type(self, client):
        """Test adding model with invalid type"""
        response = client.post(
            "/api/models",
            json={"name": "test-model", "type": "invalid"}
        )

        assert response.status_code == 422


class TestPricing:
    """Tests for GET /api/pricing/{model_name}"""

    def test_get_pricing_known_model(self, client):
        """Test getting pricing for known model"""
        response = client.get("/api/pricing/gpt-4o")

        assert response.status_code == 200
        data = response.json()

        assert data["model"] == "gpt-4o"
        assert data["input_price"] is not None
        assert data["context_window"] is not None

    def test_get_pricing_unknown_model(self, client):
        """Test getting pricing for unknown model"""
        response = client.get("/api/pricing/unknown-model-xyz")

        assert response.status_code == 200
        data = response.json()

        assert data["model"] == "unknown-model-xyz"
        assert data["input_price"] is None
        assert data["context_window"] is None

    def test_get_pricing_partial_match(self, client):
        """Test partial matching for model variants"""
        response = client.get("/api/pricing/claude-3-5-sonnet-20241022")

        assert response.status_code == 200
        data = response.json()

        # Should match claude-3-5-sonnet
        assert data["input_price"] is not None
