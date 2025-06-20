from models.message import *
from routes.__init__ import * 
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
router = APIRouter(prefix=PREFIX)


"""
returns all messages sent to a user.
"""
@router.get("/message/all", response_model=List[MessagePreview])
async def get_all_messages(session_validate: UserSessionValidate, session=Depends(get_session)):

    print("session_validaite_obj", session_validate.model_dump())

    user: User = validate_user_by_hash(session_validate=session_validate, session=session)
    msgs: List[Message] = user.messages_received
    return [msg.preview() for msg in msgs]


@router.post("/message/send")
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


@router.get("/message/{message_id}/read")
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


@router.post("/message/{message_id}/answer")
async def answer_message(message_id: int, answer: str, session_validate: UserSessionValidate, background_tasks: BackgroundTasks, session: Session=Depends(get_session), ):
    user: User = validate_user_by_hash(session_validate=session_validate, session=session)
    message: Message = get_received_message_by_id(user_id=user.id, message_id=message_id, session=session)

    # if the user answers correctly, the original message gets relayed
    # otherwise, you get gibberish.

    body = message.decrypt(answer)
    background_tasks.add_task(delete_message_by_id, message_id=message_id, session=session)
    return JSONResponse(content=body)