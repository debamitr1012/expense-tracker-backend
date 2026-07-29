# pyrefly: ignore [missing-import]
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_mode: str = Field(default="local", alias="DATABASE_MODE")
    database_url_local: str = Field(default="mongodb://localhost:27017", alias="DATABASE_URL_LOCAL")
    database_url_prod: str = Field(
        default="mongodb+srv://debamitr10_db_user:KtAqHvBP6g3haOe5@clusteretdb.i0dr4ev.mongodb.net/?appName=ClusterETdb",
        alias="DATABASE_URL_PROD",
    )
    database_name: str = "expensetracker"

    jwt_key: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_AT_LEAST_32_CHARS_LONG_123!"
    jwt_issuer: str = "ExpenseTrackerApi"
    jwt_audience: str = "ExpenseTrackerClient"
    jwt_expiry_minutes: int = 1440

    cors_allowed_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )

    @property
    def database_url(self) -> str:
        return self.database_url_prod if self.database_mode.lower() == "prod" else self.database_url_local


settings = Settings()
