import secrets
import time
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.auth import hash_password, verify_password
from app.database import get_connection, init_db

app = FastAPI(title="Simple Login App")

app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_THIS_SECRET_IN_PRODUCTION",
    https_only=False,
    same_site="lax",
)

templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)

login_attempts = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60

@app.on_event("startup")
def startup():
    init_db()

def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token

def valid_csrf(request: Request, token: str) -> bool:
    expected = request.session.get("csrf_token")
    return bool(expected and secrets.compare_digest(expected, token))

def rate_limited(identifier: str) -> bool:
    now = time.time()
    attempts = [
        t for t in login_attempts.get(identifier, [])
        if now - t < WINDOW_SECONDS
    ]
    login_attempts[identifier] = attempts
    return len(attempts) >= MAX_ATTEMPTS

def record_login_attempt(identifier: str):
    login_attempts.setdefault(identifier, []).append(time.time())

@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user,
         "csrf_token": get_csrf_token(request)},
    )

@app.get("/login-form", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None,
         "csrf_token": get_csrf_token(request)},
    )

@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    identifier: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    if not valid_csrf(request, csrf_token):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid request.",
             "csrf_token": get_csrf_token(request)},
            status_code=400,
        )

    identifier = identifier.strip().lower()

    if rate_limited(identifier):
        return templates.TemplateResponse(
            "login.html",
            {"request": request,
             "error": "Too many attempts. Try again later.",
             "csrf_token": get_csrf_token(request)},
            status_code=429,
        )

    record_login_attempt(identifier)

    conn = get_connection()
    user = conn.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE lower(username) = ? OR lower(email) = ?
        """,
        (identifier, identifier),
    ).fetchone()
    conn.close()

    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request,
             "error": "Invalid username/email or password.",
             "csrf_token": get_csrf_token(request)},
            status_code=401,
        )

    request.session.clear()
    request.session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
    }
    request.session["csrf_token"] = secrets.token_urlsafe(32)

    return RedirectResponse("/", status_code=303)

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None,
         "csrf_token": get_csrf_token(request)},
    )

@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    if not valid_csrf(request, csrf_token):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Invalid request.",
             "csrf_token": get_csrf_token(request)},
            status_code=400,
        )

    username = username.strip()
    email = email.strip().lower()

    error = None
    if len(username) < 3:
        error = "Username must contain at least 3 characters."
    elif "@" not in email:
        error = "Please enter a valid email."
    elif len(password) < 8:
        error = "Password must contain at least 8 characters."
    elif password != confirm_password:
        error = "Passwords do not match."
    else:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, hash_password(password)),
            )
            conn.commit()
            conn.close()
            return RedirectResponse("/login-form", status_code=303)
        except sqlite3.IntegrityError:
            conn.close()
            error = "Username or email is already registered."
        except Exception:
            conn.close()
            error = "Could not create account."

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": error,
         "csrf_token": get_csrf_token(request)},
        status_code=400,
    )

@app.get("/me", response_class=HTMLResponse)
def me(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login-form", status_code=303)
    return templates.TemplateResponse(
        "me.html",
        {"request": request, "user": user,
         "csrf_token": get_csrf_token(request)},
    )

@app.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    if not valid_csrf(request, csrf_token):
        return RedirectResponse("/", status_code=303)
    request.session.clear()
    return RedirectResponse("/", status_code=303)
