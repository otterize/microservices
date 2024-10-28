from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from session import get_session, UnauthenticatedException


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(get_session)])
async def get_shop_page(request: Request):
    return templates.TemplateResponse("pages/shop.html", {"request": request})


@router.get("/cart", response_class=HTMLResponse, dependencies=[Depends(get_session)])
async def get_cart_page(request: Request, session=Depends(get_session)):
    return templates.TemplateResponse("pages/cart.html", {
        "request": request,
        "email": session.email
    })


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("pages/register.html", {"request": request})
