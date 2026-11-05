from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.modules.payments.schemas import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentStatsResponse,
)
from app.modules.payments.service import payment_service

router = APIRouter()


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record payment transaction",
    description="Record a cash, UPI, or card payment against a booking, updating both the payment ledger and booking balance.",
)
def record_payment(payload: PaymentCreate) -> PaymentResponse:
    try:
        return payment_service.record_payment(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to record payment: {str(exc)}",
        )


@router.get(
    "/stats",
    response_model=PaymentStatsResponse,
    summary="Get payment & finance statistics",
    description="Retrieve aggregated metrics for total collected revenue, online/offline split, and outstanding balances.",
)
def get_payment_stats() -> PaymentStatsResponse:
    return payment_service.get_stats()


@router.get(
    "",
    response_model=List[PaymentResponse],
    summary="List payment transactions",
    description="Retrieve all transactions with optional filtering by status (Paid, Partial, Refunded) and keyword search.",
)
def list_payments(
    status: Optional[str] = Query(None, description="Filter by status: Paid, Partial, Refunded"),
    method: Optional[str] = Query(None, description="Filter by method: Cash, UPI, Card, Bank Transfer"),
    query: Optional[str] = Query(None, description="Search by transaction ID, customer, booking, or reference"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> List[PaymentResponse]:
    return payment_service.list_payments(
        status=status,
        method=method,
        query=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment details",
    description="Fetch a single transaction record by its ID (e.g. TX-7082).",
)
def get_payment(payment_id: str) -> PaymentResponse:
    payment = payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment transaction with ID '{payment_id}' not found.",
        )
    return payment


@router.patch(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Update payment record",
    description="Update transaction status or notes.",
)
def update_payment(payment_id: str, payload: PaymentUpdate) -> PaymentResponse:
    updated = payment_service.update_payment(payment_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment transaction with ID '{payment_id}' not found.",
        )
    return updated


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentResponse,
    summary="Process payment refund",
    description="Mark a transaction as refunded with optional reason.",
)
def refund_payment(payment_id: str, reason: Optional[str] = Query(None)) -> PaymentResponse:
    refunded = payment_service.refund_payment(payment_id, reason=reason)
    if not refunded:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment transaction with ID '{payment_id}' not found.",
        )
    return refunded
