from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.auth.utils import get_current_user
from app.database import supabase
from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: dict = Depends(get_current_user)):
    user = supabase.table("users")\
        .select("is_admin")\
        .eq("id", current_user["id"])\
        .execute()

    if not user.data or not user.data[0]["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    return current_user


@router.post("/generate")
def trigger_generation(
    competition: str,
    matchweek: int = None,
    current_user: dict = Depends(require_admin)
):
    # This will call your n8n webhook once it's set up
    # For now returns a placeholder
    return {
        "message": f"Generation triggered for {competition} matchweek {matchweek}",
        "status": "pending"
    }


@router.get("/logs")
def get_generation_logs(
    limit: int = 20,
    current_user: dict = Depends(require_admin)
):
    result = supabase.table("generation_log")\
        .select("*")\
        .order("started_at", desc=True)\
        .limit(limit)\
        .execute()

    return {"logs": result.data}


@router.get("/stats")
def get_stats(current_user: dict = Depends(require_admin)):
    questions = supabase.table("questions")\
        .select("competition, question_type, difficulty, is_active")\
        .execute()

    total = len(questions.data)
    active = len([q for q in questions.data if q["is_active"]])

    by_competition = {}
    for q in questions.data:
        comp = q["competition"]
        by_competition[comp] = by_competition.get(comp, 0) + 1

    by_type = {}
    for q in questions.data:
        qt = q["question_type"]
        by_type[qt] = by_type.get(qt, 0) + 1

    return {
        "total_questions": total,
        "active_questions": active,
        "by_competition": by_competition,
        "by_type": by_type
    }


@router.put("/questions/{question_id}/toggle")
def toggle_question(
    question_id: str,
    current_user: dict = Depends(require_admin)
):
    result = supabase.table("questions")\
        .select("is_active")\
        .eq("id", question_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Question not found")

    current_status = result.data[0]["is_active"]

    supabase.table("questions")\
        .update({"is_active": not current_status})\
        .eq("id", question_id)\
        .execute()

    return {
        "message": f"Question {'deactivated' if current_status else 'activated'} successfully"
    }