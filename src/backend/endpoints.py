import sentry_sdk
from fastapi import FastAPI

from config import config
from src.backend.api import annotations, auth, data, ml, projects, users
from src.backend.db.database import init_db

SENTRY_DSN = config.SENTRY_DSN

# Initialize Sentry
sentry_sdk.init(
    dsn=SENTRY_DSN,
    send_default_pii=True,
)

app = FastAPI()


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


# initialize DB (creates tables if needed)
init_db()

# include routers split across backend/api
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(data.router)
app.include_router(annotations.router)
app.include_router(ml.router)


@app.get("/", tags=["root"])
def read_root():
    return {"status": "ok", "message": "API alive"}
