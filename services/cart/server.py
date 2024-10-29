import os
import redis
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

PORT = 7004
REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
PRODUCTS_SERVICE_API = os.environ.get('PRODUCTS_SERVICE_API') or 'https://localhost:7002'


app = FastAPI()
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

class SetCartItem(BaseModel):
    item_id: int
    quantity: int


class CartItem(BaseModel):
    id: int
    title: str
    image: str
    price: float
    category: str
    quantity: int


@app.post("/items")
def add_item(user_id: str, item: SetCartItem):
    # Convert item data to a dictionary and store in Redis
    redis_client.hset(user_id, item.item_id, item.json())
    return {"message": "Item added to cart", "item": item}


@app.delete("/items/{item_id}")
def remove_item(user_id: str, item_id: str):
    if redis_client.hexists(user_id, item_id):
        redis_client.hdel(user_id, item_id)
        return {"message": f"Item {item_id} removed from cart"}
    else:
        raise HTTPException(status_code=404, detail="Item not found in cart")


@app.delete("/")
def empty_cart(user_id: str):
    redis_client.delete(user_id)
    return {"message": "Cart emptied successfully"}


@app.get("/")
def cart_summary(user_id: str):
    api_resp = requests.get(url=f'{PRODUCTS_SERVICE_API}/products', verify=False)
    products = {product['id']: product for product in api_resp.json()}

    cart_data = redis_client.hgetall(user_id)
    cart = {item_id: eval(item_data) for item_id, item_data in cart_data.items()}

    items = []
    shipping = 10.0
    total = 0.0
    for item_id, item_data in cart.items():
        product = products[int(item_id)]
        item = CartItem(**{
            **product,
            **item_data,
            "price": float(product['price']) * float(item_data['quantity'])
        })
        items.append(item)
        total += item.price * item.quantity

    return {
        "items": items,
        "shipping": shipping,
        "total": total + shipping
    }


if __name__ == "__main__":
    import uvicorn
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_path = f"{dir_path}/server.key"
    cert_path = f"{dir_path}/server.crt"

    print(key_path)

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"Starting server at https://localhost:{PORT}")
        uvicorn.run(app="server:app", host="0.0.0.0", port=PORT, reload=True, ssl_keyfile=key_path, ssl_certfile=cert_path)
    else:
        print(f"Starting server at http://localhost:{PORT}")
        uvicorn.run(app="server:app", host="0.0.0.0", port=PORT, reload=True)