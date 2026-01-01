"""API routers package."""
from src.routers.auth import router as auth_router
from src.routers.tasks import router as tasks_router

__all__ = ["auth_router", "tasks_router"]
