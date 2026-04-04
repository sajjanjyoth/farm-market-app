from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.post("/update-location")
def update_location(data: dict):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "INSERT INTO order_tracking(order_id,latitude,longitude) VALUES(%s,%s,%s)",
        (data["order_id"], data["lat"], data["lng"])
    )
    db.commit()

    return {"message": "Updated"}

@router.get("/track/{order_id}")
def track(order_id:int):
    db=get_db();cur=db.cursor(dictionary=True)

    cur.execute("SELECT * FROM order_tracking WHERE order_id=%s ORDER BY id DESC LIMIT 1",(order_id,))
    return cur.fetchone()