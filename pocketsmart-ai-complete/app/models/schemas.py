from pydantic import BaseModel, Field

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    room_type: str = Field(min_length=2, max_length=80)
    style: str = Field(default="modern", max_length=80)
    lights: int = Field(default=2, ge=0, le=100)
    fans: int = Field(default=1, ge=0, le=50)
    tables: int = Field(default=1, ge=0, le=20)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=10000)
    event_type: str = Field(min_length=2, max_length=80)
    venue_type: str = Field(default="indoor", max_length=80)
    city: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=1000)

class RecommendationItem(BaseModel):
    name: str
    category: str
    estimated_price: float
    platform: str
    reason: str
    search_url: str = ""

class RecommendationResponse(BaseModel):
    planner: str
    budget: float
    estimated_total: float
    summary: str
    items: list[RecommendationItem]
    tips: list[str] = []
    source: str = "fallback"
