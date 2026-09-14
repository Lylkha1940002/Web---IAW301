Audit & Roadmap --- FastAPI + SQLite + Login/Logout

Mục tiêu: biến nội dung trên whiteboard thành một bài tập có thể
triển khai, test và audit được.

Vai trò hướng dẫn: giảng viên hướng dẫn theo hướng thực hành
backend/API, đồng thời chú ý các nguyên tắc bảo mật cơ bản của một ứng
dụng có authentication.

1. Đọc đề bài từ whiteboard

Từ hình ảnh, mình hiểu bài tập đang hướng tới một ứng dụng Python đơn
giản gồm:

Python

FastAPI

Uvicorn

SQLite3

Database

SQLite

Có bảng users

Các trường được ghi chú: username/email, password

API / Web

/ping → trả về "pong"

/login-form → hiển thị form đăng nhập

/login → xử lý đăng nhập

/logout → đăng xuất

Có ý tưởng về:

kiểm tra thông tin đăng nhập với database

nếu đúng thì cho phép đăng nhập

nếu sai thì thông báo lỗi

quản lý trạng thái đăng nhập

Điểm chưa rõ trên whiteboard

Có một số phần viết tắt nên không nên tự coi là requirement chính
thức:

all -> Bảng -> ?

ký hiệu sau users

cơ chế session/token chưa được ghi rõ

chưa rõ frontend dùng HTML thuần hay template engine

chưa rõ password được lưu plain-text hay hash

Trong audit, các điểm này sẽ được đánh dấu là TBD (To Be Determined)
thay vì đoán.

2. Kiến trúc đề xuất

Cho một bài tập học tập, không nên làm quá phức tạp ngay từ đầu.

Browser
   |
   | HTTP
   v
FastAPI
   |
   +---- /ping
   |
   +---- /login-form
   |
   +---- /login
   |
   +---- /logout
   |
   v
Authentication logic
   |
   v
SQLite
   |
   +---- users

Luồng chính:

GET /login-form
       |
       v
   Login HTML
       |
       | POST username/email + password
       v
    POST /login
       |
       v
   Query users
       |
       +---- không tìm thấy / password sai
       |             |
       |             v
       |          Login fail
       |
       +---- hợp lệ
                     |
                     v
                 Login OK
                     |
                     v
               Session/Auth

3. Stack công nghệ

3.1 Python

Ngôn ngữ chính.

Nên dùng Python 3.11+ hoặc 3.12+ nếu môi trường học tập cho phép.

3.2 FastAPI

Dùng để xây dựng HTTP API/web backend.

FastAPI hỗ trợ dependency injection, validation và security utilities.

3.3 Uvicorn

ASGI server để chạy FastAPI.

Ví dụ:

uvicorn app.main:app --reload

3.4 SQLite

Phù hợp cho bài tập vì:

không cần chạy database server riêng

database nằm trong một file

Python có sẵn module sqlite3

dễ inspect và reset dữ liệu

FastAPI cũng có tài liệu chính thức minh họa việc dùng SQLite cho ứng
dụng nhỏ/prototype.

3.5 HTML Form

Nếu bài tập yêu cầu /login-form, có thể bắt đầu bằng HTML đơn giản.

Ví dụ:

<form method="post" action="/login">
    <input name="username" type="text">
    <input name="password" type="password">
    <button type="submit">Login</button>
</form>

FastAPI dùng Form() để nhận dữ liệu từ HTML form; với form data cần
cài thêm python-multipart.

4. Thiết kế database

4.1 Bảng users

Mức tối thiểu:

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL
);

Khuyến nghị

Không nên đặt:

password TEXT

và lưu password nguyên bản.

Nên dùng:

password_hash TEXT

Password người dùng nhập:

"123456"

không được lưu trực tiếp.

Thay vào đó:

password
   |
   v
password hashing algorithm
   |
   v
password_hash

Khi login:

input password
      |
      v
verify against password_hash
      |
      v
True / False

5. Requirement Specification

R1 --- Health check

Endpoint:

GET /ping

Expected response:

pong

Acceptance criteria

Server chạy được

GET /ping trả HTTP 200

Response body là pong

R2 --- Login form

Endpoint:

GET /login-form

Expected:

HTTP 200

trả về HTML

có field username/email

có field password

có nút Login

Acceptance criteria

mở được /login-form

form có method="post"

form trỏ tới /login

password input có type="password"

R3 --- Login

Endpoint:

POST /login

Input:

username/email
password

Backend:

receive input
     |
     v
validate input
     |
     v
find user
     |
     v
verify password
     |
     +---- FAIL ---> reject
     |
     +---- OK ----> create authenticated state

Acceptance criteria

Case 1 --- user không tồn tại:

login -> FAIL

Case 2 --- password sai:

login -> FAIL

Case 3 --- username/password đúng:

login -> SUCCESS

6. Authentication state

Đây là phần quan trọng nhất mà whiteboard chưa chỉ rõ.

Sau khi login thành công, server cần biết:

"Request tiếp theo có phải là của user đã đăng nhập không?"

Có hai hướng phổ biến:

Option A --- Session cookie

Browser
   |
   | POST /login
   v
Server
   |
   +--> authenticate
   |
   +--> create session
   |
   +--> Set-Cookie
   |
   v
Browser

Các request sau gửi cookie.

Đây là hướng dễ hiểu nếu bài tập đang xây dựng web app có login form.

Option B --- Token/JWT

POST /login
     |
     v
token
     |
     v
client gửi token ở request sau

JWT/token thường phù hợp hơn khi backend phục vụ SPA/mobile/API clients.

Khuyến nghị cho bài tập này

Nếu mục tiêu là hiểu:

form -> login -> session -> logout

thì nên ưu tiên session/cookie trước, chưa cần nhảy ngay vào JWT.

7. Logout

Endpoint:

POST /logout

hoặc trong bài tập đơn giản có thể dùng:

GET /logout

Nhưng về thiết kế HTTP, thao tác làm thay đổi trạng thái authentication
nên ưu tiên POST.

Flow:

Authenticated user
        |
        v
    POST /logout
        |
        v
invalidate session
        |
        v
    logged out

Acceptance criteria

user đang login có thể logout

session/cookie authentication bị vô hiệu hóa

truy cập resource yêu cầu login sau logout phải bị từ chối

8. Cấu trúc project đề xuất

login-app/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       └── auth.py
│
├── templates/
│   └── login.html
│
├── tests/
│   ├── test_ping.py
│   └── test_auth.py
│
├── database.db
├── requirements.txt
└── README.md

Nếu bài tập đang ở mức beginner, có thể bắt đầu nhỏ hơn:

project/
├── main.py
├── database.py
├── templates/
│   └── login.html
└── database.db

Sau khi chạy được mới refactor thành nhiều module.

9. Lộ trình implementation

Phase 1 --- Hello backend

Mục tiêu:

GET /ping

Code concept:

@app.get("/ping")
def ping():
    return "pong"

Checklist:

cài Python

cài FastAPI

cài Uvicorn

chạy server

test /ping

Phase 2 --- SQLite

Tạo database:

database.db

Tạo bảng:

users

Có thể bắt đầu với:

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL
);

Checklist:

database được tạo

table users được tạo

insert được một user test

select được user

Phase 3 --- Login form

Tạo:

GET /login-form

Hiển thị:

Username / Email
Password
[ Login ]

Checklist:

HTML render được

form submit được

request gửi tới /login

Phase 4 --- Login logic

Pseudo-code:

def login(username_or_email, password):

    user = find_user(username_or_email)

    if user is None:
        return login_failed()

    if not verify_password(password, user.password_hash):
        return login_failed()

    return login_success(user)

Quan trọng: không query database bằng cách nối string trực tiếp.

Không nên:

sql = f"SELECT * FROM users WHERE username = '{username}'"

Nên dùng parameterized query:

cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)

10. Security checklist

Đây là phần mình muốn bạn đặc biệt chú ý nếu bài được chấm theo góc nhìn
IA/security.

S1 --- Password

Không lưu plaintext password

Dùng password hashing

Không log password

Không trả password/hash về client

S2 --- SQL Injection

Không concatenate input trực tiếp vào SQL.

Bad:

f"SELECT * FROM users WHERE username = '{username}'"

Good:

cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)

S3 --- Brute force

Phiên bản beginner có thể chưa cần triển khai đầy đủ, nhưng audit phải
ghi nhận:

rate limiting chưa có / có

lockout chưa có / có

logging login failures chưa có / có

S4 --- Session

Kiểm tra:

cookie có HttpOnly

cookie có Secure khi chạy HTTPS

cookie có SameSite

session được invalidate khi logout

S5 --- Error message

Không nên trả:

User abc không tồn tại

và:

Password sai

theo cách giúp attacker enumerate account.

Có thể dùng thông báo chung:

Invalid username/email or password.

11. Test matrix

Test ID   Scenario                                  Expected

T01       GET /ping                               200 + pong
T02       GET /login-form                         200 + HTML
T03       Login user tồn tại + password đúng        Success
T04       Login user không tồn tại                  Fail
T05       Login password sai                        Fail
T06       Login thiếu username                      Validation error
T07       Login thiếu password                      Validation error
T08       SQL injection payload                     Không bypass login
T09       Logout                                    Session bị invalidate
T10       Access protected page sau logout          Denied
T11       Password không xuất hiện trong response   Pass
T12       Password không được lưu plaintext         Pass

12. Audit checklist

Architecture

FastAPI được dùng đúng vai trò backend

Uvicorn chạy application

SQLite được kết nối đúng

database access tách khỏi route nếu project đủ lớn

authentication logic không nằm lẫn toàn bộ trong HTML route

API

/ping

/login-form

/login

/logout

protected endpoint để kiểm tra trạng thái login

Database

users.id

users.username

users.email

users.password_hash

unique constraint phù hợp

parameterized SQL

Authentication

password hashing

password verification

session/token

logout

protected route

Security

SQL injection

password storage

session security

account enumeration

brute force/rate limiting

CSRF nếu dùng cookie-based form authentication

HTTPS trong môi trường production

Testing

happy path

invalid credentials

missing fields

unauthorized access

logout

security tests

13. Definition of Done

Bài tập chỉ được coi là hoàn thành khi:

[ ] Server start được
        |
        v
[ ] /ping hoạt động
        |
        v
[ ] SQLite hoạt động
        |
        v
[ ] users table hoạt động
        |
        v
[ ] login form hoạt động
        |
        v
[ ] login đúng -> authenticated
        |
        v
[ ] login sai -> rejected
        |
        v
[ ] protected endpoint yêu cầu authentication
        |
        v
[ ] logout hoạt động
        |
        v
[ ] password không lưu plaintext
        |
        v
[ ] SQL injection không bypass được login
        |
        v
[ ] test pass

14. Các câu hỏi bạn phải tự trả lời khi bị giảng viên hỏi

Q1. FastAPI làm gì?

FastAPI xử lý HTTP request/response và định nghĩa API/web routes.

Q2. Uvicorn làm gì?

Uvicorn là ASGI server dùng để chạy ứng dụng FastAPI.

Q3. SQLite là gì?

SQLite là relational database nhẹ, lưu database trong file và không cần
database server riêng.

Q4. Tại sao không lưu password trực tiếp?

Vì nếu database bị lộ, plaintext password sẽ bị lộ ngay.

Q5. Login thành công thì server nhớ user bằng cách nào?

Thông qua authentication state, ví dụ session cookie hoặc token.

Q6. Logout làm gì?

Invalidate/remove authentication state để request tiếp theo không còn
được xem là authenticated.

Q7. Tại sao dùng parameterized SQL?

Để tách SQL command khỏi user input và giảm nguy cơ SQL injection.

15. Những thứ KHÔNG nên làm ngay

Đừng bắt đầu bằng:

JWT
OAuth2
Redis
Docker
PostgreSQL
microservices
Kubernetes

nếu mục tiêu của bài hiện tại chỉ là:

Python
+
FastAPI
+
SQLite
+
Login
+
Logout

Hãy làm MVP chạy được trước.

Sau đó mới nâng cấp:

MVP
 |
 +--> password hashing
 |
 +--> session security
 |
 +--> tests
 |
 +--> validation
 |
 +--> rate limiting
 |
 +--> PostgreSQL
 |
 +--> deployment

16. Audit status hiện tại

Dựa chỉ trên whiteboard, trạng thái hiện tại nên đánh giá là:

Hạng mục                   Status   Nhận xét

Python                     🟢       Đã xác định
FastAPI                    🟢       Đã xác định
Uvicorn                    🟢       Đã xác định
SQLite                     🟢       Đã xác định
users table              🟢       Đã xác định
Login form                 🟢       Đã xác định
Login endpoint             🟢       Đã xác định
Logout                     🟡       Có đề cập nhưng chưa đặc tả
Session/token              🔴       Chưa xác định
Password hashing           🔴       Chưa xác định
Protected endpoint         🟡       Nên bổ sung để chứng minh authentication
SQL injection protection   🔴       Chưa thể hiện
Automated tests            🔴       Chưa thể hiện
Error handling             🟡       Chưa đặc tả
CSRF                       🔴       Chưa đặc tả nếu dùng cookie/form
Rate limiting              🔴       Chưa đặc tả

Legend

🟢 = đã rõ

🟡 = có ý tưởng nhưng cần đặc tả

🔴 = chưa có / cần bổ sung

17. Nguồn tham khảo

FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/

FastAPI SQL Databases:
https://fastapi.tiangolo.com/tutorial/sql-databases/

FastAPI Security:
https://fastapi.tiangolo.com/tutorial/security/first-steps/

FastAPI Form Data:
https://fastapi.tiangolo.com/tutorial/request-forms/

Python sqlite3: https://docs.python.org/3/library/sqlite3.html

FastAPI có tài liệu chính thức cho database/SQLite, security và form
data; SQLite cũng có module sqlite3 trong Python standard library.

18. Kế hoạch học/implement đề xuất

Bước 1

Làm /ping.

Bước 2

Kết nối SQLite và tạo users.

Bước 3

Viết CRUD/select cơ bản cho users.

Bước 4

Làm /login-form.

Bước 5

Làm /login.

Bước 6

Thêm password hashing.

Bước 7

Thêm session/cookie.

Bước 8

Làm /logout.

Bước 9

Tạo một protected endpoint, ví dụ:

GET /me

Nếu chưa login:

401 Unauthorized

Nếu đã login:

{
    "username": "...",
    "email": "..."
}

Bước 10

Viết test.

Bước 11

Audit security.

Kết luận

Bản chất bài này không phải là "làm một website login thật lớn".

Bài này nên được xem là một bài thực hành nhỏ để bạn hiểu chuỗi:

HTTP
  ↓
FastAPI
  ↓
Route
  ↓
Form input
  ↓
Validation
  ↓
Authentication
  ↓
Database
  ↓
Session
  ↓
Authorization
  ↓
Logout

Nếu nắm chắc chuỗi này, sau đó chuyển sang PostgreSQL, JWT, OAuth2 hoặc
một framework lớn hơn sẽ dễ hơn rất nh

## Functional
- [x] FastAPI
- [x] Uvicorn
- [x] SQLite
- [x] users table
- [x] /ping
- [x] /login-form
- [x] /login
- [x] /logout
- [x] protected /me
- [x] registration

## Security
- [x] Argon2 password hashing
- [x] no plaintext password storage
- [x] parameterized SQL
- [x] signed session cookie
- [x] HttpOnly
- [x] SameSite=Lax
- [x] CSRF token
- [x] generic authentication error
- [x] basic rate limiting
- [ ] HTTPS production
- [ ] production secret management
