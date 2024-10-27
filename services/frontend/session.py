from uuid import uuid4

from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import HTMLResponse


class SessionData(BaseModel):
    email: str


class UnauthenticatedException(Exception):
    def __init__(self, message: str):
        self.message = message


# TODO: Replace with redis or other backend
SESSION_DB: dict[str, SessionData] = {}
COOKIE_NAME = "Authorization"


def get_auth_user(request: Request):
    """verify that user has a valid session"""
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        raise UnauthenticatedException(message="No session found")
    if session_id not in SESSION_DB:
        raise UnauthenticatedException(message="Invalid session")

    return True


def create_session(email: str, response: HTMLResponse):
    data = SessionData(email=email)
    session_id = str(uuid4())
    SESSION_DB[session_id] = data

    response.set_cookie(COOKIE_NAME, session_id)


def delete_session(request: Request):
    session_id = request.cookies.get(COOKIE_NAME)
    if session_id:
        del SESSION_DB[session_id]
