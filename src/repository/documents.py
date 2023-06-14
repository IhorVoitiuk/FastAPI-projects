from sqlalchemy.orm import Session

from src.database.models import Document, User
from src.schemas import DocumentModel


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


async def update_documents_count(user_email: str, count_files: int, db: Session):
    """
    The update_documents_count function updates the number of documents a user has.

        Args:
            email (str): The email address of the user to update.
            count (int): The amount to increment or decrement by.  If negative, will decrement instead of incrementing.

    :param user_email: str: Identify the user in the database
    :param count_files: int: Determine whether the user's document count should be increased or decreased
    :param db: Session: Pass the database session to the function
    :return: The number of documents a user has
    :doc-author: Ihor Voitiuk
    """
    user = await get_user_by_email(user_email, db)
    if user:
        if user.document is None:
            document = Document(total_count=count_files, user=user)
            db.add(document)
            db.commit()
            db.refresh(document)
            return document.total_count
        else:
            user.document.total_count += count_files
            db.commit()
            db.refresh(user.document)
            return user.document.total_count
    else:
        return "You must authorize!"
