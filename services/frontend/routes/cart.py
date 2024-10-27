import os
import requests
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from session import get_session, SessionData

CART_SERVICE_API = os.environ.get('CART_SERVICE_API') or 'https://localhost:7004'
router = APIRouter(dependencies=[Depends(get_session)])

templates = Jinja2Templates(directory="templates")


@router.get("/summary", tags=["cart"], response_class=HTMLResponse)
async def cart_summary(request: Request, session: SessionData = Depends(get_session)):
    api_resp = requests.get(url=f'{CART_SERVICE_API}/?user_id={session.email}', verify=False)
    summary = api_resp.json()
    if api_resp.status_code == 200:
        return templates.TemplateResponse(
            "partials/cart_summary.html",
            {
                "request": request,
                **summary
            }
        )

    return HTMLResponse(
        status_code=api_resp.status_code,
        content="Could not subscribe. Please try again later."
    )


@router.get("/status", tags=["cart"], response_class=HTMLResponse)
async def cart_status(session: SessionData = Depends(get_session)):
    api_resp = requests.get(url=f'{CART_SERVICE_API}/?user_id={session.email}', verify=False)
    if api_resp.status_code == 200:
        cart_items = api_resp.json()['items']
        if len(cart_items) == 0:
            return HTMLResponse(status_code=200, content="CART")
        return HTMLResponse(status_code=200, content=f"CART <div class='cart-items'>{len(cart_items)}</div>")

    return HTMLResponse(status_code=api_resp.status_code, content="CART")


@router.post("/items", tags=["users"], response_class=HTMLResponse)
async def add_cart_item(
    product_id: int = Form(...),
    quantity: int = Form(...),
    session: SessionData = Depends(get_session)
):
    api_resp = requests.post(
        url=f'{CART_SERVICE_API}/items/?user_id={session.email}',
        json={
            "item_id": product_id,
            "quantity": quantity,
        },
        verify=False
    )
    if api_resp.status_code == 200:
        return HTMLResponse(
            status_code=200,
            content="<div class='success'>Added to cart &#10004;</div>",
            headers={"HX-Trigger": "cartChanged"}
        )

    return HTMLResponse(status_code=api_resp.status_code, content="Could not add item to cart")

@router.delete("/items", tags=["users"], response_class=HTMLResponse)
async def empty_cart(session: SessionData = Depends(get_session)):
    api_resp = requests.delete(url=f'{CART_SERVICE_API}/?user_id={session.email}', verify=False)
    if api_resp.status_code == 200:
        return HTMLResponse(status_code=200, content="Cart emptied", headers={"HX-Trigger": "cartChanged"})

    return HTMLResponse(status_code=api_resp.status_code, content="Could not empty cart")