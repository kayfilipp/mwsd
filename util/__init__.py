from db import engine
from sqlalchemy import select, and_
from fastapi import HTTPException, status, Depends 
from datetime import datetime
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session