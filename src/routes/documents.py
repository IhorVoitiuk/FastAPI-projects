from typing import List

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse, Response
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Document, Role, User
from src.services.auth import auth_service
from src.services.roles import RolesAccess
from src.repository import documents as respository_documents
from src.services.documents import pdf_utils
from src.schemas import CompressionRequest


router = APIRouter(prefix="/documents", tags=["documents"])

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator])
access_update = RolesAccess([Role.admin, Role.moderator])
access_delete = RolesAccess([Role.admin])


@router.post(
    "/convert_images_to_pdf",
    description="No more than 10 requests per minute.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60)), Depends(access_get)],
)
async def convert_images_to_pdf_route(
    file: list[UploadFile] | None = None,
    db: Session = Depends(get_db),
    get_current_user: User = Depends(auth_service.get_current_user),
):
    """
    The convert_images_to_pdf_route function converts images to a PDF file.

    :param file: list[UploadFile] | None: Accept a list of files
    :param db: Session: Get the database session
    :param get_current_user: User: Get the current user's email address
    :param : Get the current user
    :return: A streamingresponse object
    :doc-author: Ihor Voitiuk
    """
    if not file:
        return {"message": "No upload file sent"}

    pdf_data = await pdf_utils.convert_images_to_pdf(file)
    count_files = len(file)

    total_count = await respository_documents.update_documents_count(
        get_current_user.email, count_files, db
    )

    response_data = {
        "message": "Conversion successful",
        "attempt_count": count_files,
        "total_count": total_count,
    }

    return StreamingResponse(
        pdf_data,
        media_type="application/pdf",
        headers={f"Content-Disposition": "attachment; filename=converted_images.pdf"},
    )


@router.post(
    "/compress_pdf",
    description="No more than 10 requests per minute. Compression: lossless compression, remove images, remove duplication",
    dependencies=[Depends(RateLimiter(times=10, seconds=60)), Depends(access_get)],
)
async def compress_pdf_route(
    compression: str = "lossless compression",
    file: UploadFile | None = None,
    db: Session = Depends(get_db),
    get_current_user: User = Depends(auth_service.get_current_user),
):
    """
    The compress_pdf_route function is a route that allows the user to compress PDF files.
    The function takes in an optional compression parameter, which can be one of three values:
        - lossless compression (default)
        - remove images
        - remove duplication

    :param compression: str: Determine the type of compression to be applied on the pdf file
    :param file: UploadFile | None: Receive the file sent by the user
    :param db: Session: Pass the database session to the function
    :param get_current_user: User: Get the current user's email
    :param : Get the current user
    :return: A response object
    :doc-author: Ihor Voitiuk
    """

    if not file:
        return {"message": "No upload file sent"}
    elif compression not in [
        "lossless compression",
        "remove images",
        "remove duplication",
    ]:
        return {
            "message": "No supported compression quality. Choose the folowing \
                        compression quality: lossless compression, remove images, remove duplication"
        }

    (
        pdf_data,
        initial_file_size,
        final_file_size,
        percentage_reduction,
    ) = await pdf_utils.compress_pdf(file, compression)
    total_count = await respository_documents.update_documents_count(
        get_current_user.email, 1, db
    )

    response_data = {
        "message": "Conversion successful",
        "attempt_count": 1,
        "total_count": total_count,
        "measurement": "Mb",
        "initial_file_size": initial_file_size,
        "final_file_size": final_file_size,
        "percentage_reduction": percentage_reduction,
    }

    return Response(
        pdf_data,
        media_type="application/pdf",
        headers={f"Content-Disposition": "attachment; filename=compression.pdf"},
    )
