from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.auth.schemas import SignupRequest, LoginRequest, TokenResponse
from app.auth.utils import hash_password, verify_password, create_access_token
from app.users.schemas import UserProfileResponse, UserProfileUpdate, UserScoresResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup(data: SignupRequest):
    # Check password length
    if len(data.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be 72 characters or less")

    # Check if email already exists
    existing = supabase.table("users")\
        .select("id")\
        .eq("email", data.email)\
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username already exists
    existing_username = supabase.table("users")\
        .select("id")\
        .eq("username", data.username)\
        .execute()

    if existing_username.data:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    supabase.table("users").insert({
        "username": data.username,
        "email": data.email,
        "password_hash": hash_password(data.password)
    }).execute()

    return {"message": "Account created successfully"}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    # Find user by email
    result = supabase.table("users")\
        .select("*")\
        .eq("email", data.email)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]

    # Verify password
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create token
    token = create_access_token({"sub": user["id"]})

    return {"access_token": token}






