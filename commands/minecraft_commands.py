from typing import Optional
import discord
from discord import app_commands
from api.minecraft_client import MinecraftAPIClient, APIError
from api.models import MinecraftPlayerStats
from utils.helpers import handle_api_errors

class MinecraftCommands:
    """Gestionnaire des commandes Minecraft."""
    
    def __init__(self, api_client: MinecraftAPIClient):
        self.api_client = api_client
    
    @handle_api_errors
    async def get_player_stats_by_name(self, player_name: str) -> Optional[MinecraftPlayerStats]:
        """Récupère les stats d'un joueur par son nom."""
        players = await self.api_client.get_players()
        
        # Recherche du joueur
        player = next(
            (p for p in players if p.player_name.lower() == player_name.lower()),
            None
        )
        
        if not player:
            return None
        
        return await self.api_client.get_player_stats(player.player_uuid)
    
    def create_stats_embed(self, player_name: str, stats: MinecraftPlayerStats) -> discord.Embed:
        """Crée un embed Discord avec les statistiques."""
        embed = discord.Embed(
            title=f"Stats de {player_name}",
            description=f"Stats de combat de {player_name}",
            color=discord.Color.blue()
        )
        
        kill_data = stats.kill_data
        
        embed.add_field(
            name="Kills (Joueurs)",
            value=kill_data.player_kills_total,
            inline=True
        )
        embed.add_field(
            name="Morts",
            value=kill_data.deaths_total,
            inline=True
        )
        
        # Calcul du KDR
        if kill_data.deaths_total > 0:
            kdr = kill_data.player_kills_total / kill_data.deaths_total
            kdr_text = f"{kdr:.2f}"
        elif kill_data.player_kills_total > 0:
            kdr_text = "∞ (Aucune mort)"
        else:
            kdr_text = "0.00"
        
        embed.add_field(name="K/D Ratio", value=kdr_text, inline=True)
        
        return embed 