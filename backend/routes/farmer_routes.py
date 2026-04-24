from fastapi import APIRouter, Depends, HTTPException, Form
from middleware.auth import get_current_user
from database import get_db
from services.farmer_service import get_farmers

router = APIRouter(prefix="/farmer", tags=["Farmer"])


# =====================================
# 🤖 SIMPLE AI DESCRIPTION FUNCTION
# =====================================
def generate_ai_description(name, category):
    return f"""
{name} is a fresh and high-quality {category} product 🌱.
Naturally grown using safe farming practices.
Rich in nutrients and perfect for daily use.
Directly sourced from farmers to ensure freshness 🚜.
""".strip()


# =====================================
# 👤 CURRENT USER
# =====================================
@router.get("/me")
def get_me(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "role": user.get("role")
    }


# =====================================
# 👤 FARMER PROFILE
# =====================================
@router.get("/profile")
def get_profile(user=Depends(get_current_user)):

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        user_id = user["id"]

        cur.execute("""
            SELECT name, email, location AS address
            FROM users
            WHERE id=%s
        """, (user_id,))
        profile = cur.fetchone()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # SOLD
        cur.execute("""
            SELECT COALESCE(SUM(oi.quantity),0) AS sold
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE p.user_id=%s
        """, (user_id,))
        sold = cur.fetchone()["sold"]

        # REVENUE
        cur.execute("""
            SELECT COALESCE(SUM(oi.quantity * oi.price),0) AS revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE p.user_id=%s
        """, (user_id,))
        revenue = cur.fetchone()["revenue"] or 0

        # PENDING
        cur.execute("""
            SELECT COUNT(DISTINCT o.id) AS pending
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE p.user_id=%s AND LOWER(o.status)='pending'
        """, (user_id,))
        pending = cur.fetchone()["pending"]

        return {
            **profile,
            "productsSold": sold,
            "totalRevenue": float(revenue),
            "pendingOrders": pending
        }

    finally:
        cur.close()
        db.close()


# =====================================
# 📦 MY PRODUCTS
# =====================================
@router.get("/my-products")
def my_products(user=Depends(get_current_user)):

    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT id, name, price, category, description, image, unit
            FROM products
            WHERE user_id=%s
            ORDER BY id DESC
        """, (user["id"],))

        products = cur.fetchall() or []

        for p in products:
            img = p.get("image")
            if not img:
                p["image"] = "default.png"
            else:
                img = img.replace("\\", "/")
                img = img.replace("uploads/", "")
                p["image"] = img.lstrip("/")

        return products

    finally:
        cur.close()
        db.close()


# =====================================
# ➕ ADD PRODUCT (AUTO DESCRIPTION)
# =====================================
@router.post("/add-product")
def add_product(data: dict, user=Depends(get_current_user)):

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = get_db()
    cur = db.cursor()

    try:
        name = data.get("name")
        category = data.get("category")
        description = data.get("description")

        # ✅ AUTO GENERATE if empty
        if not description or description.strip() == "":
            description = generate_ai_description(name, category)

        cur.execute("""
            INSERT INTO products
            (name, price, category, description, image, unit, user_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            name,
            data.get("price"),
            category,
            description,
            data.get("image"),
            data.get("unit", "kg"),
            user["id"]
        ))

        db.commit()
        return {"message": "Product added successfully", "description": description}

    finally:
        cur.close()
        db.close()


# =====================================
# 📦 UPDATE PRODUCT
# =====================================
@router.put("/product/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    description: str = Form(None),
    user: dict = Depends(get_current_user)
):
    db = get_db()
    cur = db.cursor()

    try:
        # ✅ AUTO GENERATE if empty
        if not description or description.strip() == "":
            description = generate_ai_description(name, category)

        cur.execute("""
            UPDATE products
            SET name=%s, price=%s, category=%s, description=%s
            WHERE id=%s AND user_id=%s
        """, (
            name,
            price,
            category,
            description,
            product_id,
            user["id"]
        ))

        db.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"message": "Product updated successfully"}

    except Exception as e:
        db.rollback()
        print("UPDATE ERROR:", e)
        raise HTTPException(status_code=500, detail="Update failed")

    finally:
        cur.close()
        db.close()


# =====================================
# ❌ DELETE PRODUCT
# =====================================
@router.delete("/product/{product_id}")
def delete_product(product_id: int, user=Depends(get_current_user)):

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("""
            DELETE FROM products
            WHERE id=%s AND user_id=%s
        """, (product_id, user["id"]))

        db.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found")

        return {"message": "Deleted successfully"}

    except Exception as e:
        db.rollback()
        print("DELETE ERROR:", e)
        raise HTTPException(status_code=500, detail="Delete failed")

    finally:
        cur.close()
        db.close()


# =====================================
# 👨‍🌾 ALL FARMERS
# =====================================
@router.get("/all")
def fetch_farmers():
    return get_farmers() or []


# =====================================
# 🤖 MANUAL AI GENERATE API (OPTIONAL)
# =====================================
@router.post("/ai/generate-description")
def generate_description(data: dict):

    name = data.get("name")
    category = data.get("category")

    if not name:
        return {"description": "No product name provided"}

    return {
        "description": generate_ai_description(name, category)
    }