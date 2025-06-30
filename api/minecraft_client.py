import aiohttp
from typing import Optional, List, Dict, Any
from .models import MinecraftPlayer, MinecraftPlayerStats, KillData

class KillEvent:
    """Modèle pour un événement de kill."""
    def __init__(self, killer: str, victim: str, weapon: str, distance: float, timestamp: int):
        self.killer = killer
        self.victim = victim
        self.weapon = weapon
        self.distance = distance
        self.timestamp = timestamp

class APIError(Exception):
    """Exception personnalisée pour les erreurs API."""
    pass

class MinecraftAPIClient:
    """Client pour l'API Minecraft avec gestion d'erreurs robuste."""
    
    def __init__(self, base_url: str = "http://localhost:8804"):
        self.base_url = base_url.rstrip('/')
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Contexte manager pour l'ouverture de session."""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Contexte manager pour la fermeture de session."""
        if self._session:
            await self._session.close()
    
    async def get_players(self) -> List[MinecraftPlayer]:
        """Récupère la liste des joueurs."""
        if not self._session:
            raise APIError("Session non initialisée. Utilisez 'async with' ou appelez __aenter__")
            
        async with self._session.get(f"{self.base_url}/v1/playersTable") as response:
            if response.status != 200:
                raise APIError(f"Erreur {response.status}: Impossible de récupérer les joueurs")
            
            data = await response.json()
            players_data = data.get("players", [])
            
            return [
                MinecraftPlayer(
                    player_uuid=player["playerUUID"],
                    player_name=player["playerName"],
                    activity_index=player["activityIndex"],
                    playtime_active=player["playtimeActive"],
                    session_count=player["sessionCount"],
                    last_seen=player["lastSeen"],
                    registered=player["registered"],
                    ping_average=player["pingAverage"],
                    ping_max=player["pingMax"],
                    ping_min=player["pingMin"]
                )
                for player in players_data
            ]
    
    async def get_player_stats(self, player_uuid: str) -> Optional[MinecraftPlayerStats]:
        """Récupère les statistiques d'un joueur."""
        if not self._session:
            raise APIError("Session non initialisée. Utilisez 'async with' ou appelez __aenter__")
            
        async with self._session.get(f"{self.base_url}/v1/player?player={player_uuid}") as response:
            if response.status != 200:
                return None
            
            data = await response.json()
            kill_data = data.get("kill_data", {})
            
            return MinecraftPlayerStats(
                kill_data=KillData(
                    player_kills_total=kill_data.get("player_kills_total", 0),
                    deaths_total=kill_data.get("deaths_total", 0),
                    player_kills_7d=kill_data.get("player_kills_7d", 0),
                    deaths_7d=kill_data.get("deaths_7d", 0),
                    player_kdr_total=kill_data.get("player_kdr_total", "0"),
                    mob_kills_total=kill_data.get("mob_kills_total", 0)
                ),
                sessions=data.get("sessions", []),
                info=data.get("info", {}),
                timestamp=data.get("timestamp", 0)
            )
    
    async def get_kills(self, server: str = "Server 1") -> List[KillEvent]:
        """Récupère les événements de kill récents."""
        if not self._session:
            raise APIError("Session non initialisée. Utilisez 'async with' ou appelez __aenter__")
        
        import urllib.parse
        encoded_server = urllib.parse.quote(server)
        
        async with self._session.get(f"{self.base_url}/v1/kills?server={encoded_server}") as response:
            if response.status != 200:
                raise APIError(f"Erreur {response.status}: Impossible de récupérer les kills")
            
            data = await response.json()
            kills_data = data.get("kills", [])
            
            return [
                KillEvent(
                    killer=kill.get("killer", "Unknown"),
                    victim=kill.get("victim", "Unknown"),
                    weapon=kill.get("weapon", "Unknown"),
                    distance=kill.get("distance", 0.0),
                    timestamp=kill.get("timestamp", 0)
                )
                for kill in kills_data
            ] 