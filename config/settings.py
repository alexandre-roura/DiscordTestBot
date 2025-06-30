from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class APIConfig:
    """Configuration pour les APIs externes."""
    minecraft_base_url: str = "http://localhost:8804"
    timeout: int = 30

@dataclass
class BotConfig:
    """Configuration pour le bot Discord."""
    command_prefix: str = "!"
    welcome_channel_id: Optional[int] = None
    ban_channel_id: Optional[int] = None
    minecraft_killfeed_channel_id: int = 1389082181309300796
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Crée une configuration à partir des variables d'environnement."""
        return cls(
            welcome_channel_id=int(os.getenv('WELCOME_CHANNEL', 0)) if os.getenv('WELCOME_CHANNEL') else None,
            ban_channel_id=int(os.getenv('BAN_CHANNEL', 0)) if os.getenv('BAN_CHANNEL') else None,
            minecraft_killfeed_channel_id=int(os.getenv('MINECRAFT_KILLFEED_CHANNEL', 1389082181309300796))
        )

# Configuration globale
api_config = APIConfig()
bot_config = BotConfig.from_env() 