"""
Pydantic models and schemas for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class Verdict(str, Enum):
    """Review verdict types"""
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    UNCERTAIN = "UNCERTAIN"


class QueryOptions(BaseModel):
    """Optional parameters for query processing"""
    use_cache: bool = True
    timeout: int = 120
    enable_parallel: bool = True
    skip_failed_models: bool = True


class QueryRequest(BaseModel):
    """Request model for /api/query endpoint"""
    query: str = Field(..., min_length=5, max_length=1000, description="User query")
    options: QueryOptions = Field(default_factory=QueryOptions)
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class Citation(BaseModel):
    """Citation information"""
    source: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class Stage1Opinion(BaseModel):
    """Stage-1 model opinion"""
    model_name: str
    answer_text: str
    claims: List[str] = []
    citations: List[Citation] = []
    metadata: Dict[str, Any] = {}


class ParaphrasedClaim(BaseModel):
    """Paraphrased canonical claim"""
    claim_id: str
    original_model: str
    original_text: str
    canonical_text: str
    word_count: int


class ReviewItem(BaseModel):
    """Individual review for a claim"""
    claim_id: str
    verdict: Verdict
    reason: str
    evidence_needed: bool
    confidence: float = Field(ge=0.0, le=1.0)


class ReviewerVerdict(BaseModel):
    """Complete verdict from a reviewer"""
    reviewer_name: str
    reviews: List[ReviewItem]
    metadata: Dict[str, Any] = {}


class AggregationResult(BaseModel):
    """Aggregated review results"""
    total_claims: int
    supported_claims: List[str]
    rejected_claims: List[str]
    disputed_claims: List[str]
    uncertain_claims: List[str]
    consensus_score: float = Field(ge=0.0, le=1.0)
    evidence_needed_count: int


class FinalAnswer(BaseModel):
    """Chairman's final synthesized answer"""
    final_answer: str
    supporting_claims: List[str]
    uncertain_points: List[str]
    rejected_claims: List[str]
    citations: List[Citation] = []
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: Optional[str] = None


class PipelineMetadata(BaseModel):
    """Metadata about pipeline execution"""
    request_id: str
    processing_time: float
    models_used: List[str]
    cache_hit: bool = False
    errors: List[str] = []
    warnings: List[str] = []
    stage_timings: Dict[str, float] = {}


class QueryResponse(BaseModel):
    """Response model for /api/query endpoint"""
    query: str
    stage1_opinions: List[Stage1Opinion]
    paraphrased_claims: List[ParaphrasedClaim]
    reviewer_verdicts: List[ReviewerVerdict]
    aggregation: AggregationResult
    final_answer: FinalAnswer
    metadata: PipelineMetadata


class ModelStatus(BaseModel):
    """Status of a single model"""
    name: str
    status: str  # "online", "offline", "degraded"
    endpoint: Optional[str] = None
    response_time: Optional[float] = None
    last_checked: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for /api/health endpoint"""
    status: str  # "healthy", "degraded", "unhealthy"
    models: Dict[str, str]
    details: Optional[List[ModelStatus]] = None
    timestamp: str
