from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ShadowByte Cyber Operations Platform"
    database_url: str = "sqlite:///./shadowbyte.db"
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_assessment_timeout_seconds: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
