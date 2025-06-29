import logging
from functools import wraps
from typing import Callable, Any
from api.minecraft_client import APIError

logger = logging.getLogger(__name__)

def handle_api_errors(func: Callable) -> Callable:
    """Décorateur pour gérer les erreurs API."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except APIError as e:
            logger.error(f"Erreur API dans {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue dans {func.__name__}: {e}")
            raise
    return wrapper

def setup_logging(level: str = "INFO") -> None:
    """Configure le système de logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log', encoding='utf-8')
        ]
    ) 