"""FastAPI application entry point."""

from fastapi import FastAPI

from .config import get_settings
from .database import engine
from .models import Base
from .routers import auth, posts, users

Base.metadata.create_all(bind=engine)

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.app_name}"}
