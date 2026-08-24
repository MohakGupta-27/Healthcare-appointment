from fastapi import APIRouter

from app.api.v1 import auth, health, doctors, admin_doctors, appointments, calendar_routes

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(doctors.router)
api_router.include_router(admin_doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(calendar_routes.router)
