import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config
from src.backend.api import annotations, data, images, minio_sync, ml, notifications, projects, test_auth, users
from src.backend.db.database import init_db

SENTRY_DSN = config.SENTRY_DSN

# Initialize Sentry
sentry_sdk.init(
    dsn=SENTRY_DSN,
    send_default_pii=True,
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sentry-debug")
async def trigger_error():
    return 1 / 0


# initialize DB (creates tables if needed)
init_db()

# include routers split across backend/api
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(data.router)
app.include_router(annotations.router)
app.include_router(ml.router)
app.include_router(images.router)
app.include_router(minio_sync.router)
app.include_router(test_auth.router)
app.include_router(notifications.router)


@app.get("/", tags=["root"])
def read_root():
    return {"status": "ok", "message": "API alive"}


# todo add endpoints for: statistics for annotation and project , health , get all images without annotations,
# TODO refactor endpoint to limit the call ( by batch or pagination) and run 1 request instead of loop of db requests
