from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.modules.bookings.schemas import (
    OfflineBookingCreate,
    OfflineBookingUpdate,
    OfflineBookingResponse,
    PaymentRecordCreate,
)
from app.modules.bookings.service import booking_service

router = APIRouter()


@router.post(
    "/offline",
    response_model=OfflineBookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an offline booking",
    description="Record an in-store / walk-in offline booking with vehicle, customer, rental dates and payment breakdown.",
)
def create_offline_booking(payload: OfflineBookingCreate) -> OfflineBookingResponse:
    try:
        return booking_service.create_offline_booking(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create offline booking: {str(exc)}",
        )


@router.get(
    "/offline",
    response_model=List[OfflineBookingResponse],
    summary="List offline bookings",
    description="Retrieve all offline bookings with optional filtering by status and search keyword.",
)
def list_offline_bookings(
    status: Optional[str] = Query(None, description="Filter by status, e.g., Active, Completed, Cancelled"),
    query: Optional[str] = Query(None, description="Search by ID, customer name or vehicle name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> List[OfflineBookingResponse]:
    return booking_service.list_bookings(status=status, query=query, skip=skip, limit=limit)


@router.get(
    "/offline/{booking_id}",
    response_model=OfflineBookingResponse,
    summary="Get offline booking details",
    description="Fetch a single offline booking record by its ID (e.g., BK-123456).",
)
def get_offline_booking(booking_id: str) -> OfflineBookingResponse:
    booking = booking_service.get_booking(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID '{booking_id}' not found.",
        )
    return booking


@router.patch(
    "/offline/{booking_id}",
    response_model=OfflineBookingResponse,
    summary="Update offline booking status or details",
    description="Update booking status (Active, Completed, Cancelled) or notes.",
)
def update_offline_booking(booking_id: str, payload: OfflineBookingUpdate) -> OfflineBookingResponse:
    updated = booking_service.update_booking(booking_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID '{booking_id}' not found.",
        )
    return updated


@router.post(
    "/offline/{booking_id}/payments",
    response_model=OfflineBookingResponse,
    summary="Record payment for an offline booking",
    description="Record a cash/UPI/card payment against a pending booking balance.",
)
def record_booking_payment(booking_id: str, payment: PaymentRecordCreate) -> OfflineBookingResponse:
    updated = booking_service.record_payment(booking_id, payment)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID '{booking_id}' not found.",
        )
    return updated
