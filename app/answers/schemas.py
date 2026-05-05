from pydantic import BaseModel
from typing import Optional


class AnswerSubmit(BaseModel):
    question_id: str
    answer: str
    time_taken_seconds: Optional[int] = None
    hints_used: Optional[int] = 0


class AnswerResponse(BaseModel):
    correct: bool
    points_earned: int
    correct_answer: str
    message: str