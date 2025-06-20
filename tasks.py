from celery import Celery
from celery.schedules import crontab
import os 
from dotenv import load_dotenv
import requests as r 
from util.user import engine, generate_random_burner
from sqlalchemy import delete 
from sqlmodel import Session
from models.user import User
from models.user_session import UserSession 
from models.message import Message
from datetime import datetime, timedelta 
from util import gibberish

load_dotenv()

FAPI_URL = os.getenv('APP_URL')
app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):

    # testing suite - do not deploy in prod.
    # sender.add_periodic_task(20.0, create_burner.s(), name='Bother FastAPI')

    # production suite 
    sender.add_periodic_task(10.0, nuke_expired_users.s(), name='Nuke Expired Users')
    sender.add_periodic_task(10.0, nuke_expired_sessions.s(), name='Nuke Expired Sessions')

@app.task
def create_burner():
    burner = {
        "username": gibberish.create(8),
        "password": gibberish.create(8),
        "expires_on_timestamp": str(datetime.now() + timedelta(minutes=1))
    }

    burner = generate_random_burner(1)
    create_burner = r.post(os.getenv("APP_URL")+"/user/register", json=burner)
    print(f"generated burner with status code; {create_burner.status_code}")


@app.task 
def nuke_expired_users():
    session=Session(engine)
    session.exec(delete(User).where(User.expires_on_timestamp <= datetime.now()))
    session.commit()

@app.task 
def nuke_expired_sessions():
    session=Session(engine)
    session.exec(delete(UserSession).where(UserSession.expires_on <= datetime.now()))
    session.commit()

@app.task 
def nuke_expired_messages():
    session=Session(engine)
    session.exec(delete(Message).where(UserSession.expires_on <= datetime.now()))
    session.commit()
