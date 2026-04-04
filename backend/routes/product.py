from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import shutil, os, uuid
from database import get_db
from middleware.auth import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# ✅ ADD PRODUCT
# =========================
@router.post("/products")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    description: str = Form(""),
    image: UploadFile = File(...),
    user=Depends(get_current_user)
):
    db = get_db()
    cur = db.cursor()

    try:
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        cur.execute("""
            INSERT INTO products(name, price, category, description, image, user_id)
            VALUES(%s,%s,%s,%s,%s,%s)
        """, (name, price, category, description, "/uploads/" + filename, user["id"]))

        db.commit()

        return {"msg": "Product added successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ✅ GET ALL PRODUCTS
# =========================
@router.get("/products")
def get_products():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    for p in products:
        cur.execute("""
            SELECT qty, unit, price 
            FROM variants 
            WHERE product_id=%s
        """, (p["id"],))
        p["variants"] = cur.fetchall()

    return products


# =========================
# ✅ GET SINGLE PRODUCT
# =========================
@router.get("/products/{id}")
def get_product(id: int):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT id, name, price, category, description, image
        FROM products
        WHERE id=%s
    """, (id,))
    
    product = cur.fetchone()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cur.execute("""
        SELECT qty, unit, price 
        FROM variants 
        WHERE product_id=%s
    """, (id,))
    
    product["variants"] = cur.fetchall()

    return product


# =========================
# ✅ DELETE PRODUCT
# =========================
@router.delete("/products/{id}")
def delete_product(id: int):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    db.commit()

    return {"msg": "Product deleted successfully"}


# =========================
# ⭐ ADD REVIEW
# =========================
@router.post("/reviews")
def add_review(data: dict):
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("""
            INSERT INTO reviews (product_id, user_id, rating, comment)
            VALUES (%s,%s,%s,%s)
        """, (
            data["product_id"],
            data.get("user_id", 1),  # fallback if not sent
            data["rating"],
            data["comment"]
        ))

        db.commit()
        return {"msg": "Review added"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ⭐ GET REVIEWS (FIXED)
# =========================
@router.get("/reviews/{product_id}")
def get_reviews(product_id: int):
    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT r.id, r.rating, r.comment, r.user_id,
                   u.name AS username
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.product_id = %s
            ORDER BY r.id DESC
        """, (product_id,))

        data = cur.fetchall()

        return data if data else []

    except Exception as e:
        print("ERROR:", e)
        return []