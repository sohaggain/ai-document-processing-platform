"""
Confidence and validity scoring for extraction results.

Design principle: fail closed. If we are not confident the extraction is
correct, we never write it into the system as if it were verified — we
mark it needs_review and store the raw output for a human to check.
"""
from pydantic import BaseModel


def score_extraction(model: BaseModel, classification_confidence: float) -> float:
    """
    Combines classification confidence with a simple completeness signal
    (fraction of non-null top-level fields) into a single confidence score.
    This is intentionally simple and transparent rather than a black box —
    it can be swapped for a more sophisticated evaluator without touching
    callers.
    """
    data = model.model_dump()
    total_fields = len(data)
    filled_fields = sum(1 for v in data.values() if v not in (None, "", [], {}))
    completeness = filled_fields / total_fields if total_fields else 0.0

    # Weighted blend: classification confidence matters, but completeness
    # of the extracted schema matters more for downstream usability.
    return round((0.4 * classification_confidence) + (0.6 * completeness), 4)


def is_valid(confidence: float, threshold: float) -> bool:
    return confidence >= threshold
