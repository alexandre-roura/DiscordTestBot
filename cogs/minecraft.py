import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from api.minecraft_client import MinecraftAPIClient
from api.models import MinecraftPlayerStats, RankingType
from utils.helpers import handle_api_errors
from services.killfeed_service import KillFeedService
from services.google_sheets_service import GoogleSheetsService
from views.minecraft_views import MinecraftViews
from enum import Enum
from config.settings import bot_config

class MinecraftCog(commands.Cog):
    """Cog pour les commandes Minecraft."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_client = MinecraftAPIClient()
        self.killfeed = None
        self.sheets_service = GoogleSheetsService()
    
    async def cog_load(self):
        """Appelé quand le Cog est chargé."""
        await self.api_client.__aenter__()
        # Configuration du killfeed avec le canal configuré
        if bot_config.minecraft_killfeed_channel_id:
            channel = self.bot.get_channel(bot_config.minecraft_killfeed_channel_id)
            if channel:
                self.killfeed = KillFeedService(self.api_client, channel)
    
    async def cog_unload(self):
        """Appelé quand le Cog est déchargé."""
        if self.killfeed:
            await self.killfeed.stop_monitoring()
        await self.api_client.__aexit__(None, None, None)

    
    ### Liste des joueurs ###
    @app_commands.command(name="listminecraftplayers", description="Affiche la liste des joueurs Minecraft")
    @handle_api_errors
    async def list_minecraft_players(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        players = await self.api_client.get_players()
        embed = MinecraftViews.create_player_list_embed(players)
        await interaction.followup.send(embed=embed)
    


    ### Stats ###
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



    ### Ranking ###
    @app_commands.command(name="minecraftranking", description="Affiche le classement des joueurs Minecraft")
    @app_commands.describe(
        ranking_type="Type de classement (kd_ratio/kills/deaths)",
        limit="Nombre de joueurs à afficher (défaut: 10, max: 25)"
    )
    @app_commands.choices(ranking_type=[
        app_commands.Choice(name="Ratio K/D", value="kd_ratio"),
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
                "Type de classement invalide. Utilisez 'kd_ratio', 'kills' ou 'deaths'.",
                ephemeral=True
            )
            return
        
        ranking_data = await self.get_players_ranking(ranking_enum, limit)
        
        # Mettre à jour le classement dans Google Sheets
        print("Mise à jour du classement dans Google Sheets...")
        self.sheets_service.update_ranking(ranking_data)
        print("Mise à jour du classement dans Google Sheets terminée.")
        
        embed = MinecraftViews.create_ranking_embed(ranking_data, ranking_enum)
        await interaction.followup.send(embed=embed)




    ### Killfeed ###
    @app_commands.command(name="killfeed", description="Active/désactive le suivi des kills dans le canal configuré")
    @app_commands.describe(action="Action à effectuer (start/stop)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Démarrer", value="start"),
        app_commands.Choice(name="Arrêter", value="stop")
    ])
    @handle_api_errors
    async def toggle_killfeed(self, interaction: discord.Interaction, action: str):
        """Active/désactive le suivi des kills dans le canal configuré."""
        await interaction.response.defer()

        # Vérifier si le canal est configuré
        if not bot_config.minecraft_killfeed_channel_id:
            await interaction.followup.send("❌ Le canal de killfeed n'est pas configuré dans les paramètres.", ephemeral=True)
            return

        # Vérifier si l'utilisateur est dans le bon canal
        if interaction.channel_id != bot_config.minecraft_killfeed_channel_id:
            channel = self.bot.get_channel(bot_config.minecraft_killfeed_channel_id)
            if channel:
                await interaction.followup.send(f"❌ Cette commande doit être utilisée dans le canal {channel.mention}.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Le canal configuré n'est pas accessible.", ephemeral=True)
            return

        if action.lower() == "start":
            if not self.killfeed:
                self.killfeed = KillFeedService(self.api_client, interaction.channel)
            success, message = await self.killfeed.start_monitoring()
        
        elif action.lower() == "stop":
            if not self.killfeed:
                await interaction.followup.send("❌ Le killfeed n'est pas initialisé.", ephemeral=True)
                return
            success, message = await self.killfeed.stop_monitoring()
        
        else:
            await interaction.followup.send("❌ Action invalide. Utilisez 'start' ou 'stop'.", ephemeral=True)
            return

        await interaction.followup.send("✅ " + message if success else "❌ " + message)
    
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
        if ranking_type == RankingType.KD_RATIO:
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
        if ranking_type == RankingType.KD_RATIO:
            return score if score != float('inf') else 999999
        return score

async def setup(bot: commands.Bot):
    """Fonction de configuration du Cog."""
    minecraft_cog = MinecraftCog(bot)
    await bot.add_cog(minecraft_cog) 