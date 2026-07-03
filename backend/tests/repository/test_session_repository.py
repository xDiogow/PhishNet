"""Tests for SessionRepository — Redis-backed JWT blocklist. All Redis calls are mocked."""
import pytest
from unittest.mock import patch, MagicMock
import redis

from app.repository.session_repository import SessionRepository


class TestRevokeToken:

    def test_revoke_token_calls_setex(self, app):
        mock_redis = MagicMock()
        with app.app_context():
            with patch('redis.from_url', return_value=mock_redis):
                SessionRepository().revoke_token(jti="abc-123", expires_in=3600)

        mock_redis.setex.assert_called_once_with("blocklist:abc-123", 3600, "1")


class TestIsTokenRevoked:

    def test_is_token_revoked_true(self, app):
        mock_redis = MagicMock()
        mock_redis.exists.return_value = 1
        with app.app_context():
            with patch('redis.from_url', return_value=mock_redis):
                result = SessionRepository().is_token_revoked("abc-123")

        assert result is True
        mock_redis.exists.assert_called_once_with("blocklist:abc-123")

    def test_is_token_revoked_false(self, app):
        mock_redis = MagicMock()
        mock_redis.exists.return_value = 0
        with app.app_context():
            with patch('redis.from_url', return_value=mock_redis):
                result = SessionRepository().is_token_revoked("abc-123")

        assert result is False

    def test_is_token_revoked_redis_down_returns_false(self, app):
        """Graceful degradation: if Redis is unreachable, token is treated as not revoked."""
        mock_redis = MagicMock()
        mock_redis.exists.side_effect = redis.exceptions.ConnectionError("Connection refused")
        with app.app_context():
            with patch('redis.from_url', return_value=mock_redis):
                result = SessionRepository().is_token_revoked("abc-123")

        assert result is False
