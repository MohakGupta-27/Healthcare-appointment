from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.health import get_health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse | JSONResponse:
    result = get_health(db)
    if result.status != "ok":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=result.model_dump(),
        )
    return result
