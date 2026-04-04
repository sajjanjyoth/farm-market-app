from fastapi import APIRouter, Depends
from services.farmer_service import get_farmers
from middleware.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/farmer")

@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor(dictionary=True)

    user_id = user["id"]

    # ✅ PROFILE DATA
    cur.execute("""
        SELECT name, lastname, email, phone, address,
               farm_name AS farmName,
               profile_image AS profileImage,
               qr_code AS qrCode
        FROM users
        WHERE id=%s
    """, (user_id,))
    profile = cur.fetchone() or {}

    # =========================
    # 📦 PRODUCTS SOLD
    # =========================
    cur.execute("""
        SELECT SUM(oi.quantity) AS sold
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE p.farmer_id = %s
    """, (user_id,))
    sold = cur.fetchone()["sold"] or 0

    # =========================
    # 💰 TOTAL REVENUE
    # =========================
    cur.execute("""
        SELECT SUM(oi.quantity * oi.price) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE p.farmer_id = %s
    """, (user_id,))
    revenue = cur.fetchone()["revenue"] or 0

    # =========================
    # 📋 PENDING ORDERS
    # =========================
    cur.execute("""
        SELECT COUNT(*) AS pending
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE p.farmer_id = %s AND o.status = 'pending'
    """, (user_id,))
    pending = cur.fetchone()["pending"] or 0

    cur.close()
    db.close()

    # ✅ MERGE ALL DATA
    profile["productsSold"] = sold
    profile["totalRevenue"] = revenue
    profile["pendingOrders"] = pending

    return profile

@router.get("/farmers")
def fetch_farmers():
    return get_farmers()

@router.get("/farmer/orders")
def get_farmer_orders(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "farmer":
        raise HTTPException(status_code=403, detail="Not authorized")

    orders = db.query(Order).filter(Order.farmer_id == current_user["id"]).all()

    return 
    
@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    return current_user