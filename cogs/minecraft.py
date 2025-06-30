import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from api.minecraft_client import MinecraftAPIClient
from api.models import MinecraftPlayerStats
from utils.helpers import handle_api_errors
from utils.killfeed_manager import KillFeedManager
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
        self.killfeed_channel = None
        self.killfeed_manager = None
    
    async def cog_load(self):
        """Appelé quand le Cog est chargé."""
        await self.api_client.__aenter__()
        # Le canal sera configuré dans setup_killfeed
    
    async def cog_unload(self):
        """Appelé quand le Cog est déchargé."""
        if self.killfeed_manager and self.killfeed_manager.is_monitoring:
            await self.killfeed_manager.stop_monitoring()
        await self.api_client.__aexit__(None, None, None)
    
    async def setup_killfeed(self, channel_id: int):
        """Configure le canal de killfeed."""
        self.killfeed_channel = self.bot.get_channel(channel_id)
        if self.killfeed_channel:
            self.killfeed_manager = KillFeedManager(self.api_client, self.killfeed_channel)
    
    @app_commands.command(name="listminecraftplayers", description="Affiche la liste des joueurs Minecraft")
    @handle_api_errors
    async def list_minecraft_players(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        players = await self.api_client.get_players()
        
        if not players:
            await interaction.followup.send("Aucun joueur trouvé.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="Liste des joueurs Minecraft",
            color=discord.Color.blue()
        )
        
        player_list = "\n".join([f"• {player.player_name}" for player in players])
        embed.add_field(name="Joueurs", value=player_list)
        
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
        
        embed = self.create_stats_embed(player_name, stats)
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
        
        if not ranking_data:
            await interaction.followup.send(
                "Aucun joueur trouvé avec des statistiques de combat.",
                ephemeral=True
            )
            return
        
        embed = self.create_ranking_embed(ranking_data, ranking_enum)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="killfeedstart", description="Démarre le monitoring du killfeed dans le canal dédié")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def killfeed_start(self, interaction: discord.Interaction):
        if not self.killfeed_manager:
            await interaction.response.send_message(
                "❌ Le canal de killfeed n'est pas configuré.",
                ephemeral=True
            )
            return
        
        if self.killfeed_manager.is_monitoring:
            await interaction.response.send_message(
                "Le killfeed est déjà actif !",
                ephemeral=True
            )
            return
        
        await self.killfeed_manager.start_monitoring()
        await interaction.response.send_message("✅ Monitoring du killfeed démarré !")
    
    @app_commands.command(name="killfeedstop", description="Arrête le monitoring du killfeed")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def killfeed_stop(self, interaction: discord.Interaction):
        if not self.killfeed_manager:
            await interaction.response.send_message(
                "❌ Le canal de killfeed n'est pas configuré.",
                ephemeral=True
            )
            return
        
        if not self.killfeed_manager.is_monitoring:
            await interaction.response.send_message(
                "Le killfeed est déjà arrêté !",
                ephemeral=True
            )
            return
        
        await self.killfeed_manager.stop_monitoring()
        await interaction.response.send_message("✅ Monitoring du killfeed arrêté !")
    
    @app_commands.command(name="killfeedstatus", description="Affiche le statut du killfeed")
    async def killfeed_status(self, interaction: discord.Interaction):
        if not self.killfeed_manager:
            status = "❌ Non configuré"
        else:
            status = "✅ Actif" if self.killfeed_manager.is_monitoring else "⏸️ Inactif"
        
        await interaction.response.send_message(f"Statut du killfeed : {status}")
    
    # Méthodes utilitaires
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
        
        if kill_data.deaths_total > 0:
            kdr = kill_data.player_kills_total / kill_data.deaths_total
            kdr_text = f"{kdr:.2f}"
        elif kill_data.player_kills_total > 0:
            kdr_text = "∞ (Aucune mort)"
        else:
            kdr_text = "0.00"
        
        embed.add_field(name="K/D Ratio", value=kdr_text, inline=True)
        return embed
    
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
    
    def create_ranking_embed(self, ranking_data: List[tuple], ranking_type: RankingType) -> discord.Embed:
        """Crée un embed Discord avec le classement des joueurs."""
        titles = {
            RankingType.KDA: ("Ratio K/D", "Classement basé sur le ratio Kill/Death"),
            RankingType.KILLS: ("Nombre de Kills", "Classement basé sur le nombre total de kills"),
            RankingType.DEATHS: ("Nombre de Morts", "Classement basé sur le nombre total de morts")
        }
        
        title, description = titles[ranking_type]
        
        embed = discord.Embed(
            title=f"🏆 Classement des Joueurs Minecraft - {title}",
            description=description,
            color=discord.Color.gold()
        )
        
        if not ranking_data:
            embed.add_field(
                name="Aucune donnée",
                value="Aucun joueur trouvé avec des statistiques de combat.",
                inline=False
            )
            return embed
        
        ranking_text = ""
        for i, (player_name, kills, deaths, score) in enumerate(ranking_data, 1):
            prefix = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"**{i}.**"
            
            if ranking_type == RankingType.KDA:
                score_text = "∞" if score == float('inf') else f"{score:.2f}"
                ranking_text += f"{prefix} **{player_name}**\n"
                ranking_text += f"   Kills: {kills} | Morts: {deaths} | K/D: {score_text}\n\n"
            elif ranking_type == RankingType.DEATHS:
                ranking_text += f"{prefix} **{player_name}** - {deaths} Morts\n\n"
            else:  # KILLS
                ranking_text += f"{prefix} **{player_name}** - {kills} Kills\n\n"
        
        embed.add_field(
            name="Classement",
            value=ranking_text,
            inline=False
        )
        
        embed.set_footer(text="Mis à jour automatiquement")
        embed.timestamp = discord.utils.utcnow()
        
        return embed

async def setup(bot: commands.Bot):
    """Fonction de configuration du Cog."""
    minecraft_cog = MinecraftCog(bot)
    await bot.add_cog(minecraft_cog)
    # Configuration du killfeed si l'ID du canal est disponible
    from config.settings import bot_config
    if hasattr(bot_config, 'minecraft_killfeed_channel_id'):
        await minecraft_cog.setup_killfeed(bot_config.minecraft_killfeed_channel_id) 