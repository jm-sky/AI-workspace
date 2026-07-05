"""AI routers."""

from .chat import router as chat_router
from .history import router as history_router
from .models import router as models_router
from .settings import router as settings_router

__all__ = ["chat_router", "models_router", "settings_router", "history_router"]
