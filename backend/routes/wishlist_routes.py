from fastapi import APIRouter, Depends
from database import get_db
from middleware.auth import get_current_user

router = APIRouter()

# ❤️ GET WISHLIST (FIXED WITH JOIN)
@router.get("/wishlist")
def get_wishlist(user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    query = """
    SELECT 
        w.product_id,
        p.name,
        p.price,
        p.image
    FROM wishlist w
    JOIN products p ON w.product_id = p.id
    WHERE w.user_id = %s
    """

    cur.execute(query, (user["id"],))
    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "product_id": r[0],
            "name": r[1] if r[1] else "No Name",
            "price": float(r[2]) if r[2] else 0,
            "image": r[3] if r[3] else ""
        })

    cur.close()
    db.close()

    return result


# ❤️ ADD WISHLIST (PREVENT DUPLICATE)
@router.post("/wishlist/{product_id}")
def add_wishlist(product_id: int, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    # ✅ check already exists
    cur.execute("""
        SELECT * FROM wishlist 
        WHERE user_id=%s AND product_id=%s
    """, (user["id"], product_id))

    if cur.fetchone():
        return {"msg": "Already in wishlist ❤️"}

    cur.execute("""
        INSERT INTO wishlist(user_id, product_id)
        VALUES(%s,%s)
    """, (user["id"], product_id))

    db.commit()

    cur.close()
    db.close()

    return {"msg": "Added ❤️"}


# ❌ REMOVE WISHLIST
@router.delete("/wishlist/{product_id}")
def remove_wishlist(product_id: int, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        DELETE FROM wishlist 
        WHERE user_id=%s AND product_id=%s
    """, (user["id"], product_id))

    db.commit()

    cur.close()
    db.close()

    return {"msg": "Removed ❌"}