import os
import requests
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

NEWSLETTER_SERVICE_API = os.environ.get('NEWSLETTER_SERVICE_API') or 'http://localhost:7003'
router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/subscribe", tags=["newsletter"], response_class=HTMLResponse)
async def subscribe(email: str = Form(...)):
    api_resp = requests.post(url=f'{NEWSLETTER_SERVICE_API}/subscribe', verify=False, json={
        "email": email
    })
    if api_resp.status_code == 201:
        return HTMLResponse(status_code=200, content="Successfully subscribed to newsletter!")

    print(f"Could not subscribe. Error: {api_resp.text}")
    return HTMLResponse(
        status_code=api_resp.status_code,
        content="Could not subscribe. Please try again later."
    )
