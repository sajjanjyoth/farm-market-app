from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# ✅ Import Routes
from routes import (
    user,
    product,
    cart,
    order,
    payment,
    chat,
    farmer_routes,
    location_routes,
    admin,
    tracking,
    wishlist_routes
)

# ✅ Initialize App
app = FastAPI(title="Farmers Market API")

# =============================
# ✅ CORS CONFIGURATION
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⚠️ Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# ✅ INCLUDE ROUTERS
# =============================
app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(payment.router)
app.include_router(chat.router)
app.include_router(farmer_routes.router)
app.include_router(admin.router)
app.include_router(location_routes.router)
app.include_router(tracking.router)
app.include_router(wishlist_routes.router)

# =============================
# ✅ PATH SETUP
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================
# ✅ STATIC FILES (VERY IMPORTANT)
# =============================
app.mount(
    "/uploads",
    StaticFiles(directory=os.path.join(BASE_DIR, "uploads")),
    name="uploads"
)

# =============================
# ✅ FRONTEND FILES
# =============================
app.mount(
    "/frontend",
    StaticFiles(directory=os.path.join(BASE_DIR, "../frontend")),
    name="frontend"
)

# =============================
# ✅ HOME ROUTE
# =============================
@app.get("/")
def home():
    return {"message": "Backend working ✅"}