"""Version 1 HTTP routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.fapi_db_tmpl.api.protocols import GreetingServiceProtocol
from src.fapi_db_tmpl.api.dependencies import get_greeting_service

router = APIRouter(prefix="/v1", tags=["greetings"])


class GreetingResponse(BaseModel):
    message: str


@router.get("/greetings/{name}", response_model=GreetingResponse)
async def greet(
    name: str,
    greeter: GreetingServiceProtocol = Depends(get_greeting_service),
) -> GreetingResponse:
    """Return a personalised greeting provided by the configured service."""

    greeting = greeter.generate_greeting(name)
    return GreetingResponse(message=greeting)
