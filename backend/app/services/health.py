import logging

from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.health import HealthResponse, HealthStatus

logger = logging.getLogger(__name__)


def _check_postgres(db: Session) -> HealthStatus:
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except SQLAlchemyError:
        logger.exception("PostgreSQL health check failed")
        return "error"


def _check_redis() -> HealthStatus:
    try:
        client = Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        try:
            if client.ping():
                return "ok"
            return "error"
        finally:
            client.close()
    except RedisError:
        logger.exception("Redis health check failed")
        return "error"


def get_health(db: Session) -> HealthResponse:
    postgres = _check_postgres(db)
    redis_status = _check_redis()
    overall = "ok" if postgres == "ok" and redis_status == "ok" else "degraded"
    return HealthResponse(status=overall, postgres=postgres, redis=redis_status)
