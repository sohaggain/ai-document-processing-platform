"""Unit tests for confidence scoring and fail-closed validity logic."""
from src.schemas import InvoiceData
from src.services.validation_service import is_valid, score_extraction


def test_score_extraction_all_fields_filled_scores_high():
    model = InvoiceData(
        invoice_number="INV-001",
        vendor_name="Acme Corp",
        customer_name="Beta LLC",
        issue_date="2026-01-01",
        due_date="2026-01-31",
        currency="USD",
        subtotal=100.0,
        tax=10.0,
        total_amount=110.0,
        line_items=[{"description": "Widget", "quantity": 1, "unit_price": 100.0, "total": 100.0}],
    )
    score = score_extraction(model, classification_confidence=0.95)
    assert score > 0.8


def test_score_extraction_mostly_empty_scores_low():
    model = InvoiceData()
    score = score_extraction(model, classification_confidence=0.5)
    assert score < 0.3


def test_is_valid_respects_threshold():
    assert is_valid(0.8, threshold=0.75) is True
    assert is_valid(0.7, threshold=0.75) is False


def test_is_valid_fails_closed_on_boundary():
    # Exactly at threshold should pass; just below should fail-closed.
    assert is_valid(0.75, threshold=0.75) is True
    assert is_valid(0.7499, threshold=0.75) is False
