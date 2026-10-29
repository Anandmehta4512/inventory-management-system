from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.dsa import InventoryEngine

app = FastAPI(title="Zoho-Style Enterprise Inventory Management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = InventoryEngine()

# Auth Schemas
class LoginSchema(BaseModel):
    email: str
    password: str

class RegisterSchema(BaseModel):
    email: str
    password: str
    full_name: str

# Inventory Schemas
class ProductSchema(BaseModel):
    product_id: str
    name: str
    category: str = "General"
    quantity: int
    cost_price: float
    selling_price: float

class SaleSchema(BaseModel):
    product_id: str
    quantity: int
    customer_name: str

class PurchaseSchema(BaseModel):
    product_id: str
    quantity: int
    vendor_name: str

# Auth Endpoints
@app.post("/auth/register")
def register(data: RegisterSchema):
    success, msg = engine.register_user(data.email, data.password, data.full_name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/auth/login")
def login(data: LoginSchema):
    authenticated, full_name = engine.authenticate_user(data.email, data.password)
    if not authenticated:
        raise HTTPException(status_code=401, detail="Invalid email or password!")
    return {
        "message": "Login successful",
        "user": {
            "email": data.email,
            "full_name": full_name
        }
    }

# Data Endpoints
@app.get("/")
def home():
    return {"status": "Enterprise Inventory Backend Active"}

@app.get("/summary")
def get_kpi_summary():
    return engine.get_summary()

@app.get("/products")
def get_products():
    return engine.get_all_sorted()

@app.get("/products/{product_id}")
def search_product(product_id: str):
    item = engine.search(product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Product nahi mila")
    return item

@app.post("/products")
def add_product(product: ProductSchema):
    engine.add_or_update(
        product.product_id, 
        product.name, 
        product.category, 
        product.quantity, 
        product.cost_price, 
        product.selling_price
    )
    return {"message": "Product item master me save ho gaya"}

@app.post("/sales")
def create_sale(sale: SaleSchema):
    success, msg = engine.process_sale(sale.product_id, sale.quantity, sale.customer_name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/purchases")
def create_purchase(purchase: PurchaseSchema):
    success, msg = engine.process_purchase(purchase.product_id, purchase.quantity, purchase.vendor_name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    success = engine.delete(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product nahi mila")
    return {"message": "Product delete ho gaya"}