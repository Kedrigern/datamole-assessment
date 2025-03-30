from datetime import datetime
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GH Stats"
    debug: bool = False

    expire_after: int = 7200
    base_url: str = "https://api.github.com/repos/"
    end_of_url: str = "/events"
    requests_cache: str
    events_db: str
    gh_token: str
    repos: list[str]
    history_limit: datetime

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Settings()
