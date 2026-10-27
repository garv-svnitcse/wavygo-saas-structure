from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WavyGo Vendor API"
    app_env: str = "development"
    mongo_uri: Optional[str] = None
    mongodb_uri: Optional[str] = None
    mongodb_database: str = "wavygo_vendor"
    frontend_origin: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:3000,http://127.0.0.1:3000"

    # Cloudinary credentials
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def effective_mongo_uri(self) -> Optional[str]:
        return self.mongodb_uri or self.mongo_uri

    @property
    def frontend_origins(self) -> List[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]


settings = Settings()
