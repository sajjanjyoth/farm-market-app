from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from middleware.auth import get_current_user

router = APIRouter()

router = APIRouter(prefix="/admin")

@router.get("/stats")
def stats():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    p = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    o = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    u = cursor.fetchone()[0]

    return {
        "products": p,
        "orders": o,
        "users": u
    }
# 📊 ADMIN ANALYTICS
@router.get("/admin/stats")
def admin_stats(user=Depends(get_current_user)):

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # total products
    cur.execute("SELECT COUNT(*) as count FROM products")
    products = cur.fetchone()["count"]

    # total users
    cur.execute("SELECT COUNT(*) as count FROM users")
    users = cur.fetchone()["count"]

    # total orders + revenue
    cur.execute("SELECT COUNT(*) as orders, SUM(total) as revenue FROM orders")
    order_data = cur.fetchone()

    orders = order_data["orders"] or 0
    revenue = order_data["revenue"] or 0

    return {
        "products": products,
        "users": users,
        "orders": orders,
        "revenue": revenue
    }