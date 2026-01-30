"""Tests for /api/count-tokens endpoints"""
import pytest
import io


class TestCountTokensText:
    """Tests for POST /api/count-tokens"""

    def test_count_tokens_gpt_model(self, client, sample_text):
        """Test counting tokens with GPT model (uses tiktoken, no API key needed)"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_text,
                "model": "gpt-4o",
                "model_type": "commercial"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["token_count"] > 0
        assert data["model"] == "gpt-4o"
        assert data["cost_usd"] is not None
        assert data["context_window"] is not None

    def test_count_tokens_empty_text(self, client):
        """Test with empty text"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": "",
                "model": "gpt-4o",
                "model_type": "commercial"
            }
        )

        # Should fail validation (min_length=1)
        assert response.status_code == 422

    def test_count_tokens_invalid_model_type(self, client, sample_text):
        """Test with invalid model type"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_text,
                "model": "gpt-4o",
                "model_type": "invalid"
            }
        )

        assert response.status_code == 422

    def test_count_tokens_short_model_name(self, client, sample_text):
        """Test with too short model name"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_text,
                "model": "a",
                "model_type": "commercial"
            }
        )

        assert response.status_code == 422

    def test_count_tokens_korean_text(self, client, sample_korean_text):
        """Test with Korean text"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_korean_text,
                "model": "gpt-4o",
                "model_type": "commercial"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["token_count"] > 0

    def test_count_tokens_o1_model(self, client, sample_text):
        """Test counting tokens with o1 model"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_text,
                "model": "o1-mini",
                "model_type": "commercial"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["token_count"] > 0
        assert data["model"] == "o1-mini"

    def test_count_tokens_gpt5_fallback(self, client, sample_text):
        """Test that gpt-5 falls back to gpt-4o tokenizer"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_text,
                "model": "gpt-5",
                "model_type": "commercial"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["token_count"] > 0

    def test_count_tokens_unsupported_commercial(self, client, sample_text):
        """Test with unsupported commercial model"""
        response = client.post(
            "/api/count-tokens",
            json={
                "text": sample_text,
                "model": "unsupported-model",
                "model_type": "commercial"
            }
        )

        assert response.status_code == 400


class TestCountTokensFile:
    """Tests for POST /api/count-tokens/file"""

    def test_count_tokens_txt_file(self, client):
        """Test counting tokens from TXT file"""
        file_content = b"Hello, this is a test file content."
        files = {
            "file": ("test.txt", io.BytesIO(file_content), "text/plain")
        }
        data = {
            "model": "gpt-4o",
            "model_type": "commercial"
        }

        response = client.post(
            "/api/count-tokens/file",
            files=files,
            data=data
        )

        assert response.status_code == 200
        result = response.json()

        assert result["token_count"] > 0

    def test_count_tokens_md_file(self, client):
        """Test counting tokens from MD file"""
        file_content = b"# Test Markdown\n\nThis is a test."
        files = {
            "file": ("test.md", io.BytesIO(file_content), "text/markdown")
        }
        data = {
            "model": "gpt-4o",
            "model_type": "commercial"
        }

        response = client.post(
            "/api/count-tokens/file",
            files=files,
            data=data
        )

        assert response.status_code == 200

    def test_count_tokens_unsupported_file(self, client):
        """Test with unsupported file type"""
        file_content = b"test content"
        files = {
            "file": ("test.xyz", io.BytesIO(file_content), "application/octet-stream")
        }
        data = {
            "model": "gpt-4o",
            "model_type": "commercial"
        }

        response = client.post(
            "/api/count-tokens/file",
            files=files,
            data=data
        )

        assert response.status_code == 415

    def test_count_tokens_invalid_model_type(self, client):
        """Test file upload with invalid model type"""
        file_content = b"Hello, test."
        files = {
            "file": ("test.txt", io.BytesIO(file_content), "text/plain")
        }
        data = {
            "model": "gpt-4o",
            "model_type": "invalid"
        }

        response = client.post(
            "/api/count-tokens/file",
            files=files,
            data=data
        )

        assert response.status_code == 400


class TestHealthCheck:
    """Tests for /api/health endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "version" in data
