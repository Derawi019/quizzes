from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.database import supabase
from app.auth.utils import get_current_user
from app.leaderboard.schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
def get_leaderboard(
    timeframe: str = Query("weekly", description="weekly or alltime"),
    competition: str = Query("all", description="all, PL, UCL or WC"),
    limit: int = Query(10, description="Number of entries to return"),
    current_user: dict = Depends(get_current_user)
):
    # Choose points column based on timeframe
    points_col = "weekly_points" if timeframe == "weekly" else "total_points"

    result = supabase.table("user_scores")\
        .select(f"user_id, {points_col}, total_correct, accuracy_percentage")\
        .eq("competition", competition)\
        .eq("question_type", "all")\
        .order(points_col, desc=True)\
        .limit(limit)\
        .execute()

    rankings = []
    my_position = None

    for i, row in enumerate(result.data):
        # Get username
        user = supabase.table("users")\
            .select("username")\
            .eq("id", row["user_id"])\
            .execute()

        username = user.data[0]["username"] if user.data else "Unknown"
        points = row[points_col]

        entry = LeaderboardEntry(
            rank=i + 1,
            username=username,
            points=points,
            total_correct=row["total_correct"],
            accuracy_percentage=row["accuracy_percentage"]
        )
        rankings.append(entry)

        if row["user_id"] == current_user["id"]:
            my_position = {
                "rank": i + 1,
                "points": points
            }

    # If current user not in top results find their position
    if my_position is None:
        my_score = supabase.table("user_scores")\
            .select(f"{points_col}")\
            .eq("user_id", current_user["id"])\
            .eq("competition", competition)\
            .eq("question_type", "all")\
            .execute()

        if my_score.data:
            my_pts = my_score.data[0][points_col]
            higher = supabase.table("user_scores")\
                .select("user_id")\
                .eq("competition", competition)\
                .eq("question_type", "all")\
                .gt(points_col, my_pts)\
                .execute()

            my_position = {
                "rank": len(higher.data) + 1,
                "points": my_pts
            }

    return {
        "timeframe": timeframe,
        "competition": competition,
        "rankings": rankings,
        "my_position": my_position
    }