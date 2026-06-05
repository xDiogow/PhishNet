"""NoSQL (Redis) repository for JWT session management and token revocation."""
import redis
from flask import current_app


class SessionRepository:
    """Stores revoked JWT JTIs in Redis with a TTL equal to the token's remaining lifetime."""

    def _client(self):
        url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        return redis.from_url(url, decode_responses=True, socket_connect_timeout=2)

    def revoke_token(self, jti: str, expires_in: int) -> None:
        """Mark a token as revoked by writing its JTI to Redis with a TTL."""
        self._client().setex(f"blocklist:{jti}", expires_in, "1")

    def is_token_revoked(self, jti: str) -> bool:
        """Return True if the JTI is present in the blocklist."""
        try:
            return self._client().exists(f"blocklist:{jti}") > 0
        except redis.exceptions.ConnectionError:
            current_app.logger.warning("Redis unavailable; token treated as not revoked")
            return False


session_repo = SessionRepository()
