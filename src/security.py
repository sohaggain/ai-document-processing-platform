"""API key auth and webhook HMAC signing."""
import hashlib
import hmac

from fastapi import Header, HTTPException, status

from src.config import get_settings

settings = get_settings()


def verify_api_key(x_api_key: str = Header(...)) -> None:
    if not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def sign_payload(payload: bytes) -> str:
    return hmac.new(settings.webhook_signing_secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_signature(payload: bytes, signature: str) -> bool:
    expected = sign_payload(payload)
    return hmac.compare_digest(expected, signature)
