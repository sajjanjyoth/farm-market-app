from fastapi import APIRouter, Depends
from database import get_db
from middleware.auth import get_current_user

router = APIRouter()

# 💬 SEND MESSAGE
@router.post("/chat")
def send_message(data: dict, user=Depends(get_current_user)):

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO messages(sender_id, receiver_id, message)
        VALUES(%s,%s,%s)
    """, (user["id"], data["receiver_id"], data["message"]))

    # 🔔 create notification
    cur.execute("""
        INSERT INTO notifications(user_id, message)
        VALUES(%s,%s)
    """, (data["receiver_id"], "New message received 💬"))

    db.commit()
    cur.close()
    db.close()

    return {"msg": "sent"}
    

# 📥 GET CHAT
@router.get("/chat/{user_id}")
def get_chat(user_id: int, user=Depends(get_current_user)):

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM messages
        WHERE (sender_id=%s AND receiver_id=%s)
        OR (sender_id=%s AND receiver_id=%s)
        ORDER BY created_at
    """, (user["id"], user_id, user_id, user["id"]))

    data = cur.fetchall()

    cur.close()
    db.close()

    return data


# 🔔 GET NOTIFICATIONS
@router.get("/notifications")
def get_notifications(user=Depends(get_current_user)):

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY id DESC", (user["id"],))
    data = cur.fetchall()

    cur.close()
    db.close()

    return data


# ✅ MARK READ
@router.put("/notifications/read/{id}")
def read_notification(id:int, user=Depends(get_current_user)):

    db = get_db()
    cur = db.cursor()

    cur.execute("UPDATE notifications SET is_read=1 WHERE id=%s", (id,))
    db.commit()

    cur.close()
    db.close()

    return {"msg":"updated"}