from util.__init__ import *
from util.pwd import *
from models.user import User, UserLogin
from models.user_session import UserSession, UserSessionValidate

def refresh_user_session(session_validate: UserSessionValidate, session: Session) -> UserSession:

    result = session.exec(
        select(UserSession) 
        .join(User, User.id == UserSession.user_id) 
        .where(
            UserSession.session_hash == session_validate.session_hash,
            User.username == session_validate.username  
        )
    )
    user_session: UserSession = result.scalars().first()

    if not user_session:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user session cannot be authenticated."
        )
    
    user_session.rename()
    user_session.extend()

    session.add(user_session)
    session.commit()
    session.refresh(user_session)

    return user_session
    


def get_user_by_username(username: str, session: Session = Depends(get_session)):
    result = session.exec(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="username not found."
        )

    return user 

def delete_user_session(session_validate: UserSessionValidate, session: Session):
    result = session.exec(
        select(UserSession) 
        .join(User, User.id == UserSession.user_id) 
        .where(
            UserSession.session_hash == session_validate.session_hash,
            User.username == session_validate.username  
        )
    )
    user_session = result.scalars().first()

    if not user_session:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user session cannot be authenticated."
        )

    session.delete(user_session)
    session.commit()

def validate_user_by_hash(session_validate: UserSessionValidate ,session: Session):

    result = session.exec(
        select(User) 
        .join(UserSession, User.id == UserSession.user_id) 
        .where(
            UserSession.session_hash == session_validate.session_hash,
            User.username == session_validate.username  
        )
    )
    user = result.scalars().first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user cannot be authenticated via hash."
        )

    return user 

async def get_current_user(userLogin: UserLogin, session: Session = Depends(get_session)):

    user = get_user_by_username(userLogin.username, session)

    if not verify_password(userLogin.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return user

"""
Check if this agent is submitting a session key that 
1. belongs to the proper username AND 
2. hasn't expired yet
"""
def get_user_session_by_hash(user: User, session_hash: str, session: Session):
    user_session: UserSession = session.scalars(select(UserSession).where(
        UserSession.user_id==user.id,
        UserSession.session_hash==session_hash
    ))\
    .first()

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Session doesn't exist or expired."
            }
        )
    
    return user_session
    
"""
Check if a user has any open sessions at all 
"""
def user_has_open_session(user: User, session: Session) -> bool:
    user_session: UserSession = session.scalars(select(UserSession).where(
        UserSession.user_id==user.id
    ))\
    .first()

    return (user_session is not None)
