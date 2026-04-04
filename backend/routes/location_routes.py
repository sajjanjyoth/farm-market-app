from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import get_db
from utils.auth_utils import get_current_user
from math import radians, cos, sin, asin, sqrt

router = APIRouter()

# -------- MODEL --------
class Location(BaseModel):
    latitude: float
    longitude: float

# -------- DISTANCE FUNCTION --------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    return R * c

# -------- UPDATE USER LOCATION --------
@router.post("/user/location")
def update_location(loc: Location, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE users SET latitude=%s, longitude=%s WHERE id=%s",
        (loc.latitude, loc.longitude, user["id"])
    )

    db.commit()
    cursor.close()
    db.close()

    return {"message": "Location updated"}

# -------- NEARBY PRODUCTS --------
@router.get("/nearby-products")
def nearby_products(user_lat: float, user_lon: float):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, u.latitude, u.longitude, u.name AS farmer_name
        FROM products p
        JOIN users u ON p.farmer_id = u.id
    """)

    products = cursor.fetchall()
    result = []

    DELIVERY_RATE = 5

    for p in products:
        if p["latitude"] and p["longitude"]:
            dist = haversine(user_lat, user_lon, p["latitude"], p["longitude"])

            if dist <= 20:
                p["distance_km"] = round(dist, 2)
                p["delivery_price"] = round(dist * DELIVERY_RATE, 2)
                result.append(p)

    result.sort(key=lambda x: x["distance_km"])

    cursor.close()
    db.close()

    return result

# -------- RECOMMENDED FARMER --------
@router.get("/recommended-farmer")
def recommended_farmer(user_lat: float, user_lon: float):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE role='farmer'")
    farmers = cursor.fetchall()

    best = None
    min_dist = 999

    for f in farmers:
        if f["latitude"] and f["longitude"]:
            dist = haversine(user_lat, user_lon, f["latitude"], f["longitude"])

            if dist < min_dist:
                min_dist = dist
                best = f

    cursor.close()
    db.close()

    if best:
        return {"farmer": best, "distance_km": round(min_dist, 2)}

    return {"message": "No farmers found"}

# -------- ADMIN: ALL FARMERS --------
@router.get("/all-farmers")
def all_farmers():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, name, latitude, longitude FROM users WHERE role='farmer'")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return data