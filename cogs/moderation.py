import discord
from discord import app_commands
from discord.ext import commands

class ModerationCog(commands.Cog):
    """Cog pour les commandes de modération."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="warn", description="Avertir un utilisateur")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, target: discord.Member):
        """Commande pour avertir un utilisateur."""
        await interaction.response.send_message(
            f"Fais attention à toi ça va te mêler {target.mention} !"
        )
    
    @app_commands.command(name="ban", description="Bannir un utilisateur")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, target: discord.Member, reason: str):
        """Commande pour bannir un utilisateur."""
        await interaction.response.send_message(
            f"L'utilisateur {target.mention} a été banni pour la raison : {reason} !"
        )
        await target.send(f"Tu as été banni pour la raison : {reason} !")
        await target.ban(reason=reason)
    
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
            await interaction.response.send_message(
                "L'ID fourni n'est pas valide. Veuillez entrer un ID numérique.",
                ephemeral=True
            )
            return
        except discord.NotFound:
            await interaction.response.send_message(
                "Aucun utilisateur trouvé avec cet ID.",
                ephemeral=True
            )
            return
        
        try:
            await guild.unban(user_to_unban, reason="Débanni via la commande du bot.")
            await interaction.response.send_message(
                f"✅ L'utilisateur **{user_to_unban.name}** (`{user_to_unban.id}`) a été débanni avec succès."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas la permission de gérer les bannissements sur ce serveur.",
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                f"L'utilisateur **{user_to_unban.name}** ne semble pas être banni.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Une erreur est survenue : {e}",
                ephemeral=True
            )
    
    @app_commands.command(name="kick", description="Kick un utilisateur")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, target: discord.Member, reason: str):
        """Commande pour kick un utilisateur."""
        await interaction.response.send_message(
            f"L'utilisateur {target.mention} a été kick pour la raison : {reason} !"
        )
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
            await interaction.response.send_message(
                "Vous n'avez pas la permission d'utiliser cette commande.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Une erreur inconnue est survenue.",
                ephemeral=True
            )
            raise error

async def setup(bot: commands.Bot):
    """Fonction de configuration du Cog."""
    await bot.add_cog(ModerationCog(bot)) 