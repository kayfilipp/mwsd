from sqlmodel import SQLModel, create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os

load_dotenv()


# Create pg Engine
pg_url = os.getenv("PG_URL")

engine = create_engine(pg_url)

if not database_exists(engine.url):
    create_database(engine.url)

# Create tables in the database
SQLModel.metadata.create_all(engine)
