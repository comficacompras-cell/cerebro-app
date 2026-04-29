from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import adaptive, exercises, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(adaptive.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "version": "0.1.0"}
