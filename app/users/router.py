from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.auth.utils import get_current_user
from app.users.schemas import UserProfileResponse, UserProfileUpdate, UserScoresResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    result = supabase.table("users")\
        .select("id, username, email, avatar_url, favorite_club_id")\
        .eq("id", current_user["id"])\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return result.data[0]

@router.put("/me")
def update_my_profile(
    data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    updates = {k: v for k, v in data.dict().items() if v is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    supabase.table("users")\
        .update(updates)\
        .eq("id", current_user["id"])\
        .execute()

    return {"message": "Profile updated successfully"}


@router.get("/me/scores", response_model=UserScoresResponse)
def get_my_scores(current_user: dict = Depends(get_current_user)):
    result = supabase.table("user_scores")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .eq("competition", "all")\
        .eq("question_type", "all")\
        .execute()

    if not result.data:
        return UserScoresResponse()

    return result.data[0]


@router.get("/me/badges")
def get_my_badges(current_user: dict = Depends(get_current_user)):
    result = supabase.table("user_badges")\
        .select("*, badges(code, name, description, icon)")\
        .eq("user_id", current_user["id"])\
        .execute()

    return {"badges": result.data}