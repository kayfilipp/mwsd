import requests as r
from typing import Annotated, Optional, List
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from datetime import datetime, timedelta
from sqlalchemy import String, Column, Integer, ForeignKey
from dotenv import load_dotenv
from sqlalchemy.orm import relationship
import os 

load_dotenv()