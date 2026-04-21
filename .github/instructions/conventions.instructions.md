---
applyTo: "backend/**"
---

# Backend Conventions — All Agents Must Follow

## Service Structure
Every backend service is a standalone FastAPI app. Run from within its directory:
```
uvicorn main:app --reload --port <PORT>
```

## Required Files Per Service
- `main.py` — FastAPI app, CORS middleware, router registration, `/health` endpoint
- `database.py` — SQLAlchemy engine, SessionLocal, Base, `get_db()` dependency
- `models.py` — SQLAlchemy ORM models (only tables this service uses)
- `schemas.py` — Pydantic models for request/response
- `routers/<service>.py` — all route handlers
- `routers/__init__.py` — empty file
- `requirements.txt` — `fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart`

## Database
- DB path (relative from service folder): `sqlite:///../../kirana.db`
- Never hardcode absolute paths
- `Base.metadata.create_all(bind=engine)` in `main.py` to create tables on startup

## CORS — Copy Exactly
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

## Response Standards
- Return correct HTTP status: 200, 201, 400, 401, 404
- All error responses: `{"detail": "message"}`
- Use `response_model=` on all routes

## JWT Pattern (services that verify tokens)
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SECRET_KEY = os.getenv("JWT_SECRET", "kirana-secret-key-change-in-production")
ALGORITHM  = "HS256"
bearer = HTTPBearer()

def get_current_user_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Principles
- SOLID, KISS, DRY, YAGNI
- No global mutable state
- Validate all inputs via Pydantic schemas
- Never log or return password hashes
