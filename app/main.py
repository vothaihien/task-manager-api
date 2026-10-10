from fastapi import FastAPI

from app.routers import health, projects

app = FastAPI(title="Task Manager API", version="0.1.0")

app.include_router(health.router)
app.include_router(projects.router)
