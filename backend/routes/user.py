from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from utils.hash import hash_password, verify_password
from utils.token import create_token
from middleware.auth import get_current_user

router = APIRouter()

# =========================
# ✅ REGISTER
# =========================
@router.post("/register")
def register(user: dict):
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Check email exists
    cur.execute("SELECT id FROM users WHERE email=%s", (user["email"],))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user["password"])

    cur.execute(
        "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,%s)",
        (user["name"], user["email"], hashed, user.get("role", "customer"))
    )

    db.commit()
    cur.close()
    db.close()

    return {"message": "Registered successfully"}


# =========================
# ✅ LOGIN
# =========================
@router.post("/login")
def login(user: dict):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE email=%s", (user["email"],))
    data = cur.fetchone()

    cur.close()
    db.close()

    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user["password"], data["password"]):
        raise HTTPException(status_code=401, detail="Wrong password")

    # ✅ CREATE TOKEN
    token = create_token({
        "id": data["id"],
        "role": data["role"]
    })

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": data["id"],
            "name": data["name"],
            "role": data["role"]
        }
    }


# =========================
# ✅ GET USERS (ADMIN)
# =========================
@router.get("/users")
def get_users(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT id,name,email,role FROM users")
    users = cur.fetchall()

    cur.close()
    db.close()

    return users


# =========================
# ✅ PROFILE
# =========================
@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT id, name, email, role, image FROM users WHERE id=%s",
        (user["id"],)
    )

    data = cur.fetchone()

    cur.close()
    db.close()

    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    return data