from pydantic import BaseModel
from typing import List, Optional


class BracketTie(BaseModel):
    id: str
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    score_home: Optional[int] = None
    score_away: Optional[int] = None
    winner: Optional[str] = None
    is_blank: bool = False


class BracketRound(BaseModel):
    round_name: str
    round_order: int
    ties: List[BracketTie]


class BracketResponse(BaseModel):
    competition: str
    year: str
    difficulty: str
    rounds: List[BracketRound]
    total_blanks: int


class TournamentListItem(BaseModel):
    competition: str
    year: str
    winner: Optional[str] = None