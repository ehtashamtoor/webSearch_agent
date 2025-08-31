from pydantic import BaseModel
from typing import List, Optional


# For planner agent
class ResearchPlan(BaseModel):
    master_query: str
    refined_queries: List[str]
    research_plan: str
    subtopics: Optional[List[str]] = None
    assumptions: Optional[List[str]] = None


# For websearch agent
class SourceItem(BaseModel):
    url: str
    title: Optional[str]
    domain: Optional[str]
    published_at: Optional[str]
    snippet: Optional[str]
    matched_query: Optional[str]
    score: float
    subtopic: Optional[str]


# for web search agent
class SearchResults(BaseModel):
    master_query: str
    sources: List[SourceItem]
