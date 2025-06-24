from models.user_session import *
from routes.__init__ import * 
from fastapi import APIRouter
router = APIRouter(prefix=PREFIX)

"""
mwsd doesn't do logins - it creates a session key for the user that 
must be grabbed by the local machine and stored somewhere. 
"""
@router.post("/session/create", response_model=UserSessionRead)
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
Refresh a token by supplying the existing session hash / username 
renames the session and extends it by an hour from the request
"""
@router.post("/session/refresh/{session_hash}", response_model=UserSessionRead)
async def refresh_session(session_hash: str, username: str, session: Session=Depends(get_session)):

    session_validate = UserSessionValidate(
        username=username,
        session_hash=session_hash
    )

    refreshed : UserSession = refresh_user_session(session_validate=session_validate, session=session)
    return UserSessionRead(
        user_id=refreshed.id,
        username=refreshed.user.username,
        session_hash=refreshed.session_hash,
        expires_on=refreshed.expires_on
    ).model_dump()


"""
Extends the user session by the configured server time in env.py
"""
@router.patch("/session/extend/{session_hash}", response_model=UserSessionRead)
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
@router.delete("/session/terminate/{session_hash}")
async def terminate_user_session(session_hash: str, username: str, session: Session = Depends(get_session)):

    session_validate = UserSessionValidate(
        username=username,
        session_hash=session_hash
    )

    delete_user_session(session_validate, session)

    return JSONResponse(
        content="successfully revoked user session.",
        status_code=status.HTTP_200_OK
    )
