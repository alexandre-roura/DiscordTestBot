import discord
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from api.models import MinecraftPlayer, MinecraftPlayerStats, KillEvent
from cogs.minecraft import RankingType
from .embed_theme import EmbedTheme

class MinecraftViews:
    """Classe pour la création des embeds Minecraft."""
    
    @staticmethod
    def create_player_list_embed(players: List[MinecraftPlayer]) -> discord.Embed:
        """Crée l'embed pour la liste des joueurs."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['player']} Liste des joueurs Minecraft",
            color=EmbedTheme.MINECRAFT_COLOR
        )
        
        if not players:
            embed.description = f"{EmbedTheme.ICONS['info']} Aucun joueur trouvé."
            return embed
        
        player_list = "\n".join([f"• {player.player_name}" for player in players])
        embed.add_field(name="Joueurs", value=player_list)
        
        embed.set_footer(text=f"Total: {len(players)} joueurs")
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @staticmethod
    def create_stats_embed(player_name: str, stats: MinecraftPlayerStats) -> discord.Embed:
        """Crée l'embed pour les stats d'un joueur."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['stats']} Stats de {player_name}",
            description=f"Statistiques de combat de {player_name}",
            color=EmbedTheme.STATS_COLOR
        )
        
        kill_data = stats.kill_data
        
        # Stats de kills
        embed.add_field(
            name=f"{EmbedTheme.ICONS['kills']} Kills (Joueurs)",
            value=kill_data.player_kills_total,
            inline=True
        )
        
        # Stats de morts
        embed.add_field(
            name=f"{EmbedTheme.ICONS['deaths']} Morts",
            value=kill_data.deaths_total,
            inline=True
        )
        
        # Calcul et affichage du KDR
        if kill_data.deaths_total > 0:
            kdr = kill_data.player_kills_total / kill_data.deaths_total
            kdr_text = f"{kdr:.2f}"
        elif kill_data.player_kills_total > 0:
            kdr_text = "∞ (Aucune mort)"
        else:
            kdr_text = "0.00"
        
        embed.add_field(
            name=f"{EmbedTheme.ICONS['kd_ratio']} K/D Ratio",
            value=kdr_text,
            inline=True
        )
        
        embed.set_footer(text="Mis à jour")
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @staticmethod
    def create_ranking_embed(
        ranking_data: List[tuple],
        ranking_type: RankingType
    ) -> discord.Embed:
        """Crée l'embed pour le classement."""
        titles = {
            RankingType.KDA: ("Ratio K/D", "Classement basé sur le ratio Kill/Death"),
            RankingType.KILLS: ("Nombre de Kills", "Classement basé sur le nombre total de kills"),
            RankingType.DEATHS: ("Nombre de Morts", "Classement basé sur le nombre total de morts")
        }
        
        title, description = titles[ranking_type]
        
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['stats']} Classement des Joueurs Minecraft - {title}",
            description=description,
            color=EmbedTheme.RANKING_COLOR
        )
        
        if not ranking_data:
            embed.add_field(
                name="Aucune donnée",
                value=f"{EmbedTheme.ICONS['info']} Aucun joueur trouvé avec des statistiques de combat.",
                inline=False
            )
            return embed
        
        ranking_text = ""
        for i, (player_name, kills, deaths, score) in enumerate(ranking_data, 1):
            prefix = EmbedTheme.get_ranking_prefix(i)
            
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
    
    @staticmethod
    def create_killfeed_embed(kill_event: KillEvent) -> discord.Embed:
        """Crée l'embed pour un événement de kill."""
        weapon_emoji = EmbedTheme.get_weapon_emoji(kill_event.weapon)
        
        embed = discord.Embed(
            title=f"{weapon_emoji} Nouveau Kill !",
            color=EmbedTheme.KILLFEED_COLOR
        )
        
        # Description du kill
        embed.description = f"**{kill_event.killer}** a tué **{kill_event.victim}**"
        
        # Détails
        embed.add_field(
            name="Arme",
            value=f"{weapon_emoji} {kill_event.weapon}",
            inline=True
        )
        
        embed.add_field(
            name="Distance",
            value=f"📏 {kill_event.distance:.1f}m",
            inline=True
        )
        
        # Timestamp
        kill_time = datetime.fromtimestamp(kill_event.timestamp)
        embed.timestamp = kill_time
        
        return embed
    
    @staticmethod
    def create_killfeed_status_embed(is_active: bool, is_configured: bool) -> discord.Embed:
        """Crée l'embed pour le statut du killfeed."""
        if not is_configured:
            status = f"{EmbedTheme.ICONS['error']} Non configuré"
            color = EmbedTheme.ERROR_COLOR
        else:
            status = f"{EmbedTheme.ICONS['success']} Actif" if is_active else f"{EmbedTheme.ICONS['warning']} Inactif"
            color = EmbedTheme.SUCCESS_COLOR if is_active else EmbedTheme.WARNING_COLOR
        
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['info']} Statut du Killfeed",
            description=f"État actuel : {status}",
            color=color
        )
        
        embed.timestamp = discord.utils.utcnow()
        return embed 