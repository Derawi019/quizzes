from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.auth.utils import get_current_user
from app.answers.schemas import AnswerSubmit, AnswerResponse

router = APIRouter(prefix="/answers", tags=["answers"])

POINTS = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "extreme": 5
}


def _calculate_points(
    difficulty: str,
    is_correct: bool,
    time_taken: int,
    hints_used: int
) -> int:
    if not is_correct:
        return 0

    points = POINTS.get(difficulty, 1)

    # Speed bonus
    if time_taken and time_taken < 5:
        points += 1

    # Hints penalty for card flip
    if hints_used:
        points = max(0, points - (hints_used * 0.5))

    return int(points)


def _update_user_scores(user_id: str, points: int, is_correct: bool):
    result = supabase.table("user_scores")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("competition", "all")\
        .eq("question_type", "all")\
        .execute()

    if not result.data:
        # Create score row if it doesn't exist
        supabase.table("user_scores").insert({
            "user_id": user_id,
            "competition": "all",
            "question_type": "all",
            "total_points": points,
            "total_answered": 1,
            "total_correct": 1 if is_correct else 0,
            "weekly_points": points,
            "current_streak": 1 if is_correct else 0,
            "best_streak": 1 if is_correct else 0,
            "accuracy_percentage": 100.0 if is_correct else 0.0
        }).execute()
        return

    score = result.data[0]
    total_answered = score["total_answered"] + 1
    total_correct = score["total_correct"] + (1 if is_correct else 0)
    current_streak = (score["current_streak"] + 1) if is_correct else 0
    best_streak = max(score["best_streak"], current_streak)
    accuracy = round((total_correct / total_answered) * 100, 2)

    supabase.table("user_scores").update({
        "total_points": score["total_points"] + points,
        "weekly_points": score["weekly_points"] + points,
        "total_answered": total_answered,
        "total_correct": total_correct,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "accuracy_percentage": accuracy
    }).eq("user_id", user_id)\
      .eq("competition", "all")\
      .eq("question_type", "all")\
      .execute()


@router.post("/submit", response_model=AnswerResponse)
def submit_answer(
    data: AnswerSubmit,
    current_user: dict = Depends(get_current_user)
):
    # Get the question
    result = supabase.table("questions")\
        .select("*")\
        .eq("id", data.question_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Question not found")

    question = result.data[0]
    is_correct = data.answer.strip().lower() == question["correct_answer"].strip().lower()
    points = _calculate_points(
        question["difficulty"],
        is_correct,
        data.time_taken_seconds or 999,
        data.hints_used or 0
    )

    # Save the answer
    supabase.table("user_answers").insert({
        "user_id": current_user["id"],
        "question_id": data.question_id,
        "answer_given": data.answer,
        "is_correct": is_correct,
        "time_taken_seconds": data.time_taken_seconds,
        "points_earned": points,
        "hints_used": data.hints_used or 0
    }).execute()

    # Update scores
    _update_user_scores(current_user["id"], points, is_correct)

    return {
        "correct": is_correct,
        "points_earned": points,
        "correct_answer": question["correct_answer"],
        "message": "Correct! Well done!" if is_correct else "Wrong answer, keep trying!"
    }