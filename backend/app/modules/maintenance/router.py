from __future__ import annotations

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status

from app.modules.maintenance.schemas import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceResponse,
    MaintenanceStatsResponse,
    VehicleReviewStatusUpdate,
)
from app.modules.maintenance.service import maintenance_service

router = APIRouter()


@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add vehicle to maintenance",
    description="Records a new maintenance job with damage/flaw details, start date, cost, and sets vehicle status to Maintenance.",
)
def create_maintenance(payload: MaintenanceCreate) -> MaintenanceResponse:
    try:
        return maintenance_service.create_maintenance(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to record maintenance: {str(exc)}",
        )


@router.get(
    "",
    response_model=List[MaintenanceResponse],
    summary="List maintenance jobs",
    description="Retrieve all maintenance records with optional status, vehicle, and search filters.",
)
def list_maintenance(
    status: Optional[str] = Query(None, description="Filter by status: Ongoing, Completed, or All"),
    vehicle_id: Optional[str] = Query(None, description="Filter by vehicle ID or name"),
    query: Optional[str] = Query(None, description="Search by ID, vehicle, type, mechanic or damage"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> List[MaintenanceResponse]:
    return maintenance_service.list_maintenance(
        status=status,
        vehicle_id=vehicle_id,
        query=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/stats",
    response_model=MaintenanceStatsResponse,
    summary="Get maintenance statistics",
    description="Returns counts of open jobs, completed jobs, and total maintenance costs.",
)
def get_stats() -> MaintenanceStatsResponse:
    return maintenance_service.get_stats()


@router.post(
    "/vehicle-status",
    summary="Update vehicle inspection / operational status",
    description="Transition vehicle status between Rented, Under Review, Available, or Maintenance.",
)
def update_vehicle_status(payload: VehicleReviewStatusUpdate) -> Dict[str, Any]:
    return maintenance_service.update_vehicle_review_status(payload)


@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
    summary="Get maintenance job details",
)
def get_maintenance(maintenance_id: str) -> MaintenanceResponse:
    record = maintenance_service.get_maintenance(maintenance_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record '{maintenance_id}' not found.",
        )
    return record


@router.patch(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
    summary="Update maintenance record",
)
def update_maintenance(maintenance_id: str, payload: MaintenanceUpdate) -> MaintenanceResponse:
    updated = maintenance_service.update_maintenance(maintenance_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record '{maintenance_id}' not found.",
        )
    return updated


@router.post(
    "/{maintenance_id}/complete",
    response_model=MaintenanceResponse,
    summary="Complete maintenance job",
    description="Marks the maintenance job as Completed and automatically releases the vehicle back to Available status.",
)
def complete_maintenance(
    maintenance_id: str,
    return_to_available: bool = Query(True, description="Release vehicle back to Available status"),
) -> MaintenanceResponse:
    record = maintenance_service.complete_maintenance(maintenance_id, return_to_available=return_to_available)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record '{maintenance_id}' not found.",
        )
    return record


@router.delete(
    "/{maintenance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete maintenance record",
)
def delete_maintenance(maintenance_id: str) -> None:
    success = maintenance_service.delete_maintenance(maintenance_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record '{maintenance_id}' not found.",
        )
