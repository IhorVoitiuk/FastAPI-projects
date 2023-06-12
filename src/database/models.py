import enum

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Date,
    DateTime,
    func,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Role(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    birthday = Column(Date)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="documents")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    avatar = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column('role', Enum(Role), default=Role.user)
