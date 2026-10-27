from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.modules.documents.schemas import DocumentResponse, DocumentUpdate
from app.modules.documents.service import document_service

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document to Cloudinary and store URL in DB",
    description="Uploads a business or vehicle document file to Cloudinary and saves its URL, category and metadata in MongoDB.",
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload (PDF, PNG, JPG, etc.)"),
    name: str = Form(..., description="Document title/name"),
    category: str = Form(..., description="Category, e.g. Shop License, GST Certificate, Insurance"),
    scope: str = Form("Business", description="Scope: Business or Vehicle"),
    vehicle_id: Optional[str] = Form(None, description="Optional associated vehicle ID"),
    vehicle_name: Optional[str] = Form(None, description="Optional associated vehicle name"),
    status_val: str = Form("In review", description="Initial verification status"),
    notes: Optional[str] = Form(None, description="Optional remarks or notes"),
) -> DocumentResponse:
    try:
        return await document_service.upload_document(
            file=file,
            name=name,
            category=category,
            scope=scope,
            vehicle_id=vehicle_id,
            vehicle_name=vehicle_name,
            status=status_val,
            notes=notes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document upload failed: {str(exc)}",
        )


@router.get(
    "",
    response_model=List[DocumentResponse],
    summary="List all documents",
    description="Fetch business and vehicle documents with optional filtering by scope, category or search query.",
)
def list_documents(
    scope: Optional[str] = Query(None, description="Filter by scope: Business or Vehicle"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status: Verified, In review, Expired"),
    query: Optional[str] = Query(None, description="Search keyword in name or vehicle"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> List[DocumentResponse]:
    return document_service.list_documents(
        scope=scope,
        category=category,
        status=status,
        query=query,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
    description="Fetch a single document record by ID (e.g. DC-101).",
)
def get_document(document_id: str) -> DocumentResponse:
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return doc


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update document metadata or status",
    description="Update verification status (Verified, In review, Expired) or document details.",
)
def update_document(document_id: str, payload: DocumentUpdate) -> DocumentResponse:
    updated = document_service.update_document(document_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return updated


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete document",
    description="Delete a document record from DB and remove its file from Cloudinary.",
)
def delete_document(document_id: str) -> dict:
    deleted = document_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return {"message": f"Document '{document_id}' deleted successfully.", "id": document_id}
