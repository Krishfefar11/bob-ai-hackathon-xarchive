"""Request/response models — these field descriptions become the tool schema watsonx Orchestrate shows its agent."""
from pydantic import BaseModel, Field


class SignalDetectRequest(BaseModel):
    drug_name: str = Field(..., description="Drug name to search for on OpenFDA, e.g. 'ASPIRIN'")
    n_records: int = Field(1000, ge=100, le=25000, description="Number of OpenFDA adverse event reports to fetch")
    use_llm: bool = Field(False, description="Generate plain-language explanations via watsonx.ai")


class Signal(BaseModel):
    drug: str
    reaction: str
    reports: int = Field(..., description="Number of co-occurring reports (Evans 'a' count)")
    prr: float = Field(..., description="Proportional Reporting Ratio")
    chi2: float = Field(..., description="Chi-squared statistic")
    risk_level: str
    explanation: str


class SignalDetectResponse(BaseModel):
    drug_name: str
    reports_fetched: int = Field(..., description="Distinct OpenFDA reports fetched for this drug")
    signals: list[Signal] = Field(..., description="Drug-event pairs meeting PRR>=2, chi2>=4, n>=3")


class ModuleCompleteness(BaseModel):
    title: str
    completeness_pct: float
    present_count: int
    total_count: int


class SubmissionCheckResponse(BaseModel):
    completeness_pct: float
    present_count: int
    total_count: int
    missing_sections: list[str] = Field(..., description="CTD sections not detected in the uploaded document")
    modules: dict[str, ModuleCompleteness] = Field(..., description="Completeness score broken down per CTD module")
