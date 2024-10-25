from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    app_name: str = "PostCommentAPI"
    SQLALCHEMY_DATABASE_URL: str
    USER_SECRET_KEY: str
    PERSPECTIVE_API_KEY: str

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_BACKEND_URL: str = "redis://redis:6379/1"


    @property
    def GET_TEST_DATABASE_URL(self):
        return f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(__file__), 'tests', 'test_database.db')}"


settings = Settings()
