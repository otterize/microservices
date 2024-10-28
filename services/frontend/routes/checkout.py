import os
import requests
from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from session import get_session, SessionData


CHECKOUT_SERVICE_API = os.environ.get('CHECKOUT_SERVICE_API') or 'https://localhost:7005'
router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/process", tags=["checkout"], response_class=HTMLResponse)
async def process_checkout(
    request: Request,
    email: str = Form(...),
    card: str = Form(...),
    year: str = Form(...),
    month: str = Form(...),
    cvv: str = Form(...),
    session: SessionData = Depends(get_session)
):
    api_resp = requests.post(url=f'{CHECKOUT_SERVICE_API}/process/?user_id={session.email}', verify=False, json={
        "email": email,
        "payment": {
            "card": card,
            "year": year,
            "month": month,
            "cvv": cvv
        }
    })
    if api_resp.status_code == 200:
        return templates.TemplateResponse(
            "partials/checkout_success.html",
            {"request": request},
            headers={"HX-Trigger": "cartChanged"}
        )

    return HTMLResponse(
        status_code=api_resp.status_code,
        content="Could not complete checkout. Please try again later."
    )
