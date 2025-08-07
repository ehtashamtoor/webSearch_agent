from dataclasses import dataclass

# Our user profile class to manage user context
@dataclass
class UserProfile:
    name: str
    topic: str
    city: str
    uid: str