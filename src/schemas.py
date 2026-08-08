"""
Pydantic schemas: API request/response models AND per-document-type
structured extraction schemas. LLM output is always re-validated against
these before it is trusted or persisted.
"""

from pydantic import BaseModel, Field, field_validator

# ---------- API models ----------

class DocumentResponse(BaseModel):
    id: str
    filename: str
    document_type: str
    status: str
    classification_confidence: float | None = None
    created_at: str


class ExtractionResponse(BaseModel):
    id: str
    document_id: str
    document_type: str
    extracted_data: dict
    confidence: float
    is_valid: bool
    validation_errors: dict | None = None


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


# ---------- Classification ----------

class ClassificationResult(BaseModel):
    document_type: str = Field(description="One of: invoice, contract, resume, form, unknown")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""

    @field_validator("document_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        allowed = {"invoice", "contract", "resume", "form", "unknown"}
        if v not in allowed:
            return "unknown"
        return v


# ---------- Per-type extraction schemas ----------

class LineItem(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    total: float | None = None


class InvoiceData(BaseModel):
    invoice_number: str | None = None
    vendor_name: str | None = None
    customer_name: str | None = None
    issue_date: str | None = None
    due_date: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total_amount: float | None = None
    line_items: list[LineItem] = Field(default_factory=list)


class ContractData(BaseModel):
    contract_title: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    effective_date: str | None = None
    expiration_date: str | None = None
    contract_value: float | None = None
    currency: str | None = None
    key_terms: list[str] = Field(default_factory=list)
    governing_law: str | None = None


class ResumeData(BaseModel):
    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None
    years_experience: float | None = None
    skills: list[str] = Field(default_factory=list)
    most_recent_title: str | None = None
    most_recent_employer: str | None = None
    education: list[str] = Field(default_factory=list)


class FormField(BaseModel):
    label: str
    value: str


class FormData(BaseModel):
    form_title: str | None = None
    submitted_by: str | None = None
    submission_date: str | None = None
    fields: list[FormField] = Field(default_factory=list)


EXTRACTION_SCHEMAS: dict[str, type[BaseModel]] = {
    "invoice": InvoiceData,
    "contract": ContractData,
    "resume": ResumeData,
    "form": FormData,
}
