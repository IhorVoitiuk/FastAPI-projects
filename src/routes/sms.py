from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.services.auth import auth_service
from src.services.roles import RolesAccess
from src.services.send_sms import send_sms
from src.schemas import SendSMSModel, SendSMSResponse
from src.repository import sms as respository_sms


router = APIRouter(prefix="/send_sms", tags=["send_sms"])

access_post = RolesAccess([Role.admin, Role.moderator, Role.user])


@router.post(
    "/",
    response_model=SendSMSResponse,
    description="No more than 10 requests per minute. This is a test option \
        and to send to all numbers you need to purchase an account in Twilio.\n\
            You can message me.",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_sms(
    body: SendSMSModel,
    db: Session = Depends(get_db),
    get_current_user: User = Depends(auth_service.get_current_user),
):
    """
    The create_sms function creates a new sms in the database.

    :param body: SendSMSModel: Get the data from the request body
    :param db: Session: Get the database session
    :param get_current_user: User: Get the current user
    :param : Get the current user from the database
    :return: A new sms object
    :doc-author: Ihor Voitiuk
    """
    send_sms_message = await send_sms(body.message, body.from_phone, body.to_phone)
    sms = await respository_sms.create_sms(body, get_current_user.email, db)

    return sms
