from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload

app = FastAPI(title="Insight Dash AI")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend listo para recibir datos",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
