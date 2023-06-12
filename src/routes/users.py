from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserDB
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDB)
async def read_users_me(
    get_current_user: User = Depends(auth_service.get_current_user),
):
    """
    The read_users_me function returns the current user.

    :param get_current_user: User: Get the current user from the authentication service
    :return: The current user
    :doc-author: Ihor Voitiuk
    """

    return get_current_user


@router.patch("/avatar", response_model=UserDB)
async def update_cat(
    file: UploadFile = File(),
    db: Session = Depends(get_db),
    get_current_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_cat function takes a file and updates the current user's avatar.

    :param file: UploadFile: Get the file from the request body
    :param db: Session: Access the database
    :param get_current_user: User: Get the current user
    :param : Get the current user
    :return: The user object
    :doc-author: Ihor Voitiuk
    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    public_id = f"FastAPIproject/{get_current_user.id}{get_current_user.username}"
    r = cloudinary.uploader.upload(file.file, public_id=public_id, owerwrite=True)
    avatar_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    user = await repository_users.update_avatar(get_current_user.email, avatar_url, db)

    return user
