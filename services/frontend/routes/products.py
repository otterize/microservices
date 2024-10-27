import os
import requests
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

PRODUCTS_SERVICE_API = os.environ.get('PRODUCTS_SERVICE_API') or 'https://localhost:7002'
router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/products", tags=["products"], response_class=HTMLResponse)
async def products(request: Request):
    api_resp = requests.get(url=f'{PRODUCTS_SERVICE_API}/products', verify=False)
    if api_resp.status_code == 200:
        return templates.TemplateResponse(
            "partials/product_list.html",
            {
                "request": request,
                "products": api_resp.json()
            }
        )

    return HTMLResponse(status_code=500, content="Could not load products. Please try again later.")
