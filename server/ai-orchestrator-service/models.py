from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

# Define models for request/response validation
class IndustryType(str, Enum):
    ECOMMERCE = "ecommerce"
    PROFESSIONAL_SERVICES = "professional_services"
    PORTFOLIO = "portfolio"
    BLOG = "blog"
    # Add other industry types

class BrandingInfo(BaseModel):
    primary_color: Optional[str] = Field(None, description="Primary brand color in hex format (e.g., #FF5733)")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color in hex format")
    logo_url: Optional[str] = None
    font_family: Optional[str] = None

class ProcessedBusinessInput(BaseModel):
    business_name: str
    industry: str  # Can be an enum if fixed set
    description: str = Field(..., min_length=10)
    target_audience: List[str] = []
    unique_selling_points: List[str] = []
    competitor_urls: List[str] = []

class RagContextResult(BaseModel):
    documentId: str
    content: str
    similarity: float
    source: Optional[str] = None

class OrchestrationInput(BaseModel):
    sessionId: str
    processed_input: Dict[str, Any]
    branding: Optional[Dict[str, Any]] = None
    rag_context: List[RagContextResult] = []
    
    class Config:
        schema_extra = {
            "example": {
                "sessionId": "f7e60c2a-5a5d-4a0e-8ee0-42a9e3b61d15",
                "processed_input": {
                    "business_name": "TechNova Solutions",
                    "industry": "professional_services",
                    "description": "We provide cutting-edge software development services...",
                    "target_audience": ["startups", "enterprise clients"],
                    "unique_selling_points": ["24/7 support", "custom solutions"],
                    "competitor_urls": ["https://competitor1.com", "https://competitor2.com"]
                }
            }
        }

class SectionContent(BaseModel):
    id: str
    title: str
    content: str
    seoScore: Optional[float] = None

class PageContent(BaseModel):
    type: str  # e.g., 'homepage', 'about', 'contact'
    sections: List[SectionContent]

class OrchestrationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OrchestrationOutput(BaseModel):
    sessionId: str
    status: OrchestrationStatus
    progress: float = Field(0.0, ge=0.0, le=1.0)
    website_generation_data: Optional[Dict[str, Any]] = None
    pages: List[PageContent] = []
    error: Optional[str] = None