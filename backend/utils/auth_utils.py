from fastapi import Header, HTTPException

# Dummy user (for now)
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")

    # In real project → decode JWT
    return {"id": 1}  # temporary user id