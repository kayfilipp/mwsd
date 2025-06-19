from util.__init__ import * 
from models.message import Message 
from models.user import User 

def get_received_message_by_id(user_id: int, message_id: int, session: Session):

    message = session.exec(
        select(Message) 
        .join(User, User.id == Message.to_user_id) 
        .where(
            Message.id==message_id,
            User.id==user_id
        )
    )
    msg = message.scalars().first()

    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"received message with id {message_id} not found for current user."
        )
    
    return msg 

def delete_message_by_id(message_id: int, session=Depends(get_session)):
    message = session.scalars(select(Message).where(Message.id==message_id)).first()

    if not message:
        return

    session.delete(message)
    session.commit()