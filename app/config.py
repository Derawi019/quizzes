from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = BASE_DIR / ".env"

settings = Settings()