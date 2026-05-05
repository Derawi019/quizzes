from pydantic import BaseModel
from typing import Optional, List


class MCQOption(BaseModel):
    id: str
    option_text: str
    is_correct: bool


class QuestionResponse(BaseModel):
    id: str
    competition: str
    season: Optional[str] = None
    matchweek: Optional[int] = None
    question_type: str
    difficulty: str
    question_text: str
    hint_1: Optional[str] = None
    hint_2: Optional[str] = None
    hint_3: Optional[str] = None
    hint_4: Optional[str] = None
    player_id: Optional[str] = None


class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int