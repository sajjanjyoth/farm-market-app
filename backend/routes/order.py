from fastapi import APIRouter, Depends, HTTPException
from database import get_cursor
from middleware.auth import get_current_user

router = APIRouter()


# =====================================================
# 📦 CREATE ORDER
# =====================================================
@router.post("/orders")
def create_order(data: dict, user=Depends(get_current_user)):
    cursor, db = get_cursor()

    items = data.get("items")

    if not items:
        raise HTTPException(status_code=400, detail="Items required")

    total = 0
    farmer_id = None

    for item in items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)

        if not product_id:
            raise HTTPException(400, "Missing product_id")

        if quantity <= 0:
            raise HTTPException(400, "Invalid quantity")

        cursor.execute(
            "SELECT price, user_id FROM products WHERE id=%s",
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            raise HTTPException(404, f"Product not found: {product_id}")

        total += product["price"] * quantity
        farmer_id = product["user_id"]
        print("DATA RECEIVED:", data)
    # INSERT ORDER
    cursor.execute("""
        INSERT INTO orders (user_id, total, status, payment_status)
        VALUES (%s, %s, %s, %s)
    """, (
        user["id"],
        total,
        "Pending",
        data.get("payment_status", "Paid")
    ))

    order_id = cursor.lastrowid

    # INSERT ITEMS
    for item in items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (
            order_id,
            item["product_id"],
            item["quantity"]
        ))

    db.commit()

    return {"message": "Order placed successfully", "order_id": order_id}


# =====================================================
# 📄 GET ALL ORDERS
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
            SELECT p.id AS product_id, p.name, p.image, oi.quantity
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
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
        SELECT p.id AS product_id, p.name, p.image, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id=%s
    """, (order_id,))

    order["items"] = cursor.fetchall()

    return order


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

    if order["status"] in ["Shipped", "Delivered", "Cancelled"]:
        raise HTTPException(400, "Cannot cancel this order")

    cursor.execute("""
        UPDATE orders
        SET status='Cancelled'
        WHERE id=%s
    """, (order_id,))

    db.commit()

    return {"message": "Order cancelled successfully"}