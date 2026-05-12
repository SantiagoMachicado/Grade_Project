from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Salud Digital Bolivia API"
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:nimda@localhost:5434/salud_digital",
        env="DATABASE_URL"
    )
    SECRET_KEY: str = Field(default="CHANGE_ME_IN_PRODUCTION", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_API_KEY: str | None = None
    
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "santiago.machicado@ucb.edu.bo"
    SMTP_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
