from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.bookings.router import router as bookings_router
from app.modules.customers.router import router as customers_router
from app.modules.documents.router import router as documents_router
from app.modules.vehicles.router import router as vehicles_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(customers_router)


@api_router.get("/health")
def api_health_check() -> dict[str, str]:
    return {"status": "ok", "scope": "api"}


api_router.include_router(vehicles_router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
