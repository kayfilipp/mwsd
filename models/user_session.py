from models.base import *
from models.user import *
import ksuid
import os 

STANDARD_EXPIRES_IN_HRS = int(os.getenv("STANDARD_EXPIRES_IN_HRS"))
STANDARD_EXTENSION_HRS = int(os.getenv("STANDARD_EXTENSION_HRS"))


def default_session_expiration_factory():
    return datetime.now() + timedelta(hours=STANDARD_EXPIRES_IN_HRS)

def session_hash_factory():
    return ksuid.ksuid().__str__()

class UserSessionBase(SQLModel):

    session_hash: str = Field(default_factory=session_hash_factory, nullable=False)
    expires_on: Optional[datetime] = Field(default_factory=default_session_expiration_factory, nullable=True)

class UserSessionRead(SQLModel):
    user_id: int 
    username: str
    session_hash: str 
    expires_on: datetime

class UserSession(Base, UserSessionBase, table=True):
    __tablename__ = "user_session"

    user_id: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("users.id", ondelete="CASCADE"), 
            unique=True
        )
    )
    user: "User" = Relationship(sa_relationship_kwargs={"lazy": "joined"})

    def extend(self):
        self.expires_on += timedelta(hours=STANDARD_EXTENSION_HRS)

    @property 
    def as_read(self):
        return UserSessionRead(
            user_id=self.user_id,
            username=self.user.username,
            session_hash=self.session_hash,
            expires_on=self.expires_on
        )

class UserSessionValidate(SQLModel):
    username: str
    session_hash: str

