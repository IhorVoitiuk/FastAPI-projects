from datetime import datetime, date

from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field("first_name", min_length=2, max_length=20)
    last_name: str = Field("last_name", min_length=2, max_length=20)
    email: EmailStr
    phone_number: str = Field("phone_number", min_length=5, max_length=30)
    birthday: date
    description: str = Field("description", min_length=10, max_length=200)


class ContactResponse(ContactModel):
    id: int = 1
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDB(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDB
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmailSchema(BaseModel):
    email: EmailStr


class RequestEmail(BaseModel):
    email: EmailStr


class PasswordSchema(BaseModel):
    password: str


class PsswordModel(BaseModel):
    password: str
    confirm_password: str


class DocumentModel(BaseModel):
    count: int


class CompressionRequest(BaseModel):
    compression_quality: str = Field(
        "lossless compression",
        description="Compression quality. Supported formats: lossless compression, remove images, remove duplication",
    )


class SendSMSModel(BaseModel):
    message: str = Field(
        "Hello, thank you for using our application.\nGood day!",
        min_length=2,
        max_length=240,
    )
    from_phone: str = Field("+14302335529", min_length=2, max_length=20)
    to_phone: str = Field("+380639249861", min_length=13, max_length=13)


class SendSMSResponse(SendSMSModel):
    id: int = 1
    created_at: datetime
    user_id: int
    total_sms: int

    class Config:
        orm_mode = True


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: str
