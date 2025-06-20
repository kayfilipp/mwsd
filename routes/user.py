from models.user import *
from routes.__init__ import * 
from fastapi import APIRouter
router = APIRouter(prefix=PREFIX)


"""
Registering a user lets someone create a new user.
These users can be throaway / burner users that expire 
or users that are permanently on the platform.
"""
@router.post("/user/register", response_model=UserAbout)
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
@router.get("/user/about", response_model=UserAbout)
async def get_user_data(user: User=Depends(get_current_user), session=Depends(get_session)):

    user=session.exec(select(User).where(
        User.username==user.username
    )).first()

    return user


# lets a user delete their account early.
@router.delete("/user/delete")
async def delete_user(user: User=Depends(get_current_user), session=Depends(get_session)):
    session.delete(user)
    session.commit()

    return JSONResponse(
        content=f"successfully deleted user {user.username}",
        status_code=status.HTTP_200_OK
    )
