from dataclasses import dataclass
from pydantic import BaseModel


# class to check if the question/user query is relevant to the Deep Research topic
class UserQuestionGuardRail(BaseModel):
    is_relevant: bool


# Our user profile class to manage user context
@dataclass
class UserProfile:
    name: str
    city: str
    uid: str
