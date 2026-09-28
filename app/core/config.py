import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB Atlas Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "lab_management"

    # JWT Authentication Configuration
    JWT_SECRET: str = "super_secret_lab_management_jwt_key_at_least_32_bytes_long_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Frontend CORS Configuration
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        origins = [
            origin.strip()
            for origin in self.FRONTEND_URL.split(",")
            if origin.strip()
        ]
        # Always allow standard local dev origins if not explicitly listed
        default_dev_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        for dev_origin in default_dev_origins:
            if dev_origin not in origins:
                origins.append(dev_origin)
        return origins


settings = Settings()
