from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from middleware.auth import get_current_user

router = APIRouter()

# ➕ ADD TO CART
@router.post("/cart")
def add_cart(data: dict, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "INSERT INTO cart(user_id, product_id, quantity) VALUES (%s,%s,%s)",
        (user["id"], data["product_id"], data.get("quantity", 1))
    )
    db.commit()

    return {"message": "Added to cart"}


# 📦 GET CART
@router.get("/cart")
def get_cart(user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor(dictionary=True)

    query = """
    SELECT 
        cart.id AS cart_id,
        cart.product_id,
        cart.quantity,
        products.name,
        products.price,
        products.image
    FROM cart
    JOIN products ON cart.product_id = products.id
    WHERE cart.user_id = %s
    """

    cur.execute(query, (user["id"],))
    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "cart_id": r["cart_id"],
            "product_id": r["product_id"],
            "quantity": r["quantity"],
            "name": r["name"] or "No Name",
            "price": float(r["price"]) if r["price"] else 0,
            "image": r["image"] or ""
        })

    return result


# 🔄 UPDATE QUANTITY
@router.put("/cart/{id}")
def update_cart(id: int, data: dict, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "UPDATE cart SET quantity=%s WHERE id=%s AND user_id=%s",
        (data["quantity"], id, user["id"])
    )
    db.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"msg": "updated"}


# ❌ DELETE ITEM
@router.delete("/cart/{id}")
def delete_cart(id: int, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "DELETE FROM cart WHERE id=%s AND user_id=%s",
        (id, user["id"])
    )
    db.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"msg": "deleted"}


# 🎟 COUPONS
@router.get("/coupons")
def get_coupons():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM coupons")
    return cur.fetchall()


@router.post("/coupons")
def add_coupon(data: dict):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "INSERT INTO coupons(code, discount) VALUES(%s,%s)",
        (data["code"], data["discount"])
    )
    db.commit()

    return {"msg": "added"}


@router.delete("/coupons/{id}")
def delete_coupon(id:int):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM coupons WHERE id=%s",(id,))
    db.commit()

    return {"msg":"deleted"}