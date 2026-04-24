from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import shutil, os, uuid, json
from database import get_db
from middleware.auth import get_current_user

router = APIRouter()

# =========================
# 🔥 UPLOAD DIR (FIXED)
# =========================
UPLOAD_DIR = "static/uploads"
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
    variants: str = Form("[]"),
    image: UploadFile = File(None),
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    cur = db.cursor()

    try:
        image_path = None

        # ================= IMAGE UPLOAD FIX =================
        if image:
            ext = image.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                shutil.copyfileobj(image.file, f)

            # 🔥 STORE ONLY RELATIVE PATH (IMPORTANT FIX)
            image_path = f"{filename}"

        # ================= INSERT PRODUCT =================
        cur.execute("""
            INSERT INTO products
            (name, price, category, description, image, user_id)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (name, price, category, description, image_path, user["id"]))

        product_id = cur.lastrowid

        # ================= VARIANTS SAFE PARSE =================
        try:
            variants_data = json.loads(variants)
        except:
            variants_data = []

        for v in variants_data:
            cur.execute("""
                INSERT INTO variants(product_id, qty, unit, price)
                VALUES (%s,%s,%s,%s)
            """, (
                product_id,
                v.get("qty", 0),
                v.get("unit", "kg"),
                v.get("price", price)
            ))

        db.commit()
        return {"msg": "Product added successfully"}

    except Exception as e:
        db.rollback()
        print("❌ ADD PRODUCT ERROR:", e)
        raise HTTPException(status_code=500, detail="Error adding product")


# =========================
# ✅ GET ALL PRODUCTS
# =========================
@router.get("/products")
def get_products(db=Depends(get_db)):
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT p.*,
                   u.id AS farmer_id,
                   u.name AS farmer_name,
                   u.location
            FROM products p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.id DESC
        """)

        products = cur.fetchall()

        # ================= VARIANTS =================
        for p in products:
            cur2 = db.cursor(dictionary=True)
            cur2.execute("""
                SELECT qty, unit, price
                FROM variants
                WHERE product_id=%s
            """, (p["id"],))
            p["variants"] = cur2.fetchall()

        return products

    except Exception as e:
        print("❌ GET PRODUCTS ERROR:", e)
        raise HTTPException(status_code=500, detail="Error fetching products")


# =========================
# ✅ GET SINGLE PRODUCT
# =========================
@router.get("/products/{id}")
def get_product(id: int, db=Depends(get_db)):
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT p.*,
                   u.id AS farmer_id,
                   u.name AS farmer_name,
                   u.location
            FROM products p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id=%s
        """, (id,))

        product = cur.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        cur2 = db.cursor(dictionary=True)
        cur2.execute("""
            SELECT qty, unit, price
            FROM variants
            WHERE product_id=%s
        """, (id,))

        product["variants"] = cur2.fetchall()

        return product

    except Exception as e:
        print("❌ GET PRODUCT ERROR:", e)
        raise HTTPException(status_code=500, detail="Error fetching product")


# =========================
# ✅ DELETE PRODUCT (FIXED IMAGE PATH)
# =========================
@router.delete("/products/{id}")
def delete_product(id: int, db=Depends(get_db)):
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("SELECT image FROM products WHERE id=%s", (id,))
        product = cur.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Not found")

        # 🔥 FIX IMAGE DELETE PATH
        if product.get("image"):
            file_path = os.path.join(UPLOAD_DIR, product["image"])
            if os.path.exists(file_path):
                os.remove(file_path)

        cur.execute("DELETE FROM variants WHERE product_id=%s", (id,))
        cur.execute("DELETE FROM products WHERE id=%s", (id,))

        db.commit()
        return {"msg": "Product deleted successfully"}

    except Exception as e:
        db.rollback()
        print("❌ DELETE ERROR:", e)
        raise HTTPException(status_code=500, detail="Error deleting product")


# =========================
# ⭐ ADD REVIEW
# =========================
@router.post("/reviews")
def add_review(data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    cur = db.cursor()

    try:
        if not data.get("product_id") or not data.get("rating"):
            raise HTTPException(status_code=400, detail="Missing fields")

        if int(data["rating"]) < 1 or int(data["rating"]) > 5:
            raise HTTPException(status_code=400, detail="Rating must be 1-5")

        cur.execute("""
            INSERT INTO reviews (product_id, user_id, rating, comment)
            VALUES (%s,%s,%s,%s)
        """, (
            data["product_id"],
            user["id"],
            data["rating"],
            data.get("comment", "")
        ))

        db.commit()
        return {"msg": "Review added"}

    except Exception as e:
        db.rollback()
        print("❌ REVIEW ERROR:", e)
        raise HTTPException(status_code=500, detail="Error adding review")


# =========================
# ⭐ GET REVIEWS
# =========================
@router.get("/reviews/{product_id}")
def get_reviews(product_id: int, db=Depends(get_db)):
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

        return cur.fetchall()

    except Exception as e:
        print("❌ GET REVIEWS ERROR:", e)
        raise HTTPException(status_code=500, detail="Error fetching reviews")

