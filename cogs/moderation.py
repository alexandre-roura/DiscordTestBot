import discord
from discord import app_commands
from discord.ext import commands
from views.moderation_views import ModerationViews

class ModerationCog(commands.Cog):
    """Cog pour les commandes de modération."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    ### Warn ###
    @app_commands.command(name="warn", description="Avertir un utilisateur")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, target: discord.Member):
        """Commande pour avertir un utilisateur."""
        embed = ModerationViews.create_warn_embed(target)
        await interaction.response.send_message(embed=embed)
    

    ### Ban ###
    @app_commands.command(name="ban", description="Bannir un utilisateur")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, target: discord.Member, reason: str):
        """Commande pour bannir un utilisateur."""
        embed = ModerationViews.create_ban_embed(target, reason)
        await interaction.response.send_message(embed=embed)
        await target.send(f"Tu as été banni pour la raison : {reason} !")
        await target.ban(reason=reason)
    

    ### Unban ###
    @app_commands.command(name="unban", description="Révoque le bannissement d'un utilisateur")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user_id="L'ID de l'utilisateur à débannir")
    async def unban(self, interaction: discord.Interaction, user_id: str):
        """Commande pour débannir un utilisateur."""
        guild = interaction.guild
        
        try:
            banned_user_id = int(user_id)
            user_to_unban = await self.bot.fetch_user(banned_user_id)
        except ValueError:
            error_embed = ModerationViews.create_error_embed(
                "L'ID fourni n'est pas valide. Veuillez entrer un ID numérique."
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        except discord.NotFound:
            error_embed = ModerationViews.create_error_embed(
                "Aucun utilisateur trouvé avec cet ID."
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        
        try:
            await guild.unban(user_to_unban, reason="Débanni via la commande du bot.")
            embed = ModerationViews.create_unban_embed(user_to_unban)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            error_embed = ModerationViews.create_error_embed(
                "❌ Je n'ai pas la permission de gérer les bannissements sur ce serveur."
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        except discord.NotFound:
            error_embed = ModerationViews.create_error_embed(
                f"L'utilisateur **{user_to_unban.name}** ne semble pas être banni."
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        except Exception as e:
            error_embed = ModerationViews.create_error_embed(f"Une erreur est survenue : {e}")
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick un utilisateur")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, target: discord.Member, reason: str):
        """Commande pour kick un utilisateur."""
        embed = ModerationViews.create_kick_embed(target, reason)
        await interaction.response.send_message(embed=embed)
        await target.send(f"Tu as été kick pour la raison : {reason} !")
        await target.kick(reason=reason)
    
    # Gestionnaires d'erreurs
    @warn.error
    @ban.error
    @unban.error
    @kick.error
    async def moderation_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gestion des erreurs pour les commandes de modération."""
        if isinstance(error, app_commands.errors.MissingPermissions):
            error_embed = ModerationViews.create_error_embed(
                "Vous n'avez pas la permission d'utiliser cette commande."
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        else:
            error_embed = ModerationViews.create_error_embed("Une erreur inconnue est survenue.")
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            raise error

async def setup(bot: commands.Bot):
    """Fonction de configuration du Cog."""
    await bot.add_cog(ModerationCog(bot)) 