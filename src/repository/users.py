from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


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


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
    It takes a UserModel object and returns a User object.


    :param body: UserModel: Create a new user object from the data passed in
    :param db: Session: Pass in the database session
    :return: A user object
    :doc-author: Ihor Voitiuk
    """

    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user that is being updated
    :param token: str | None: Update the refresh_token field in the user table
    :param db: Session: Access the database
    :return: None
    :doc-author: Ihor Voitiuk
    """

    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes an email and a database session as arguments.
    It then gets the user from the database using that email, sets their confirmed field to True,
    and commits those changes to the database.

    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: None, but it does update the user's confirmed field to true
    :doc-author: Ihor Voitiuk
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def reset_password(email: str, new_password: str, db: Session) -> None:
    """
    The reset_password function takes an email and a new password,
    and updates the user's password in the database.


    :param email: str: Identify the user
    :param new_password: str: Set the new password for the user
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Ihor Voitiuk
    """

    user = await get_user_by_email(email, db)
    user.password = new_password
    db.commit()
    db.refresh(user)
    return user


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    The update_avatar function takes an email and a url as arguments.
    It then uses the get_user_by_email function to retrieve the user from the database.
    The avatar attribute of that user is set to be equal to the url argument, and then
    the db session is committed so that it can be saved in our database.

    :param email: Find the user in the database
    :param url: str: Specify the type of the parameter
    :param db: Session: Pass a database session to the function
    :return: The updated user object
    :doc-author: Ihor Voitiuk
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
