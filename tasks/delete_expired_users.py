from tasks.__init__ import *

session=Session(engine)
session.exec(delete(User).where(User.expires_on_timestamp <= datetime.now()))
session.commit()