from util.user import engine
from sqlalchemy import delete 
from sqlmodel import Session
from models.user import User
from models.user_session import UserSession 
from models.message import Message
from datetime import datetime, timedelta 
from util import gibberish
import sys

def delete_expired_assets():
    
    session=Session(engine)
    session.exec(delete(Message).where(UserSession.expires_on <= datetime.now()))
    session.commit()

    session.exec(delete(UserSession).where(UserSession.expires_on <= datetime.now()))
    session.commit()

    session.exec(delete(User).where(User.expires_on_timestamp <= datetime.now()))
    session.commit()


tasks = {
    "delete_expired_assets": delete_expired_assets
}

if __name__ == "__main__":
    args = sys.argv
    job = args[1]
    tasks[job]()