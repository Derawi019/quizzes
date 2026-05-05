from pydantic import BaseModel
from typing import List, Optional


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    points: int
    total_correct: int
    accuracy_percentage: float


class LeaderboardResponse(BaseModel):
    timeframe: str
    competition: str
    rankings: List[LeaderboardEntry]
    my_position: Optional[dict] = None