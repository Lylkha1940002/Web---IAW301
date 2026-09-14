# Simple FastAPI + SQLite Login

Giao diện cố ý tối giản nhưng vẫn đủ yêu cầu chính của bài:

- `/ping` -> `pong`
- `/login-form`
- `/register`
- `/login`
- `/me` protected
- `/logout`
- SQLite `users`
- Argon2 password hashing
- Parameterized SQL
- Session cookie
- CSRF token
- Basic login rate limiting
- Tests

## Windows PowerShell

```powershell
cd "duong-dan-den\simple_fastapi_login"
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Mở http://127.0.0.1:8000/

Swagger: http://127.0.0.1:8000/docs

Test: `pytest -q`

## Production
Đổi `secret_key`, dùng biến môi trường/secret manager và chạy HTTPS.
