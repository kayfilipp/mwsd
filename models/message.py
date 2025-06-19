from models.base import *
from util import gibberish

STANDARD_EXPIRES_IN = int(os.getenv("STANDARD_MESSAGE_EXPIRES_IN_HRS"))

def default_expiration_factory():
    return datetime.now() + timedelta(hours=STANDARD_EXPIRES_IN)

class MessagePreview(SQLModel):
    id: int = Field(nullable=False)
    from_username: str = Field(nullable=False)
    to_username: str = Field(nullable=False)
    sent_on: datetime = Field(nullable=False)
    expires_on: datetime = Field(nullable=False)
    is_locked: bool = Field(nullable=False)
    statement: Optional[str] = Field(default=None)

class MessageBase(SQLModel):
    body: str = Field(sa_column=Column(String, nullable=False))
    statement: str = Field(default=None, nullable=True)
    answer: str = Field(default=None, nullable=True)
    expires_on: datetime = Field(default_factory=default_expiration_factory, nullable=False)

class Message(Base, MessageBase, table=True):
    __tablename__ = "message"
    
    """
    Allow for burner accounts to send messages that persist after the burner is deleted.
    If the target deletes their account, we can delete the message.
    """
    from_user_id: Optional[int] = Field(nullable=True, foreign_key="users.id")
    to_user_id: int = Field(
        sa_column=Column(
            Integer, 
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False
        )
    )

    # Define relationships using string references
    from_user: Optional["User"] = Relationship(
        back_populates="messages_sent",
        sa_relationship_kwargs={"foreign_keys": "Message.from_user_id"}
    )
    to_user: "User" = Relationship(
        back_populates="messages_received",
        sa_relationship_kwargs={"foreign_keys": "Message.to_user_id"}
    )

    def preview(self) -> MessagePreview:
        return MessagePreview(
            id=self.id,
            from_username=self.from_user.username,
            to_username=self.to_user.username,
            sent_on=self.created_timestamp,
            expires_on=self.expires_on,
            is_locked=self.statement is not None,
            statement=self.statement
        )
    
    def decrypt(self, answer) -> str:
        # if we try to decrypt a message with no answer, 
        # just return the body.
        if self.answer == answer or not self.answer:
            return self.body 
        
        return gibberish.create(20)
    
    @property 
    def has_passphrase(self):
        return self.statement is not None

class MessageCreate(SQLModel):
    to_username: str
    body: str
    statement: Optional[str] = None
    answer: Optional[str] = None
    expires_on: Optional[datetime] = None