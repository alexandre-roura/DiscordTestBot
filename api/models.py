from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class KillEvent:
    """Modèle pour un événement de kill."""
    killer: str
    victim: str
    weapon: str
    distance: float
    timestamp: int

@dataclass
class MinecraftPlayer:
    """Modèle pour un joueur Minecraft."""
    player_uuid: str
    player_name: str
    activity_index: float
    playtime_active: int
    session_count: int
    last_seen: int
    registered: int
    ping_average: float
    ping_max: int
    ping_min: int

@dataclass
class KillData:
    """Modèle pour les données de combat."""
    player_kills_total: int
    deaths_total: int
    player_kills_7d: int
    deaths_7d: int
    player_kdr_total: str
    mob_kills_total: int

@dataclass
class MinecraftPlayerStats:
    """Modèle pour les statistiques complètes d'un joueur."""
    kill_data: KillData
    sessions: List[Dict[str, Any]]
    info: Dict[str, Any]
    timestamp: int 