import discord
from typing import Dict

class EmbedTheme:
    """Configuration des styles d'embed."""
    
    # Couleurs standard
    SUCCESS_COLOR = discord.Color.green()
    ERROR_COLOR = discord.Color.red()
    INFO_COLOR = discord.Color.blue()
    WARNING_COLOR = discord.Color.yellow()
    
    # Couleurs spécifiques
    MINECRAFT_COLOR = discord.Color.dark_green()
    RANKING_COLOR = discord.Color.gold()
    STATS_COLOR = discord.Color.blue()
    KILLFEED_COLOR = discord.Color.dark_red()
    
    # Emojis
    RANKING_EMOJIS = {
        1: "🥇",
        2: "🥈",
        3: "🥉"
    }
    
    # Emojis pour le killfeed
    WEAPON_EMOJIS = {
        "sword": "⚔️",
        "bow": "🏹",
        "trident": "🔱",
        "axe": "🪓",
        "default": "💥"
    }
    
    # Icônes
    ICONS = {
        "stats": "📊",
        "player": "👤",
        "kills": "⚔️",
        "deaths": "💀",
        "kd_ratio": "📈",
        "warning": "⚠️",
        "success": "✅",
        "error": "❌",
        "info": "ℹ️",
        "time": "⏰"
    }
    
    @classmethod
    def get_ranking_prefix(cls, position: int) -> str:
        """Retourne le préfixe (emoji ou numéro) pour une position donnée."""
        return cls.RANKING_EMOJIS.get(position, f"**{position}.**")
    
    @classmethod
    def get_weapon_emoji(cls, weapon: str) -> str:
        """Retourne l'emoji correspondant à une arme."""
        return cls.WEAPON_EMOJIS.get(weapon.lower(), cls.WEAPON_EMOJIS["default"]) 