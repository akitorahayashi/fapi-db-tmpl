from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """
    Database settings loaded from environment variables.
    """

    use_sqlite: bool = Field(
        default=True,
        alias="FAPI_DB_TMPL_USE_SQLITE",
        title="Use SQLite",
        description="Whether to use SQLite database instead of PostgreSQL.",
    )

    # PostgreSQL settings
    postgres_host: str = Field(
        default="db",
        alias="POSTGRES_HOST",
        title="PostgreSQL Host",
        description="Hostname or IP address of the PostgreSQL server.",
    )
    postgres_port: int = Field(
        default=5432,
        alias="POSTGRES_PORT",
        title="PostgreSQL Port",
        description="Port number on which the PostgreSQL server is listening.",
    )
    postgres_user: str = Field(
        default="user",
        alias="POSTGRES_USER",
        title="PostgreSQL User",
        description="Username for connecting to the PostgreSQL database.",
    )
    postgres_password: str = Field(
        default="password",
        alias="POSTGRES_PASSWORD",
        title="PostgreSQL Password",
        description="Password for the PostgreSQL user.",
    )
    postgres_db: str = Field(
        default="",
        alias="POSTGRES_DB",
        title="PostgreSQL Database",
        description="Name of the PostgreSQL database to connect to.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def _check_postgres_db(self) -> "DBSettings":
        if not self.use_sqlite and not self.postgres_db:
            raise ValueError("POSTGRES_DB must be set when FAPI_DB_TMPL_USE_SQLITE is False.")
        return self

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.use_sqlite:
            return "sqlite:///./test_db.sqlite3"
        else:
            return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
