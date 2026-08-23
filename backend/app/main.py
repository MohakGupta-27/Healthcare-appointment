from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging(settings.debug)
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
