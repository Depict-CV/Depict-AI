from fastapi import FastAPI

from backend.api import annotations, auth, data, ml, projects, users
from backend.db.database import init_db

app = FastAPI()

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
