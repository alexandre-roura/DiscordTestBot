import asyncio
import discord
from datetime import datetime
from api.minecraft_client import MinecraftAPIClient, KillEvent
from views.minecraft_views import MinecraftViews

class KillFeedService:
    """Service de monitoring du killfeed."""
    
    def __init__(self, api_client: MinecraftAPIClient, channel: discord.TextChannel = None):
        self.api_client = api_client
        self.channel = channel
        self.is_monitoring = False
        self.monitoring_task = None
        self.last_kill_timestamp = 0
        self.check_interval = 30  # secondes
    
    async def start_monitoring(self):
        """Démarre le monitoring du killfeed."""
        if self.is_monitoring:
            return False, "Le killfeed est déjà en cours de monitoring."
        
        if not self.channel:
            return False, "Canal de killfeed non configuré."
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_kills())
        return True, f"Killfeed démarré dans {self.channel.mention}"
    
    async def stop_monitoring(self):
        """Arrête le monitoring du killfeed."""
        if not self.is_monitoring:
            return False, "Le killfeed n'est pas en cours de monitoring."
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
        
        channel_name = self.channel.mention if self.channel else "le canal"
        return True, f"Killfeed arrêté dans {channel_name}"
    
    async def _monitor_kills(self):
        """Boucle de monitoring des kills."""
        while self.is_monitoring:
            try:
                kills = await self.api_client.get_kills()
                
                # Filtrer les nouveaux kills
                new_kills = [
                    kill for kill in kills 
                    if kill.timestamp > self.last_kill_timestamp
                ]
                
                # Mettre à jour le timestamp
                if kills:
                    self.last_kill_timestamp = max(kill.timestamp for kill in kills)
                
                # Afficher les nouveaux kills
                if self.is_monitoring:
                    for kill in new_kills:
                        embed = MinecraftViews.create_killfeed_embed(kill)
                        await self.channel.send(embed=embed)
                
            except Exception as e:
                print(f"Erreur lors du monitoring des kills: {e}")
            
            # Attendre avant la prochaine vérification
            await asyncio.sleep(self.check_interval) 