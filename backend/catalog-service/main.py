from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import catalog

Base.metadata.create_all(bind=engine)

app = FastAPI(title="catalog-service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(catalog.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog-service", "port": 8003}
