import discord
from .embed_theme import EmbedTheme

class ModerationViews:
    """Classe pour la création des embeds de modération."""
    
    @staticmethod
    def create_warn_embed(target: discord.Member) -> discord.Embed:
        """Crée l'embed pour un avertissement."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['warning']} Avertissement",
            description=f"Fais attention à toi ça va te mêler {target.mention} !",
            color=EmbedTheme.WARNING_COLOR
        )
        
        embed.set_footer(text=f"ID: {target.id}")
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @staticmethod
    def create_ban_embed(target: discord.Member, reason: str) -> discord.Embed:
        """Crée l'embed pour un bannissement."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['error']} Bannissement",
            description=f"L'utilisateur {target.mention} a été banni.",
            color=EmbedTheme.ERROR_COLOR
        )
        
        embed.add_field(
            name="Raison",
            value=reason,
            inline=False
        )
        
        embed.set_footer(text=f"ID: {target.id}")
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @staticmethod
    def create_unban_embed(user: discord.User) -> discord.Embed:
        """Crée l'embed pour un débannissement."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['success']} Débannissement",
            description=f"L'utilisateur **{user.name}** (`{user.id}`) a été débanni avec succès.",
            color=EmbedTheme.SUCCESS_COLOR
        )
        
        embed.timestamp = discord.utils.utcnow()
        return embed
    
    @staticmethod
    def create_kick_embed(target: discord.Member, reason: str) -> discord.Embed:
        """Crée l'embed pour une expulsion."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['warning']} Expulsion",
            description=f"L'utilisateur {target.mention} a été expulsé.",
            color=EmbedTheme.WARNING_COLOR
        )
        
        embed.add_field(
            name="Raison",
            value=reason,
            inline=False
        )
        
        embed.set_footer(text=f"ID: {target.id}")
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @staticmethod
    def create_error_embed(error_message: str) -> discord.Embed:
        """Crée l'embed pour une erreur."""
        embed = discord.Embed(
            title=f"{EmbedTheme.ICONS['error']} Erreur",
            description=error_message,
            color=EmbedTheme.ERROR_COLOR
        )
        
        embed.timestamp = discord.utils.utcnow()
        return embed 