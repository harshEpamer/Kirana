from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="alert-service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(alerts.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "alert-service", "port": 8007}
