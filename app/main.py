from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


from app.database import engine
from app import models
from app.endpoints import items, users, auth
from app.config import settings

models.Base.metadata.create_all(engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    contact={"Github": "github.com/bhaskarn11"},
    version="1.1.0"
)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(items.router)
app.include_router(users.router)
app.include_router(auth.router)

