from fastapi import APIRouter, Depends, HTTPException
from database import get_cursor
from middleware.auth import get_current_user

router = APIRouter()

VALID_STATUS = ["pending", "accepted", "shipped", "out for delivery", "delivered", "cancelled"]

# =====================================================
# 📦 CREATE ORDER
# =====================================================
@router.post("/orders")
def create_order(data: dict, user=Depends(get_current_user)):
    cursor, db = get_cursor()

    items = data.get("items")
    if not items:
        raise HTTPException(400, "Items required")

    total = 0

    # CALCULATE TOTAL
    for item in items:
        product_id = item.get("product_id")
        qty = item.get("quantity", 0)

        if not product_id or qty <= 0:
            raise HTTPException(400, "Invalid item")

        cursor.execute(
            "SELECT name, price FROM products WHERE id=%s",
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            raise HTTPException(404, "Product not found")

        total += product["price"] * qty

    # INSERT ORDER
    cursor.execute("""
        INSERT INTO orders (user_id, total, status, payment_status)
        VALUES (%s, %s, %s, %s)
    """, (
        user["id"],
        total,
        "pending",
        data.get("payment_status", "paid")
    ))

    order_id = cursor.lastrowid

    # INSERT ITEMS
    for item in items:
        cursor.execute(
            "SELECT name, price FROM products WHERE id=%s",
            (item["product_id"],)
        )
        product = cursor.fetchone()

        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, name, quantity, price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            order_id,
            item["product_id"],
            product["name"],
            item["quantity"],
            product["price"]
        ))

    db.commit()

    return {"message": "Order placed successfully", "order_id": order_id}


# =====================================================
# 📄 GET USER ORDERS
# =====================================================
@router.get("/orders")
def get_orders(user=Depends(get_current_user)):
    cursor, _ = get_cursor()

    cursor.execute("""
        SELECT * FROM orders
        WHERE user_id=%s
        ORDER BY id DESC
    """, (user["id"],))

    orders = cursor.fetchall()

    for order in orders:
        cursor.execute("""
            SELECT 
                oi.product_id,
                oi.name,
                oi.quantity,
                oi.price,
                p.image
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id=%s
        """, (order["id"],))

        order["items"] = cursor.fetchall()

    return orders


# =====================================================
# 📄 GET ALL ORDERS (ADMIN)
# =====================================================
@router.get("/admin/orders")
def get_all_orders(user=Depends(get_current_user)):
    cursor, _ = get_cursor()

    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()

    for order in orders:
        cursor.execute("""
            SELECT 
                oi.product_id,
                oi.name,
                oi.quantity,
                oi.price,
                p.image
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id=%s
        """, (order["id"],))

        order["items"] = cursor.fetchall()

    return orders


# =====================================================
# 📄 GET SINGLE ORDER
# =====================================================
@router.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(get_current_user)):
    cursor, _ = get_cursor()

    cursor.execute("""
        SELECT * FROM orders
        WHERE id=%s AND user_id=%s
    """, (order_id, user["id"]))

    order = cursor.fetchone()

    if not order:
        raise HTTPException(404, "Order not found")

    cursor.execute("""
        SELECT 
            oi.product_id,
            oi.name,
            oi.quantity,
            oi.price,
            p.image
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id=%s
    """, (order_id,))

    order["items"] = cursor.fetchall()

    return order


# =====================================================
# 🔄 UPDATE ORDER (ADMIN)
# =====================================================
@router.put("/orders/{order_id}")
def update_order(order_id: int, data: dict, user=Depends(get_current_user)):
    cursor, db = get_cursor()

    if user.get("role") != "admin":
        raise HTTPException(403, "Only admin allowed")

    status = data.get("status")

    if status not in VALID_STATUS:
        raise HTTPException(400, "Invalid status")

    cursor.execute("SELECT id FROM orders WHERE id=%s", (order_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Order not found")

    cursor.execute("""
        UPDATE orders SET status=%s WHERE id=%s
    """, (status, order_id))

    db.commit()

    return {"message": "Order updated successfully"}


# =====================================================
# ❌ CANCEL ORDER
# =====================================================
@router.delete("/orders/{order_id}")
def cancel_order(order_id: int, user=Depends(get_current_user)):
    cursor, db = get_cursor()

    cursor.execute("""
        SELECT status FROM orders
        WHERE id=%s AND user_id=%s
    """, (order_id, user["id"]))

    order = cursor.fetchone()

    if not order:
        raise HTTPException(404, "Order not found")

    if order["status"] in ["shipped", "delivered", "cancelled"]:
        raise HTTPException(400, "Cannot cancel this order")

    cursor.execute("""
        UPDATE orders SET status='cancelled'
        WHERE id=%s
    """, (order_id,))

    db.commit()

    return {"message": "Order cancelled successfully"}