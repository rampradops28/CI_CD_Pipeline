from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Order Service API")

class Order(BaseModel):
    item: str
    quantity: int

@app.get("/")
def read_root():
    return {"service": "Order Service", "status": "active"}

@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "order-service"}

@app.post("/orders")
def create_order(order: Order):
    return {"order_id": 101, "item": order.item, "quantity": order.quantity, "status": "confirmed"}
