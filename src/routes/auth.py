from typing import List


from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Path,
    Request,
    status,
    Security,
    BackgroundTasks,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session
from src.database.models import Contact

from src.database.db import get_db
from src.schemas import (
    PsswordModel,
    UserModel,
    UserResponse,
    TokenModel,
    RequestEmail,
)
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email.mail import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
    It takes a UserModel object as input, which is validated by FastAPI.
    The function then checks if an account with that email already exists, and if so raises an HTTP 409 Conflict error.
    If no account exists with that email address, it hashes the password using auth_service's get_password_hash() function and saves the new user to the database using repository_users' create_user() function. Finally it adds a task to send confirmation emails via send_email(). The return value is a dictionary containing details about what happened.

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :param : Get the user's email and username
    :return: A dict with a user key and a detail key
    :doc-author: Ihor Voitiuk
    """

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Get a database session
    :return: A dictionary with three keys:
    :doc-author: Ihor Voitiuk
    """

    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=7200
    )
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
    It takes a valid refresh token and returns a new access token.
    The function also updates the user's refresh_token in the database.

    :param credentials: HTTPAuthorizationCredentials: Validate the token
    :param db: Session: Pass the database session to the function
    :param : Get the user's email from the token
    :return: A new access token and refresh token
    :doc-author: Ihor Voitiuk
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it gets that user from our database and checks if their account has already been confirmed.
        If so, we return a message saying as much; otherwise, we update their account in our database with an updated confirmed value of True.

    :param token: str: Get the token from the url
    :param db: Session: Get a database session
    :return: A message to the user
    :doc-author: Ihor Voitiuk
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The request_email function is used to request a confirmation email.
    It takes the user's email address and sends them an email with a link that they can click on to confirm their account.


    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :param : Get the token from the url
    :return: A message to the user
    :doc-author: Ihor Voitiuk
    """

    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}


@router.get("/reset-password/{token}")
async def reset_password_token(token: str, db: Session = Depends(get_db)):
    """
    The reset_password_token function is used to reset a user's password.
        It takes the token as an argument and returns a message that the user can change their password.

    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A message that the user can change their password
    :doc-author: Ihor Voitiuk
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
        # new_password = auth_service.get_password_hash()
        # await repository_users.reset_password(email, new_password, db)
    return {"message": "You can change your password"}


@router.put("/{user_id}", response_model=UserResponse)
async def updade_contac(
    body: PsswordModel,
    user_email: str = Path(description="The email of the user to update password"),
    db: Session = Depends(get_db),
    get_current_user: Contact = Depends(auth_service.get_current_user),
):
    """
    The updade_contac function update password user.

    :param body: PsswordModel: Get the password and confirm_password from the request body
    :param user_email: str: Get the email of the user to update password
    :param db: Session: Get the database session
    :param get_current_user: Contact: Get the current user
    :param : Get the user's email
    :return: A message
    :doc-author: Ihor Voitiuk
    """

    if body.password == body.confirm_password:
        new_password = auth_service.get_password_hash(body.password)
        user = await repository_users.reset_password(user_email, new_password, db)
        return {"message": "Your password has been changed."}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Your password is incorrect, please try again.",
    )


@router.post("/reset-password")
async def reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The reset_password function is used to reset a user's password.
    It takes the email of the user as input and sends an email with a link to change their password.
    The function returns a message indicating whether or not it was successful.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Pass the database session to the function
    :param : Get the user id from the token
    :return: A message to the user
    :doc-author: Ihor Voitiuk
    """

    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        background_tasks.add_task(
            send_email,
            user.email,
            user.username,
            request.base_url,
            "Reset your password ",
        )
        return {"message": "Check your email for change password and follow the link."}
    return {"message": "First you need to register your account"}
