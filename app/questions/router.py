from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.database import supabase
from app.auth.utils import get_current_user
from app.questions.schemas import QuestionResponse, QuestionListResponse

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=QuestionListResponse)
def get_questions(
    competition: Optional[str] = Query(None, description="PL, UCL or WC"),
    question_type: Optional[str] = Query(None, description="mcq, card_flip, top10, lineup, bracket"),
    difficulty: Optional[str] = Query(None, description="easy, medium, hard, extreme"),
    season: Optional[str] = Query(None, description="e.g. 2024/25 or historical"),
    limit: int = Query(10, description="Number of questions to return"),
    current_user: dict = Depends(get_current_user)
):
    query = supabase.table("questions")\
        .select("*")\
        .eq("is_active", True)

    if competition:
        query = query.eq("competition", competition)
    if question_type:
        query = query.eq("question_type", question_type)
    if difficulty:
        query = query.eq("difficulty", difficulty)
    if season:
        query = query.eq("season", season)

    query = query.limit(limit)
    result = query.execute()

    return {
        "questions": result.data,
        "total": len(result.data)
    }


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = supabase.table("questions")\
        .select("*")\
        .eq("id", question_id)\
        .eq("is_active", True)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Question not found")

    return result.data[0]


@router.get("/{question_id}/options")
def get_mcq_options(
    question_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Verify question exists and is MCQ type
    question = supabase.table("questions")\
        .select("question_type")\
        .eq("id", question_id)\
        .execute()

    if not question.data:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.data[0]["question_type"] != "mcq":
        raise HTTPException(status_code=400, detail="This question is not MCQ type")

    options = supabase.table("mcq_options")\
        .select("id, option_text")\
        .eq("question_id", question_id)\
        .execute()

    return {"options": options.data}


@router.get("/{question_id}/hints")
def get_hints(
    question_id: str,
    level: int = Query(1, description="Hint level 1 to 4"),
    current_user: dict = Depends(get_current_user)
):
    # Verify question exists and is card flip type
    question = supabase.table("questions")\
        .select("question_type, hint_1, hint_2, hint_3, hint_4")\
        .eq("id", question_id)\
        .execute()

    if not question.data:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.data[0]["question_type"] != "card_flip":
        raise HTTPException(status_code=400, detail="This question is not card flip type")

    if level < 1 or level > 4:
        raise HTTPException(status_code=400, detail="Hint level must be between 1 and 4")

    q = question.data[0]
    hints = []
    for i in range(1, level + 1):
        hint = q.get(f"hint_{i}")
        if hint:
            hints.append({"level": i, "text": hint})

    return {"hints": hints}