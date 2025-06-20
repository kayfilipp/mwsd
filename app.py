from fastapi import FastAPI
from routes import base, message, user_session, user

app = FastAPI()

app.include_router(base.router)
app.include_router(user.router)
app.include_router(message.router)
app.include_router(user_session.router)
app.include_router(message.router)
