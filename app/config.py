from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Cerebro — Adaptive Learning App"
    database_url: str = "sqlite:///./cerebro.db"
    debug: bool = False

    model_config = {"env_prefix": "CEREBRO_"}


settings = Settings()
