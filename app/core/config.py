from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/world_cup_prediction"
    secret_key: str = "change-me-in-local-env-with-at-least-32-chars"
    access_token_expire_minutes: int = 60
    backend_cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    admin_emails: str = "ian@test.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url

    @property
    def admin_email_set(self) -> set[str]:
        return {email.strip().lower() for email in self.admin_emails.split(",") if email.strip()}

    def validate_production(self) -> None:
        if self.environment.lower() != "production":
            return
        if self.secret_key == "change-me-in-local-env-with-at-least-32-chars" or len(self.secret_key) < 32:
            raise RuntimeError("SECRET_KEY must be set to a strong value in production.")
        if not self.cors_origins:
            raise RuntimeError("BACKEND_CORS_ORIGINS must include the deployed frontend origin in production.")


settings = Settings()
settings.validate_production()
