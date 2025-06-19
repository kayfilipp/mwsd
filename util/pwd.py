import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()  # Generate a salt
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)  # Hash password
    return hashed.decode("utf-8")  # Convert bytes to string for storage

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))