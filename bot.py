import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Import des modules refactorisés
from api.minecraft_client import MinecraftAPIClient
from commands.minecraft_commands import MinecraftCommands, RankingType
from commands.moderation_commands import ModerationCommands
from config.settings import bot_config
from utils.helpers import setup_logging

# Configuration du logging
setup_logging()

# Chargement des variables d'environnement
load_dotenv()

class DiscordBot(commands.Bot):
    """Bot Discord avec architecture modulaire."""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=bot_config.command_prefix, intents=intents)
        
        # Initialisation des clients
        self.minecraft_client = MinecraftAPIClient()
        
        # Récupération du canal de killfeed
        self.killfeed_channel = None  # Sera défini après la connexion
        
        # Initialisation temporaire sans canal
        self.minecraft_commands = None
        self.moderation_commands = ModerationCommands()
    
    async def setup_hook(self):
        """Configuration initiale du bot."""
        await self.minecraft_client.__aenter__()
        print("Lancement du bot...")
    
    async def close(self):
        """Nettoyage à la fermeture."""
        await self.minecraft_client.__aexit__(None, None, None)
        await super().close()

# Instance du bot
bot = DiscordBot()

### Events ###

@bot.event
async def on_ready():
    """Événement déclenché quand le bot est prêt."""
    print(f'Bot connecté en tant que {bot.user}')
    
    # Récupération du canal de killfeed
    bot.killfeed_channel = bot.get_channel(bot_config.minecraft_killfeed_channel_id)
    if not bot.killfeed_channel:
        print(f"⚠️ Canal de killfeed (ID: {bot_config.minecraft_killfeed_channel_id}) introuvable.")
        # Créer une instance sans canal (les commandes killfeed ne fonctionneront pas)
        bot.minecraft_commands = MinecraftCommands(bot.minecraft_client, None)
    else:
        # Initialisation de MinecraftCommands avec le canal
        bot.minecraft_commands = MinecraftCommands(bot.minecraft_client, bot.killfeed_channel)
    
    # Synchronisation des commandes
    try:
        await bot.tree.sync()
        print(f"Commands synced successfully - {len(bot.tree.get_commands())} commandes")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message: discord.Message):
    """Événement déclenché à chaque message."""
    if message.author == bot.user:
        return

    if message.content.lower().startswith('!hello'):
        await message.author.send('Hello!')
    
    if message.content.lower().startswith('!welcome') and bot_config.welcome_channel_id:
        channel = bot.get_channel(bot_config.welcome_channel_id)
        if channel:
            await channel.send(f"Bienvenue {message.author.mention} sur le serveur !")

@bot.event
async def on_member_join(member: discord.Member):
    """Événement déclenché quand un membre rejoint le serveur."""
    if bot_config.welcome_channel_id:
        channel = bot.get_channel(bot_config.welcome_channel_id)
        if channel:
            await channel.send(f"Bienvenue {member.mention} sur le serveur !")

### Commands ###

@bot.tree.command(name="hello", description="Envoie bonjour à l'utilisateur")
async def hello(interaction: discord.Interaction):
    """Commande de salutation."""
    await interaction.response.send_message(f"Hello {interaction.user.mention} !")

@bot.tree.command(name="warn", description="Avertir un utilisateur")
async def warn(interaction: discord.Interaction, target: discord.Member):
    """Commande pour avertir un utilisateur."""
    await bot.moderation_commands.warn_command(interaction, target)

@bot.tree.command(name="ban", description="Bannir un utilisateur")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, target: discord.Member, reason: str):
    """Commande pour bannir un utilisateur."""
    await bot.moderation_commands.ban_command(interaction, target, reason)

@bot.tree.command(name="unban", description="Révoque le bannissement d'un utilisateur.")
@app_commands.checks.has_permissions(ban_members=True) 
@app_commands.describe(user_id="L'ID de l'utilisateur à débannir.")
async def unban(interaction: discord.Interaction, user_id: str):
    """Commande pour débannir un utilisateur."""
    await bot.moderation_commands.unban_command(interaction, user_id)

@unban.error
async def on_unban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestion d'erreur pour la commande unban."""
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

@bot.tree.command(name="kick", description="Kick un utilisateur")
async def kick(interaction: discord.Interaction, target: discord.Member, reason: str):
    """Commande pour kick un utilisateur."""
    await bot.moderation_commands.kick_command(interaction, target, reason)


@bot.tree.command(name="listminecraftplayers", description="Affiche la liste des joueurs Minecraft")
async def list_minecraft_players(interaction: discord.Interaction):
    """Commande pour afficher la liste des joueurs Minecraft."""
    await interaction.response.defer()  # Réponse différée pour les requêtes longues
    
    try:
        players = await bot.minecraft_commands.get_players()
        
        if not players:
            await interaction.followup.send(
                "Aucun joueur trouvé.",
                ephemeral=True
            )
            return
            
        # Création de l'embed
        embed = discord.Embed(
            title="Liste des joueurs Minecraft",
            color=discord.Color.blue()
        )
        
        # Ajout des joueurs à l'embed
        player_list = "\n".join([f"• {player.player_name}" for player in players])
        embed.add_field(name="Joueurs", value=player_list)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(
            f"Une erreur est survenue: {str(e)}",
            ephemeral=True
        )



@bot.tree.command(name="statsminecraftforplayer", description="Affiche les stats minecraft d'un joueur")
async def stats_minecraft_for_player(interaction: discord.Interaction, player_name: str):
    """Commande pour afficher les stats Minecraft d'un joueur."""
    await interaction.response.defer()  # Réponse différée pour les requêtes longues
    
    try:
        stats = await bot.minecraft_commands.get_player_stats_by_name(player_name)
        
        if stats is None:
            await interaction.followup.send(
                f"Le joueur {player_name} n'a pas été trouvé.",
                ephemeral=True
            )
            return
        
        embed = bot.minecraft_commands.create_stats_embed(player_name, stats)
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(
            f"Une erreur est survenue: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="minecraftranking", description="Affiche le classement des joueurs Minecraft")
@app_commands.describe(
    ranking_type="Type de classement (kda/kills)",
    limit="Nombre de joueurs à afficher (défaut: 10, max: 25)"
)
@app_commands.choices(ranking_type=[
    app_commands.Choice(name="Ratio K/D", value="kda"),
    app_commands.Choice(name="Nombre de Kills", value="kills"),
    app_commands.Choice(name="Nombre de Morts", value="deaths")
])
async def minecraft_ranking(interaction: discord.Interaction, ranking_type: str, limit: int = 10):
    """Commande pour afficher le classement des joueurs Minecraft."""
    await interaction.response.defer()  # Réponse différée pour les requêtes longues
    
    # Validation du paramètre limit
    if limit < 1 or limit > 25:
        await interaction.followup.send(
            "Le nombre de joueurs doit être entre 1 et 25.",
            ephemeral=True
        )
        return
    
    # Conversion du type de classement
    try:
        ranking_enum = RankingType(ranking_type)
    except ValueError:
        await interaction.followup.send(
            "Type de classement invalide. Utilisez 'kda', 'kills' ou 'deaths'.",
            ephemeral=True
        )
        return
    
    try:
        ranking_data = await bot.minecraft_commands.get_players_ranking(ranking_enum, limit)
        
        if not ranking_data:
            await interaction.followup.send(
                "Aucun joueur trouvé avec des statistiques de combat.",
                ephemeral=True
            )
            return
        
        embed = bot.minecraft_commands.create_ranking_embed(ranking_data, ranking_enum)
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(
            f"Une erreur est survenue lors de la récupération du classement: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(name="killfeedstart", description="Démarre le monitoring du killfeed dans le canal dédié")
@app_commands.checks.has_permissions(manage_channels=True)
async def killfeed_start(interaction: discord.Interaction):
    """Commande pour démarrer le monitoring du killfeed."""
    await interaction.response.defer()
    
    try:
        success, message = await bot.minecraft_commands.start_killfeed()
        
        if success:
            embed = discord.Embed(
                title="✅ Killfeed Démarré",
                description=message,
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⚠️ Killfeed Déjà Actif",
                description=message,
                color=discord.Color.orange()
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(
            f"Une erreur est survenue lors du démarrage du killfeed: {str(e)}",
            ephemeral=True
        )

@killfeed_start.error
async def on_killfeed_start_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestion d'erreur pour la commande killfeedstart."""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "Vous n'avez pas la permission de gérer les canaux pour utiliser cette commande.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Une erreur inconnue est survenue.",
            ephemeral=True
        )
        raise error

@bot.tree.command(name="killfeedstop", description="Arrête le monitoring du killfeed")
@app_commands.checks.has_permissions(manage_channels=True)
async def killfeed_stop(interaction: discord.Interaction):
    """Commande pour arrêter le monitoring du killfeed."""
    await interaction.response.defer()
    
    try:
        success, message = await bot.minecraft_commands.stop_killfeed()
        
        if success:
            embed = discord.Embed(
                title="🛑 Killfeed Arrêté",
                description=message,
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="⚠️ Killfeed Non Actif",
                description=message,
                color=discord.Color.orange()
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(
            f"Une erreur est survenue lors de l'arrêt du killfeed: {str(e)}",
            ephemeral=True
        )

@killfeed_stop.error
async def on_killfeed_stop_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestion d'erreur pour la commande killfeedstop."""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "Vous n'avez pas la permission de gérer les canaux pour utiliser cette commande.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Une erreur inconnue est survenue.",
            ephemeral=True
        )
        raise error

@bot.tree.command(name="killfeedstatus", description="Affiche le statut du killfeed")
async def killfeed_status(interaction: discord.Interaction):
    """Commande pour afficher le statut du killfeed."""
    is_active = bot.minecraft_commands.is_killfeed_active()
    
    if is_active:
        embed = discord.Embed(
            title="🟢 Killfeed Actif",
            description=f"Le monitoring du killfeed est en cours dans {bot.killfeed_channel.mention}",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="🔴 Killfeed Inactif",
            description=f"Le monitoring du killfeed n'est pas actif.",
            color=discord.Color.red()
        )
    
    await interaction.response.send_message(embed=embed)

# Point d'entrée principal
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
