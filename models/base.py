# we can dump all the packages we need for other models in here 
from models.__init__ import *  


class Base(SQLModel):

    __tablename__ = NotImplemented
    __apiname__ = NotImplemented

    id : int = Field(primary_key=True, default=None)
    created_by_id: int = Field(default=0) # 0 = system
    created_timestamp: datetime = Field(default_factory=datetime.now)
    updated_by_id: int = Field(default=None, nullable=True)
    updated_timestamp: datetime = Field(default_factory=datetime.now)
