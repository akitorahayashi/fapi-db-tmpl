"""Application entrypoint for the FastAPI database template."""

from fastapi import Depends, FastAPI

from .api.protocols import GreetingServiceProtocol
from .api.router import router as v1_router
from .api.dependencies import get_app_settings, get_greeting_service


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""

    settings = get_app_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A FastAPI template project with database support.",
    )

    app.include_router(v1_router)

    @app.get("/")
    async def hello_world(
        greeter: GreetingServiceProtocol = Depends(get_greeting_service),
    ) -> dict[str, str]:
        """Return a basic greeting sourced from the configured service."""

        return {"message": greeter.generate_greeting("World")}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Simple health check endpoint to confirm the API is running."""

        return {"status": "ok"}

    # print(f"Routes: {[route.path for route in app.router.routes]}")
    return app


app = create_app()
