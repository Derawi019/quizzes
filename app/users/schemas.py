from pydantic import BaseModel
from typing import Optional

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    favorite_club_id: Optional[str] = None

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    favorite_club_id: Optional[str] = None

class UserScoresResponse(BaseModel):
    total_points: int = 0
    total_answered: int = 0
    total_correct: int = 0
    weekly_points: int = 0
    current_streak: int = 0
    best_streak: int = 0
    accuracy_percentage: float = 0.0