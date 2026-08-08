"""Unit tests for webhook signature signing/verification."""
from src.security import sign_payload, verify_signature


def test_signature_roundtrip():
    payload = b'{"document_id": "abc123"}'
    sig = sign_payload(payload)
    assert verify_signature(payload, sig) is True


def test_signature_detects_tampering():
    payload = b'{"document_id": "abc123"}'
    sig = sign_payload(payload)
    tampered = b'{"document_id": "hacked"}'
    assert verify_signature(tampered, sig) is False
