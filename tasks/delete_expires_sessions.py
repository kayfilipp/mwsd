from tasks.__init__ import * 

session=Session(engine)
session.exec(delete(UserSession).where(UserSession.expires_on <= datetime.now()))
session.commit()