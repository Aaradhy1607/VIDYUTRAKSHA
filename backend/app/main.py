import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of where command is run
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.db.database import init_db
from backend.app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    setup_logging()
    logger.info("Initializing %s backend engine...", settings.PROJECT_NAME)
    await init_db()
    logger.info("Database schemas initialized.")
    logger.info("Operational Meteorological Domains loaded for India.")
    yield
    logger.info("Shutting down %s backend engine...", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.SYSTEM_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", summary="Root Index")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
