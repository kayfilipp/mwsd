from models.base import *
from models.message import Message
from typing import List 

def default_user_expires_on_factory():
    return datetime.now() + timedelta(days=7)


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    password_hash: str = Field(sa_column=Column(String, nullable=False))
    discoverable: bool = Field(default=False)
    expires_on_timestamp: Optional[datetime] = Field(default=None, nullable=True)


class User(UserBase, Base, table=True):
    __tablename__ = "users"

    messages_sent: List["Message"] = Relationship(
        back_populates="from_user",
        sa_relationship_kwargs={"foreign_keys": "Message.from_user_id", "lazy": "select"}
    )
    messages_received: List["Message"] = Relationship(
        back_populates="to_user",
        sa_relationship_kwargs={"foreign_keys": "Message.to_user_id", "lazy": "select"}
    )

class UserLogin(SQLModel):
    username: str
    password: str

class UserCreate(SQLModel):
    username: str
    password: str
    discoverable: Optional[bool] = None
    expires_on_timestamp: Optional[datetime] = None

class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    discoverable: Optional[bool] = None

class UserRead(SQLModel):
    username: str

class UserAbout(SQLModel):
    id: int
    username: str 
    discoverable: bool 
    expires_on_timestamp: Optional[datetime] = None      
    created_timestamp: datetime 