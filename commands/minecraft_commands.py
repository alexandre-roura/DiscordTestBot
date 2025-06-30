from typing import Optional, List, Callable
import discord
from discord import app_commands
from api.minecraft_client import MinecraftAPIClient, APIError, KillEvent
from api.models import MinecraftPlayerStats
from utils.helpers import handle_api_errors
from utils.killfeed_manager import KillFeedManager
from config.settings import bot_config
from enum import Enum

class RankingType(Enum):
    """Types de classements disponibles."""
    KDA = "kda"
    KILLS = "kills"
    DEATHS = "deaths"

class RankingCriteria:
    """Critères de classement avec leurs fonctions de calcul et de tri."""
    
    def __init__(self, name: str, description: str, 
                 calculate_score: Callable, sort_key: Callable):
        self.name = name
        self.description = description
        self.calculate_score = calculate_score
        self.sort_key = sort_key

class MinecraftCommands:
    """Gestionnaire des commandes Minecraft."""
    
    def __init__(self, api_client: MinecraftAPIClient, killfeed_channel: discord.TextChannel):
        self.api_client = api_client
        self._ranking_criteria = self._initialize_ranking_criteria()
        self.killfeed_manager = KillFeedManager(api_client, killfeed_channel)
    
    def _initialize_ranking_criteria(self) -> dict:
        """Initialise les critères de classement."""
        return {
            RankingType.KDA: RankingCriteria(
                name="Ratio K/D",
                description="Classement basé sur le ratio Kill/Death",
                calculate_score=self._calculate_kda_score,
                sort_key=self._kda_sort_key
            ),
            RankingType.KILLS: RankingCriteria(
                name="Nombre de Kills",
                description="Classement basé sur le nombre total de kills",
                calculate_score=self._calculate_kills_score,
                sort_key=self._kills_sort_key
            ),
            RankingType.DEATHS: RankingCriteria(
                name="Nombre de Morts",
                description="Classement basé sur le nombre total de morts",
                calculate_score=self._calculate_deaths_score,
                sort_key=self._deaths_sort_key
            )
        }
    
    def _calculate_kda_score(self, kills: int, deaths: int) -> float:
        """Calcule le score KDA."""
        if deaths > 0:
            return kills / deaths
        elif kills > 0:
            return float('inf')
        return 0.0
    
    def _calculate_kills_score(self, kills: int, deaths: int) -> int:
        """Calcule le score basé sur les kills."""
        return kills
    
    def _calculate_deaths_score(self, kills: int, deaths: int) -> int:
        """Calcule le score basé sur les deaths."""
        return deaths
    
    def _kda_sort_key(self, score: float) -> float:
        """Clé de tri pour KDA (infini = très haut score)."""
        return score if score != float('inf') else 999999
    
    def _kills_sort_key(self, score: int) -> int:
        """Clé de tri pour les kills."""
        return score
    
    def _deaths_sort_key(self, score: int) -> int:
        """Clé de tri pour les deaths."""
        return score
    
    @handle_api_errors
    async def get_players(self):
        """Récupère la liste des joueurs."""
        return await self.api_client.get_players()
    
    @handle_api_errors
    async def get_player_stats(self, player_uuid: str) -> Optional[MinecraftPlayerStats]:
        """Récupère les stats d'un joueur par son UUID."""
        return await self.api_client.get_player_stats(player_uuid)

    @handle_api_errors
    async def get_players_ranking(self, ranking_type: RankingType, limit: int = 10) -> List[tuple]:
        """Récupère le classement des joueurs selon le type spécifié."""
        players = await self.get_players()
        ranking_data = []
        criteria = self._ranking_criteria[ranking_type]
        
        for player in players:
            stats = await self.get_player_stats(player.player_uuid)
            if stats and stats.kill_data:
                kill_data = stats.kill_data
                score = criteria.calculate_score(
                    kill_data.player_kills_total, 
                    kill_data.deaths_total
                )
                
                ranking_data.append((
                    player.player_name,
                    kill_data.player_kills_total,
                    kill_data.deaths_total,
                    score
                ))
        
        # Tri selon les critères spécifiés
        ranking_data.sort(
            key=lambda x: criteria.sort_key(x[3]), 
            reverse=True
        )
        
        return ranking_data[:limit]

    def create_ranking_embed(self, ranking_data: List[tuple], ranking_type: RankingType) -> discord.Embed:
        """Crée un embed Discord avec le classement des joueurs."""
        criteria = self._ranking_criteria[ranking_type]
        
        embed = discord.Embed(
            title=f"🏆 Classement des Joueurs Minecraft - {criteria.name}",
            description=criteria.description,
            color=discord.Color.gold()
        )
        
        if not ranking_data:
            embed.add_field(
                name="Aucune donnée",
                value="Aucun joueur trouvé avec des statistiques de combat.",
                inline=False
            )
            return embed
        
        # Création du classement
        ranking_text = ""
        for i, (player_name, kills, deaths, score) in enumerate(ranking_data, 1):
            # Emojis pour les 3 premiers
            if i == 1:
                prefix = "🥇"
            elif i == 2:
                prefix = "🥈"
            elif i == 3:
                prefix = "🥉"
            else:
                prefix = f"**{i}.**"
            
            # Formatage selon le type de classement
            if ranking_type == RankingType.KDA:
                # Pour KDA : afficher kills, morts et K/D
                if score == float('inf'):
                    score_text = "∞"
                else:
                    score_text = f"{score:.2f}"
                ranking_text += f"{prefix} **{player_name}**\n"
                ranking_text += f"   Kills: {kills} | Morts: {deaths} | K/D: {score_text}\n\n"
            elif ranking_type == RankingType.DEATHS:
                # Pour DEATHS : afficher seulement les morts
                ranking_text += f"{prefix} **{player_name}** - {deaths} Morts\n\n"
            else:  # KILLS
                # Pour KILLS : afficher seulement les kills
                ranking_text += f"{prefix} **{player_name}** - {kills} Kills\n\n"
        
        embed.add_field(
            name="Classement",
            value=ranking_text,
            inline=False
        )
        
        embed.set_footer(text="Mis à jour automatiquement")
        embed.timestamp = discord.utils.utcnow()
        
        return embed

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

    async def start_killfeed(self):
        """Démarre le monitoring du killfeed."""
        return await self.killfeed_manager.start_monitoring()
    
    async def stop_killfeed(self):
        """Arrête le monitoring du killfeed."""
        return await self.killfeed_manager.stop_monitoring()
    
    def is_killfeed_active(self) -> bool:
        """Vérifie si le killfeed est actif."""
        return self.killfeed_manager.is_monitoring 