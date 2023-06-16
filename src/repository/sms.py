import datetime
from sqlalchemy.orm import Session

from src.database.models import User, TotalSMS, MessageSMS
from src.schemas import SendSMSModel, SendSMSResponse


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes an email and a database session as arguments.
    It then queries the database for a user with that email address, returning the first result.
    If no such user exists, it returns None.

    :param email: str: Specify the type of the parameter
    :param db: Session: Pass in the database session
    :return: The first user in the database that matches the email provided
    :doc-author: Ihor Voitiuk
    """
    return db.query(User).filter(User.email == email).first()


async def create_sms(body: SendSMSModel, user_email: str, db: Session):
    """
    The create_sms function creates a new sms message.
    
        Args:
            body (SendSMSModel): The request body, in this case containing the message to send.
            user_email (str): The email of the user sending the SMS message.
    
    :param body: SendSMSModel: Pass the data from the request body
    :param user_email: str: Get the user by email
    :param db: Session: Access the database
    :return: An object of type sendsmsresponse
    :doc-author: Ihor Voitiuk
    """
    total_sms = db.query(TotalSMS).first()
    if total_sms is None:
        total_sms = TotalSMS(total_send_sms=0)
        db.add(total_sms)
        db.commit()
    if total_sms.total_send_sms >= 100:
        return "The limit for sending messages has been reached!"

    user = await get_user_by_email(user_email, db)
    if user:
        if user.messagesms is None:
            message = MessageSMS(
                message=body.message,
                from_phone=body.from_phone,
                to_phone=body.to_phone,
                user_id=user.id,
                total_sms_id=total_sms.id,
            )
            db.add(message)
        else:
            message = MessageSMS(
                message=body.message,
                from_phone=body.from_phone,
                to_phone=body.to_phone,
                user_id=user.id,
                total_sms_id=total_sms.id,
            )
            user.messagesms.append(message)
        total_sms.total_send_sms += 1
        db.commit()
        db.refresh(user)
        response = SendSMSResponse(
            id=message.id,
            message=message.message,
            from_phone=message.from_phone,
            to_phone=message.to_phone,
            created_at=message.created_at,
            user_id=message.user_id,
            total_sms=total_sms.total_send_sms,
        )
        return response

    else:
        return "You must authorize!"
