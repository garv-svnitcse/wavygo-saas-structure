from __future__ import annotations

from typing import Annotated, Any, Optional
from fastapi import APIRouter, Depends, Query, Request
from bson import ObjectId

from app.modules.dashboard.schemas import DashboardStatsResponse
from app.modules.dashboard.service import dashboard_service

router = APIRouter()


async def get_optional_vendor(request: Request) -> Optional[dict[str, Any]]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    try:
        from app.modules.auth.security import decode_access_token, get_vendors_collection
        payload = decode_access_token(token)
        vendor_id = payload.get("sub")
        if not vendor_id:
            return None
        vendors = get_vendors_collection()
        return vendors.find_one({"_id": ObjectId(vendor_id)})
    except Exception:
        return None


@router.get("/stats", response_model=DashboardStatsResponse, summary="Get dashboard metrics and charts")
@router.get("", response_model=DashboardStatsResponse, summary="Get dashboard metrics (alias)", include_in_schema=False)
def get_dashboard_stats(
    range: Optional[str] = Query(default="Last 30 days", alias="range"),
    vendor: Annotated[Optional[dict[str, Any]], Depends(get_optional_vendor)] = None,
) -> DashboardStatsResponse:
    """
    Returns high-level fleet statistics, revenue numbers, utilization percentage,
    monthly trend data, and latest bookings for the partner dashboard.
    """
    tenant_id = str(vendor["_id"]) if vendor else None
    return dashboard_service.get_stats(date_range=range, tenant_id=tenant_id)
