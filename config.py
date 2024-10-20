from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra="allow")

    app_name: str = "PostCommentAPI"
    SQLALCHEMY_DATABASE_URL: str
    USER_SECRET_KEY: str

settings = Settings()
