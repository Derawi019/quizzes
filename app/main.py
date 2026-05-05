from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.questions.router import router as questions_router
from app.answers.router import router as answers_router
from app.leaderboard.router import router as leaderboard_router
from app.brackets.router import router as brackets_router
from app.admin.router import router as admin_router

app = FastAPI(title="Football Quiz API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(leaderboard_router)
app.include_router(brackets_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"status": "Football Quiz API is running"}