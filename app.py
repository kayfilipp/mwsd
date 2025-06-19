from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from util.user import *
from util.pwd import *
from util.message import *
from models.user import *
from models.message import *
from models.user_session import *
from models.message import * 
from fastapi import HTTPException, status

app = FastAPI()

@app.get("/")
async def root():
    return RedirectResponse("/docs")

"""
Registering a user lets someone create a new user.
These users can be throaway / burner users that expire 
or users that are permanently on the platform.
"""
@app.post("/user/register", response_model=UserAbout)
async def register_user(userCreate: UserCreate, session: Session = Depends(get_session)):

    user = session.exec(select(User).where(User.username == userCreate.username)).first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {userCreate.username} already exists."
        )

    user = User(
        username=userCreate.username,
        password_hash=hash_password(userCreate.password),
        discoverable=userCreate.discoverable,
        expires_on_timestamp=userCreate.expires_on_timestamp
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user 

"""
gives a user their username, creation date, discoverability, and expiration date.
"""
@app.get("/user/about", response_model=UserAbout)
async def get_user_data(user: User=Depends(get_current_user), session=Depends(get_session)):

    user=session.exec(select(User).where(
        User.username==user.username
    )).first()

    return user


# lets a user delete their account early.
@app.delete("/user/delete")
async def delete_user(user: User=Depends(get_current_user), session=Depends(get_session)):
    session.delete(user)
    session.commit()

    return JSONResponse(
        content=f"successfully deleted user {user.username}",
        status_code=status.HTTP_200_OK
    )


"""
mwsd doesn't do logins - it creates a session key for the user that 
must be grabbed by the local machine and stored somewhere. 
"""
@app.post("/session/create", response_model=UserSessionRead)
async def create_user_session(user: User=Depends(get_current_user), session=Depends(get_session)):

    # check if any user sessions currently exist that aren't expired 
    # throw a 409 if so.
    # otherwise, make a new sesh.
    user_has_session = user_has_open_session(user, session)

    if user_has_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={ "message": "session already exists for this user." }
        )

    user_session = UserSession(user_id=user.id)

    session.add(user_session)
    session.commit() 
    session.refresh(user_session)

    return user_session.as_read

"""
Extends the user session by the configured server time in env.py
"""
@app.patch("/session/extend/{session_hash}", response_model=UserSessionRead)
async def extend_user_session(session_hash: str, user: User=Depends(get_current_user), session: Session=Depends(get_session)):

    user_session: UserSession = get_user_session_by_hash(user=user, session_hash=session_hash, session=session)
    user_session.extend()

    session.add(user_session)
    session.commit()
    session.refresh(user_session)

    read = UserSessionRead(
        user_id=user_session.user_id,
        username=user_session.user.username,
        session_hash=user_session.session_hash,
        expires_on=user_session.expires_on
    )

    return read.model_dump()


"""
logs the user out of their session
"""
@app.delete("/session/terminate/{session_hash}")
async def terminate_user_session(session_hash: str, user: User=Depends(get_current_user), session: Session = Depends(get_session)):

    user_session = get_user_session_by_hash(user=user, session_hash=session_hash, session=session)
    session.delete(user_session)
    session.commit()

    return JSONResponse(
        content="successfully revoked user session.",
        status_code=status.HTTP_200_OK
    )


"""
returns all messages sent to a user.
"""
@app.get("/message/all", response_model=List[MessagePreview])
async def get_all_messages(session_validate: UserSessionValidate, session=Depends(get_session)):

    print("session_validaite_obj", session_validate.model_dump())

    user: User = validate_user_by_hash(session_validate=session_validate, session=session)
    msgs: List[Message] = user.messages_received
    return [msg.preview() for msg in msgs]


@app.post("/message/send")
async def send_message(
    message: MessageCreate, 
    session_validate: UserSessionValidate,
    session: Session=Depends(get_session)
):
    
    # validate that both users exist
    user: User = validate_user_by_hash(session_validate=session_validate, session=session)
    recepient: User = get_user_by_username(message.to_username, session)

    # create message object 
    message: Message = Message(
        body=message.body,
        statement=message.statement,
        answer=message.answer,
        expires_on=message.expires_on,
        from_user_id=user.id,
        to_user_id=recepient.id
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    preview = message.preview()
    return preview 


@app.get("/message/{message_id}/read")
async def read_message(message_id: int, session_validate: UserSessionValidate, background_tasks: BackgroundTasks, session: Session=Depends(get_session)):
    # reads message by id, but checks that it belongs to the user first.
    # if the message has a statement guarding it, return the statement
    # otherwise, return the content.
    user: User = validate_user_by_hash(session_validate=session_validate, session=session)
    message: Message = get_received_message_by_id(user_id=user.id, message_id=message_id, session=session)

    # if this is a message without a statement, delete it immediately
    # after sending it to the user.
    if not message.has_passphrase:
        background_tasks.add_task(delete_message_by_id, message_id=message.id, session=session)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=message.body
        )
    
    return JSONResponse(
        status_code=status.HTTP_423_LOCKED,
        content={
            "message_preview": message.preview(),
            "detail": "this message requires a password to be unlocked through the /message/{id}/answer endpoint"
        }
    )


@app.post("/message/{message_id}/answer")
async def answer_message(message_id: int, answer: str, session_validate: UserSessionValidate, background_tasks: BackgroundTasks, session: Session=Depends(get_session), ):
    user: User = validate_user_by_hash(session_validate=session_validate, session=session)
    message: Message = get_received_message_by_id(user_id=user.id, message_id=message_id, session=session)

    # if the user answers correctly, the original message gets relayed
    # otherwise, you get gibberish.

    body = message.decrypt(answer)
    background_tasks.add_task(delete_message_by_id, message_id=message_id, session=session)
    return JSONResponse(content=body)