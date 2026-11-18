from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"
    database_url: str = "postgresql://readonly:readonly@localhost:5432/shop"
    max_rows: int = 200
    max_clarification_rounds: int = 2


settings = Settings()
