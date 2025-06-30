import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from api.minecraft_client import MinecraftAPIClient
from api.models import MinecraftPlayerStats
from utils.helpers import handle_api_errors
from services.killfeed_service import KillFeedService
from views.minecraft_views import MinecraftViews
from enum import Enum

class RankingType(Enum):
    """Types de classements disponibles."""
    KDA = "kda"
    KILLS = "kills"
    DEATHS = "deaths"

class MinecraftCog(commands.Cog):
    """Cog pour les commandes Minecraft."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_client = MinecraftAPIClient()
        self.killfeed = None
    
    async def cog_load(self):
        """Appelé quand le Cog est chargé."""
        await self.api_client.__aenter__()
        # Le canal sera configuré dans setup_killfeed
    
    async def cog_unload(self):
        """Appelé quand le Cog est déchargé."""
        if self.killfeed:
            await self.killfeed.stop_monitoring()
        await self.api_client.__aexit__(None, None, None)
    
    async def setup_killfeed(self, channel_id: int):
        """Configure le canal de killfeed."""
        self.killfeed = KillFeedService(self.api_client, self.bot.get_channel(channel_id))
    
    @app_commands.command(name="listminecraftplayers", description="Affiche la liste des joueurs Minecraft")
    @handle_api_errors
    async def list_minecraft_players(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        players = await self.api_client.get_players()
        embed = MinecraftViews.create_player_list_embed(players)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="statsminecraftforplayer", description="Affiche les stats minecraft d'un joueur")
    @handle_api_errors
    async def stats_minecraft_for_player(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer()
        
        players = await self.api_client.get_players()
        player = next(
            (p for p in players if p.player_name.lower() == player_name.lower()),
            None
        )
        
        if not player:
            await interaction.followup.send(
                f"Le joueur {player_name} n'a pas été trouvé.",
                ephemeral=True
            )
            return
        
        stats = await self.api_client.get_player_stats(player.player_uuid)
        if not stats:
            await interaction.followup.send(
                f"Aucune statistique trouvée pour {player_name}.",
                ephemeral=True
            )
            return
        
        embed = MinecraftViews.create_stats_embed(player_name, stats)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="minecraftranking", description="Affiche le classement des joueurs Minecraft")
    @app_commands.describe(
        ranking_type="Type de classement (kda/kills/deaths)",
        limit="Nombre de joueurs à afficher (défaut: 10, max: 25)"
    )
    @app_commands.choices(ranking_type=[
        app_commands.Choice(name="Ratio K/D", value="kda"),
        app_commands.Choice(name="Nombre de Kills", value="kills"),
        app_commands.Choice(name="Nombre de Morts", value="deaths")
    ])
    @handle_api_errors
    async def minecraft_ranking(self, interaction: discord.Interaction, ranking_type: str, limit: int = 10):
        await interaction.response.defer()
        
        if limit < 1 or limit > 25:
            await interaction.followup.send(
                "Le nombre de joueurs doit être entre 1 et 25.",
                ephemeral=True
            )
            return
        
        try:
            ranking_enum = RankingType(ranking_type)
        except ValueError:
            await interaction.followup.send(
                "Type de classement invalide. Utilisez 'kda', 'kills' ou 'deaths'.",
                ephemeral=True
            )
            return
        
        ranking_data = await self.get_players_ranking(ranking_enum, limit)
        embed = MinecraftViews.create_ranking_embed(ranking_data, ranking_enum)
        await interaction.followup.send(embed=embed)
    
    @commands.command(name="killfeed")
    async def toggle_killfeed(self, ctx, action: str = None):
        """Active/désactive le suivi des kills dans le canal."""
        if not action:
            await ctx.send("❌ Veuillez spécifier 'start' ou 'stop'.")
            return

        if action.lower() == "start":
            if not self.killfeed:
                self.killfeed = KillFeedService(self.api_client, ctx.channel)
            success, message = await self.killfeed.start_monitoring()
        
        elif action.lower() == "stop":
            if not self.killfeed:
                await ctx.send("❌ Le killfeed n'est pas initialisé.")
                return
            success, message = await self.killfeed.stop_monitoring()
        
        else:
            await ctx.send("❌ Action invalide. Utilisez 'start' ou 'stop'.")
            return

        await ctx.send("✅ " + message if success else "❌ " + message)
    
    # Méthodes utilitaires
    async def get_players_ranking(self, ranking_type: RankingType, limit: int = 10) -> List[tuple]:
        """Récupère le classement des joueurs selon le type spécifié."""
        players = await self.api_client.get_players()
        ranking_data = []
        
        for player in players:
            stats = await self.api_client.get_player_stats(player.player_uuid)
            if stats and stats.kill_data:
                kill_data = stats.kill_data
                score = self.calculate_score(
                    kill_data.player_kills_total,
                    kill_data.deaths_total,
                    ranking_type
                )
                
                ranking_data.append((
                    player.player_name,
                    kill_data.player_kills_total,
                    kill_data.deaths_total,
                    score
                ))
        
        ranking_data.sort(
            key=lambda x: self.get_sort_key(x[3], ranking_type),
            reverse=True
        )
        
        return ranking_data[:limit]
    
    def calculate_score(self, kills: int, deaths: int, ranking_type: RankingType) -> float:
        """Calcule le score selon le type de classement."""
        if ranking_type == RankingType.KDA:
            if deaths > 0:
                return kills / deaths
            elif kills > 0:
                return float('inf')
            return 0.0
        elif ranking_type == RankingType.KILLS:
            return kills
        else:  # DEATHS
            return deaths
    
    def get_sort_key(self, score: float, ranking_type: RankingType) -> float:
        """Retourne la clé de tri selon le type de classement."""
        if ranking_type == RankingType.KDA:
            return score if score != float('inf') else 999999
        return score

async def setup(bot: commands.Bot):
    """Fonction de configuration du Cog."""
    minecraft_cog = MinecraftCog(bot)
    await bot.add_cog(minecraft_cog)
    # Configuration du killfeed si l'ID du canal est disponible
    from config.settings import bot_config
    if hasattr(bot_config, 'minecraft_killfeed_channel_id'):
        await minecraft_cog.setup_killfeed(bot_config.minecraft_killfeed_channel_id) 