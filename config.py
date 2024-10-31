from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    app_name: str = "PostCommentAPI"
    USER_SECRET_KEY: str
    PERSPECTIVE_API_KEY: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str

    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str

    @property
    def SQLALCHEMY_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self):
        return f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(__file__), 'tests', 'test_database.db')}"


settings = Settings()

if __name__ == '__main__':
    print(settings.SQLALCHEMY_DATABASE_URL)
