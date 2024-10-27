import os
import requests
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from session import create_session, delete_session

USERS_SERVICE_API = os.environ.get('USERS_SERVICE_API') or 'https://localhost:7001'
router = APIRouter()


@router.post("/signup", tags=["users"], response_class=HTMLResponse)
async def signup(email: str = Form(...), password: str = Form(...)):
    api_resp = requests.post(
        url=f'{USERS_SERVICE_API}/signup',
        json={"email": email, "password": password},
        verify=False
    )
    if api_resp.status_code == 201:
        response: HTMLResponse = HTMLResponse(status_code=200, content="Registered", headers={"HX-Redirect": "/login"})
        return response

    return HTMLResponse(status_code=401, content=api_resp.content)


@router.post("/signin", tags=["users"], response_class=HTMLResponse)
async def signin(email: str = Form(...), password: str = Form(...)):
    api_resp = requests.post(
        url=f'{USERS_SERVICE_API}/signin',
        json={"email": email, "password": password},
        verify=False
    )

    if api_resp.status_code == 200:
        response: HTMLResponse = HTMLResponse(status_code=200, content="Logged in", headers={"HX-Redirect": "/"})
        create_session(email, response)
        return response

    return HTMLResponse(status_code=401, content="Invalid credentials, please try again.")


@router.post("/signout", tags=["users"], response_class=HTMLResponse)
async def signout(request: Request):
    delete_session(request)
    return HTMLResponse(status_code=401, content="Logged out.", headers={"HX-Redirect": "/login"})
