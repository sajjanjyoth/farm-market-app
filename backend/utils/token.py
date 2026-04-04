from jose import jwt, JWTError

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# ✅ CREATE TOKEN
def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ✅ VERIFY TOKEN
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None