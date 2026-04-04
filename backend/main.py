from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import user, product, cart, order, payment, chat, farmer_routes, location_routes, admin, tracking, wishlist_routes

app = FastAPI()

# ✅ Routers
app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(payment.router)
app.include_router(chat.router)
app.include_router(farmer_routes.router, prefix="/farmer")
app.include_router(admin.router)
app.include_router(location_routes.router)
app.include_router(tracking.router)
app.include_router(wishlist_routes.router)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Static
app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/frontend",
    StaticFiles(directory=os.path.join(BASE_DIR, "../frontend")),
    name="frontend"
)
@app.get("/")
def home():
    return {"message": "Backend working ✅"}