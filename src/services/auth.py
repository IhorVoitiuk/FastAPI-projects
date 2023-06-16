import pickle

from typing import Optional
from datetime import datetime, timedelta

import redis as redis_db
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    """
    This class provides helper methods for authentication, such as hashing passwords,
    generating JWT tokens, and decoding JWT tokens.

    Attributes:
    - pwd_context (CryptContext): A context object for hashing passwords.
    - SECRET_KEY (str): The secret key used to encode and decode JWT tokens.
    - ALGORITHM (str): The hashing algorithm used to encode and decode JWT tokens.
    - oauth2_scheme (OAuth2PasswordBearer): An OAuth2 scheme used for token-based authentication.
    - redis (Redis): A Redis instance used for caching user information.
    :doc-author: Ihor Voitiuk
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key_jwt
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis_db.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password
    )

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the CryptContext object to verify that
        the plain-text password matches the hashed version. If it does, it returns True; if not, False.

        :param self: Make the method a bound method, which means that it can be called on instances of the class
        :param plain_password: Pass in the password that is entered by the user
        :param hashed_password: Pass in the hashed password from the database
        :return: True if the password is correct and false otherwise
        :doc-author: Ihor Voitiuk
        """

        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password and returns the hashed version of it.
        The hashing algorithm is defined in the config file, which is passed to CryptContext.

        :param self: Represent the instance of the class
        :param password: str: Specify the password that is to be hashed
        :return: A password hash
        :doc-author: Ihor Voitiuk
        """

        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.
            The function takes in the data to be encoded, and an optional expires_delta parameter.
            If no expires_delta is provided, the default value of 15 minutes will be used.
            The iat (issued at) claim is added automatically by PyJWT and set to utcnow().
            This means that when we decode this token later on, we can check if it has expired or not.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A token that is encoded with the jwt algorithm
        :doc-author: Ihor Voitiuk
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=180)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
            The function takes in three arguments: self, data, and expires_delta.
            The self argument is the class itself (OAuth2PasswordBearer).
            The data argument is a dictionary containing information about the user's session.  This includes their username and password hash as well as other information such as their email address or phone number if they have provided it to us.  It also contains an iat key which stands for &quot;issued at&quot; time which tells us when this token was created and an exp key which stands for expiration time that tells us when this

        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded into the token
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token that is encoded with the user's id, username and email
        :doc-author: Ihor Voitiuk
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    def create_email_token(self, data: dict):
        """
        The create_email_token function creates a token that is used to verify the user's email address.
        The token is created using the JWT library and contains information about when it was issued,
        when it expires, and what scope (or purpose) it has. The function returns this token.

        :param self: Make the function a method of the class
        :param data: dict: Pass the data that will be encoded in the token
        :return: A token
        :doc-author: Ihor Voitiuk
        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
            The function takes in a refresh_token as an argument and returns the email of the user if successful.
            If not, it raises an HTTPException with status code 401 (Unauthorized) and detail message &quot;Invalid scope for token&quot; or &quot;Could not validate credentials&quot;.

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that is sent to the server
        :return: The email of the user
        :doc-author: Ihor Voitiuk
        """

        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=self.ALGORITHM
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
        If the scope of the token is not &quot;email_token&quot;, then it raises an HTTPException. If there is a JWTError, then it also raises an HTTPException.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that we want to decode
        :return: The email address associated with the token
        :doc-author: Ihor Voitiuk
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError as error:
            print(error)
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be injected into the
            function that requires it. It will return the user object for the current
            request, if there is one. If not, it raises an HTTPException with status code 401.

        :param self: Access the class attributes
        :param token: str: Get the token from the authorization header
        :param db: Session: Get the database session
        :return: The user object associated with the token
        :doc-author: Ihor Voitiuk
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.redis.get(f"user:{email}")
        if user is None:
            print("GET USER FROM POSTGRES")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.redis.set(f"user:{email}", pickle.dumps(user))
            self.redis.expire(f"user:{email}", 900)
        else:
            print("GET USER FROM CACHE")
            user = pickle.loads(user)
        return user


auth_service = Auth()
