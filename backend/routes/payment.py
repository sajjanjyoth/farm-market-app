from fastapi import APIRouter, HTTPException
import razorpay
from config import RAZORPAY_KEY, RAZORPAY_SECRET
from database import get_cursor

router = APIRouter()

# =========================
# 💳 RAZORPAY CLIENT
# =========================
client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))


# =====================================================
# 🎟️ CREATE COUPON
# =====================================================
@router.post("/coupons")
def create_coupon(data: dict):
    cursor, db = get_cursor()

    code = data.get("code")
    discount = data.get("discount")

    if not code or not discount:
        raise HTTPException(status_code=400, detail="Invalid coupon data")

    cursor.execute(
        "INSERT INTO coupons(code, discount) VALUES (%s,%s)",
        (code, discount)
    )
    db.commit()

    return {"message": "Coupon added successfully"}


# =====================================================
# 📄 GET ALL COUPONS
# =====================================================
@router.get("/coupons")
def get_coupons():
    cursor, _ = get_cursor()
    cursor.execute("SELECT * FROM coupons")
    return cursor.fetchall()


# =====================================================
# ❌ DELETE COUPON
# =====================================================
@router.delete("/coupons/{id}")
def delete_coupon(id: int):
    cursor, db = get_cursor()

    cursor.execute("DELETE FROM coupons WHERE id=%s", (id,))
    db.commit()

    return {"message": "Coupon deleted"}


# =====================================================
# 💳 CREATE RAZORPAY ORDER
# =====================================================
@router.post("/create-payment")
def create_payment(data: dict):
    try:
        amount = float(data.get("amount", 0))

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")

        order = client.order.create({
            "amount": int(amount * 100),  # paise
            "currency": "INR",
            "payment_capture": 1
        })

        return order

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ✅ VERIFY PAYMENT (IMPORTANT)
# =====================================================
@router.post("/verify-payment")
def verify_payment(data: dict):
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature")
        })

        return {"status": "Payment Verified ✅"}

    except Exception:
        raise HTTPException(status_code=400, detail="Payment verification failed ❌")