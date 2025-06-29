import discord
from discord import app_commands
from typing import Optional

class ModerationCommands:
    """Gestionnaire des commandes de modération."""
    
    @staticmethod
    async def warn_command(interaction: discord.Interaction, target: discord.Member) -> None:
        """Commande pour avertir un utilisateur."""
        await interaction.response.send_message(
            f"Fais attention à toi ça va te mêler {target.mention} !"
        )
    
    @staticmethod
    async def ban_command(interaction: discord.Interaction, target: discord.Member, reason: str) -> None:
        """Commande pour bannir un utilisateur."""
        await interaction.response.send_message(
            f"L'utilisateur {target.mention} a été banni pour la raison : {reason} !"
        )
        await target.send(f"Tu as été banni pour la raison : {reason} !")
        await target.ban(reason=reason)
    
    @staticmethod
    async def unban_command(interaction: discord.Interaction, user_id: str) -> None:
        """Commande pour débannir un utilisateur."""
        guild = interaction.guild
        
        try:
            banned_user_id = int(user_id)
            user_to_unban = await interaction.client.fetch_user(banned_user_id)
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
    
    @staticmethod
    async def kick_command(interaction: discord.Interaction, target: discord.Member, reason: str) -> None:
        """Commande pour kick un utilisateur."""
        await interaction.response.send_message(
            f"L'utilisateur {target.mention} a été kick pour la raison : {reason} !"
        )
        await target.send(f"Tu as été kick pour la raison : {reason} !")
        await target.kick(reason=reason) 