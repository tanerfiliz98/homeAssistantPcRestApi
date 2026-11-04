from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import require_api_key
from app.services.power import PowerAction, UnsupportedActionError, run_power_action

router = APIRouter(prefix="/power", tags=["power"], dependencies=[Depends(require_api_key)])


class PowerRequest(BaseModel):
    delay_seconds: int = Field(default=0, ge=0, le=3600)


@router.post("/{action}")
def power_action(action: PowerAction, body: PowerRequest | None = None) -> dict:
    payload = body or PowerRequest()
    try:
        return run_power_action(action, payload.delay_seconds)
    except UnsupportedActionError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
