"""Application entrypoint for the FastAPI database template."""

from fastapi import FastAPI

from .dependencies import get_api_settings
from .routers.greetings import router


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""

    settings = get_api_settings()

    app = FastAPI(
        title=settings.api_name,
        version=settings.api_version,
        description="A FastAPI template project with database support.",
    )

    app.include_router(router)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Simple health check endpoint to confirm the API is running."""

        return {"status": "ok"}

    # print(f"Routes: {[route.path for route in app.router.routes]}")
    return app


app = create_app()
