import os
import requests
from fastapi import APIRouter, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from session import get_session, SessionData


CHECKOUT_SERVICE_API = os.environ.get('CHECKOUT_SERVICE_API') or 'https://localhost:7005'
router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/process", tags=["chekcout"], response_class=HTMLResponse)
async def process_checkout(
    email: str = Form(...),
    session: SessionData = Depends(get_session)
):
    api_resp = requests.post(url=f'{CHECKOUT_SERVICE_API}/process/?user_id={session.email}', verify=False, json={
        "email": email
    })
    if api_resp.status_code == 200:
        return HTMLResponse(status_code=200, content="Successfully subscribed to newsletter!")

    return HTMLResponse(
        status_code=api_resp.status_code,
        content="Could not subscribe. Please try again later."
    )
