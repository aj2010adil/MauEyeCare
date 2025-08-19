import os
from dataclasses import dataclass


def _expand_path(path: str) -> str:
    return os.path.expandvars(os.path.expanduser(path))


@dataclass
class Settings:
    # Postgres
    db_name: str = os.getenv("MAU_DB_NAME", "maueyecare")
    db_user: str = os.getenv("MAU_DB_USER", "maueyecare")
    db_password: str = os.getenv("MAU_DB_PASSWORD", "maueyecare")
    db_host: str = os.getenv("MAU_DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("MAU_DB_PORT", "5432"))

    # JWT
    jwt_secret_key: str = os.getenv("MAU_JWT_SECRET", "change-this-in-setup")
    jwt_refresh_secret_key: str = os.getenv("MAU_JWT_REFRESH_SECRET", "change-this-too")
    jwt_algorithm: str = os.getenv("MAU_JWT_ALG", "HS256")
    access_token_expires_minutes: int = int(os.getenv("MAU_ACCESS_TOKEN_MIN", "30"))
    refresh_token_expires_days: int = int(os.getenv("MAU_REFRESH_TOKEN_DAYS", "7"))

    # Filesystem
    documents_root: str = _expand_path(os.getenv(
        "MAU_DOCUMENTS_ROOT",
        os.path.join(os.getenv("USERPROFILE", "C:/Users/Public"), "Documents", "MauEyeCare"),
    ))

    @property
    def prescription_root(self) -> str:
        return os.path.join(self.documents_root, "prescriptions")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()


