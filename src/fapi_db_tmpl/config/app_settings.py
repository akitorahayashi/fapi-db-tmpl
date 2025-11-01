from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    General application settings loaded from environment variables.
    """

    app_name: str = Field(
        default="FastAPI Template",
        alias="APP_NAME",
        title="Application Name",
        description="The name of the application.",
    )
    app_version: str = Field(
        default="0.1.0",
        alias="APP_VERSION",
        title="Application Version",
        description="The version of the application.",
    )
    use_mock_greeting: bool = Field(
        default=False,
        alias="FAPI_DB_TMPL_USE_MOCK_GREETING",
        title="Use mock greeting service",
        description="Toggle to inject the development mock greeting service.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )
