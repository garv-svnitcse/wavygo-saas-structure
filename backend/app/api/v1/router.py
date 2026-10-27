from fastapi import APIRouter

<<<<<<< HEAD
from app.modules.bookings.router import router as bookings_router
from app.modules.documents.router import router as documents_router
=======
from app.modules.vehicles.router import router as vehicles_router
>>>>>>> upstream/feature/saas-structure

api_router = APIRouter()


@api_router.get("/health")
def api_health_check() -> dict[str, str]:
    return {"status": "ok", "scope": "api"}


<<<<<<< HEAD
api_router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
=======
api_router.include_router(vehicles_router, prefix="/vehicles", tags=["vehicles"])
>>>>>>> upstream/feature/saas-structure
