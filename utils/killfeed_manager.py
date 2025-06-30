import asyncio
import discord
from datetime import datetime
from api.minecraft_client import MinecraftAPIClient, KillEvent

class KillFeedManager:
    """Gestionnaire du killfeed avec monitoring automatique."""
    
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
                        embed = self._create_kill_embed(kill)
                        await self.channel.send(embed=embed)
                
            except Exception as e:
                print(f"Erreur lors du monitoring des kills: {e}")
            
            # Attendre avant la prochaine vérification
            await asyncio.sleep(self.check_interval)
    
    def _create_kill_embed(self, kill: KillEvent) -> discord.Embed:
        """Crée un embed pour un événement de kill."""
        # Déterminer l'emoji selon l'arme
        weapon_emoji = self._get_weapon_emoji(kill.weapon)
        
        # Créer un message stylé
        if kill.distance > 0:
            message = f"{weapon_emoji} **{kill.killer}** a anéanti **{kill.victim}** avec un {kill.weapon} à {kill.distance:.0f} mètres !"
        else:
            message = f"{weapon_emoji} **{kill.killer}** a éliminé **{kill.victim}** avec un {kill.weapon} !"
        
        embed = discord.Embed(
            title="💀 Kill Feed",
            description=message,
            color=discord.Color.red(),
            timestamp=datetime.fromtimestamp(kill.timestamp / 1000) if kill.timestamp > 0 else datetime.now()
        )
        
        embed.set_footer(text="Kill détecté automatiquement")
        return embed
    
    def _get_weapon_emoji(self, weapon: str) -> str:
        """Retourne l'emoji approprié selon l'arme."""
        weapon_lower = weapon.lower()
        
        if "sword" in weapon_lower or "épée" in weapon_lower:
            return "⚔️"
        elif "bow" in weapon_lower or "arc" in weapon_lower:
            return "🏹"
        elif "axe" in weapon_lower or "hache" in weapon_lower:
            return "🪓"
        elif "pickaxe" in weapon_lower or "pioche" in weapon_lower:
            return "⛏️"
        elif "trident" in weapon_lower:
            return "🔱"
        elif "crossbow" in weapon_lower or "arbalète" in weapon_lower:
            return "🏹"
        else:
            return "🗡️" 