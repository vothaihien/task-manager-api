from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.domain import AppError
from app.routers import auth, health, projects, users

app = FastAPI(title="Task Manager API", version="0.1.0")


@app.exception_handler(AppError)
async def app_error_handler(_, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(users.router)
