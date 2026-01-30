"""Tests for WebSocket endpoint"""
import pytest
from fastapi.testclient import TestClient


class TestWebSocket:
    """Tests for /api/ws WebSocket endpoint"""

    def test_websocket_connect_and_init(self, client):
        """Test WebSocket connection and initial message"""
        with client.websocket_connect("/api/ws") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "init"
            assert "data" in data
            assert "official" in data["data"]
            assert "custom" in data["data"]
            assert "version" in data["data"]

    def test_websocket_add_model(self, client):
        """Test adding model via WebSocket"""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive init message
            init_data = websocket.receive_json()
            assert init_data["type"] == "init"

            # Send add_model message
            websocket.send_json({
                "type": "add_model",
                "name": "ws-test-model",
                "category": "custom"
            })

            # Should receive model_added message
            response = websocket.receive_json()
            assert response["type"] == "model_added"
            assert "ws-test-model" in response["data"]["custom"]

    def test_websocket_add_model_invalid_name(self, client):
        """Test adding model with invalid name"""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive init message
            websocket.receive_json()

            # Send add_model with empty name
            websocket.send_json({
                "type": "add_model",
                "name": "",
                "category": "custom"
            })

            # Should receive error
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "error" in response

    def test_websocket_add_official_model(self, client):
        """Test adding official model via WebSocket"""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive init message
            websocket.receive_json()

            # Send add_model for official category
            websocket.send_json({
                "type": "add_model",
                "name": "ws-official-test",
                "category": "official"
            })

            # Should receive model_added message
            response = websocket.receive_json()
            assert response["type"] == "model_added"
            assert "ws-official-test" in response["data"]["official"]

    def test_websocket_multiple_connections(self, client):
        """Test multiple WebSocket connections receive updates"""
        with client.websocket_connect("/api/ws") as ws1:
            with client.websocket_connect("/api/ws") as ws2:
                # Both receive init
                ws1.receive_json()
                ws2.receive_json()

                # ws1 adds a model
                model_name = "multi-conn-test-model"
                ws1.send_json({
                    "type": "add_model",
                    "name": model_name,
                    "category": "custom"
                })

                # ws1 receives update
                response1 = ws1.receive_json()
                assert response1["type"] == "model_added"
                assert model_name in response1["data"]["custom"]

                # ws2 should also receive the broadcast
                response2 = ws2.receive_json()
                assert response2["type"] == "model_added"
                assert model_name in response2["data"]["custom"]
