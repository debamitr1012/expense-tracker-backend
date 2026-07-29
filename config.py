# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mongodb+srv://debamitr10_db_user:KtAqHvBP6g3haOe5@clusteretdb.i0dr4ev.mongodb.net/?appName=ClusterETdb"
    database_name: str = "expensetracker"

    jwt_key: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_AT_LEAST_32_CHARS_LONG_123!"
    jwt_issuer: str = "ExpenseTrackerApi"
    jwt_audience: str = "ExpenseTrackerClient"
    jwt_expiry_minutes: int = 1440

    cors_allowed_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )


settings = Settings()
