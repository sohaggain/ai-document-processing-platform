"""Unit tests for classification/extraction schema validation and coercion."""
import pytest
from pydantic import ValidationError

from src.schemas import EXTRACTION_SCHEMAS, ClassificationResult, InvoiceData


def test_classification_result_valid_type():
    result = ClassificationResult(document_type="invoice", confidence=0.9)
    assert result.document_type == "invoice"


def test_classification_result_invalid_type_coerced_to_unknown():
    result = ClassificationResult(document_type="banana", confidence=0.5)
    assert result.document_type == "unknown"


def test_classification_confidence_out_of_range_rejected():
    with pytest.raises(ValidationError):
        ClassificationResult(document_type="invoice", confidence=1.5)


def test_extraction_schema_registry_has_all_supported_types():
    assert set(EXTRACTION_SCHEMAS.keys()) == {"invoice", "contract", "resume", "form"}


def test_invoice_data_accepts_partial_data():
    # Extraction must tolerate missing fields (null) rather than requiring
    # a fully-populated document -- reflects real-world messy documents.
    invoice = InvoiceData(invoice_number="INV-1")
    assert invoice.vendor_name is None
    assert invoice.line_items == []
