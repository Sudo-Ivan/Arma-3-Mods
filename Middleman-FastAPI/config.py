from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str
    ollama_api_url: str
    openrouter_site_url: str = "http://localhost"
    openrouter_site_name: str = "Arma3LLMGod"

    class Config:
        env_file = ".env"


settings = Settings()
