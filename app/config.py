from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://authuser:authpass@localhost:5432/authdb"
    SECRET_KEY: str = "change-me-in-prod"
    TOKEN_LIFETIME_MINUTES: int = 60 * 8  # 8 часов

    class Config:
        env_file = ".env"


settings = Settings()
