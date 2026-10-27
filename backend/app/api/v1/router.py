from fastapi import APIRouter

from app.modules.bookings.router import router as bookings_router
from app.modules.documents.router import router as documents_router

api_router = APIRouter()


@api_router.get("/health")
def api_health_check() -> dict[str, str]:
    return {"status": "ok", "scope": "api"}


api_router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
