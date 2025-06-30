from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class RankingType(Enum):
    """Types de classement disponibles."""
    KILLS = "kills"
    DEATHS = "deaths"
    KD_RATIO = "kd_ratio"

@dataclass
class KillEvent:
    """Représente un événement de kill."""
    killer: str
    victim: str
    weapon: str
    timestamp: int
    distance: float = 0.0

@dataclass
class KillData:
    """Données de kills d'un joueur."""
    player_kills_total: int
    deaths_total: int
    player_kills_7d: int
    deaths_7d: int
    player_kdr_total: str
    mob_kills_total: int

@dataclass
class MinecraftPlayerStats:
    """Statistiques d'un joueur Minecraft."""
    kill_data: KillData
    sessions: List[Dict[str, Any]]
    info: Dict[str, Any]
    timestamp: int

@dataclass
class MinecraftPlayer:
    """Informations d'un joueur Minecraft."""
    player_uuid: str
    player_name: str
    activity_index: float
    playtime_active: int
    session_count: int
    last_seen: str
    registered: str
    ping_average: int
    ping_max: int
    ping_min: int 