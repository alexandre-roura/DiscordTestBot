import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
load_dotenv()

print("Lancement du bot...")
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Variables
WELCOME_CHANNEL = int(os.getenv('WELCOME_CHANNEL'))
BAN_CHANNEL = int(os.getenv('BAN_CHANNEL'))

### Events ###

# On ready
@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    # Sync commands
    try:
        await bot.tree.sync()
        print(f"Commands synced successfully len {len(bot.tree.get_commands())}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# On message
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if message.content.lower().startswith('!hello'):
        await message.author.send('Hello!')
    if message.content.lower().startswith('!welcome'):
        await bot.get_channel(WELCOME_CHANNEL).send(f"Bienvenue {message.author.mention} sur le serveur !")


# On member join
@bot.event
async def on_member_join(member: discord.Member):
    # await member.send(f"Bienvenue sur le serveur !")
    await bot.get_channel(WELCOME_CHANNEL).send(f"Bienvenue {member.mention} sur le serveur !")








### Commands ###

# Hello
@bot.tree.command(name="hello", description="Envoie bonjour à l'utilisateur")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention} !")


# Warn
@bot.tree.command(name="warn", description="Avertir un utilisateur")
async def warn(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.send_message(f"Fais attention à toi ça va te mêler {target.mention} !")


# Ban
@bot.tree.command(name="ban", description="Bannir un utilisateur")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, target: discord.Member, reason: str):
    await interaction.response.send_message(f"L'utilisateur {target.mention} a été banni pour la raison : {reason} !")
    await target.send(f"Tu as été banni pour la raison : {reason} !")
    await target.ban(reason=reason)

# Unban
@bot.tree.command(name="unban", description="Révoque le bannissement d'un utilisateur.")
# On demande au bot d'avoir la permission de bannir pour pouvoir exécuter cette commande.
@app_commands.checks.has_permissions(ban_members=True) 
# On définit le paramètre que l'utilisateur devra fournir
@app_commands.describe(user_id="L'ID de l'utilisateur à débannir.")
async def unban(interaction: discord.Interaction, user_id: str):
    """
    Commande pour débannir un utilisateur en utilisant son ID.
    """
    # On récupère le serveur (guild) où la commande a été exécutée
    guild = interaction.guild

    try:
        # On tente de convertir l'ID fourni (qui est une chaîne) en entier
        banned_user_id = int(user_id)
        
        # On essaie de récupérer l'objet discord.User correspondant à cet ID
        # bot.fetch_user() est nécessaire car l'utilisateur n'est plus dans le serveur.
        user_to_unban = await bot.fetch_user(banned_user_id)

    except ValueError:
        await interaction.response.send_message("L'ID fourni n'est pas valide. Veuillez entrer un ID numérique.", ephemeral=True)
        return
    except discord.NotFound:
         await interaction.response.send_message("Aucun utilisateur trouvé avec cet ID.", ephemeral=True)
         return

    # Maintenant, on tente de révoquer le bannissement
    try:
        await guild.unban(user_to_unban, reason="Débanni via la commande du bot.")
        await interaction.response.send_message(f"✅ L'utilisateur **{user_to_unban.name}** (`{user_to_unban.id}`) a été débanni avec succès.")
    
    except discord.Forbidden:
        # Le bot n'a pas la permission de bannir/débannir des membres
        await interaction.response.send_message("❌ Je n'ai pas la permission de gérer les bannissements sur ce serveur.", ephemeral=True)
    
    except discord.NotFound:
        # L'utilisateur avec cet ID n'était en fait pas dans la liste des bannis
        await interaction.response.send_message(f"L'utilisateur **{user_to_unban.name}** ne semble pas être banni.", ephemeral=True)
        
    except Exception as e:
        # Gestion d'autres erreurs potentielles
        await interaction.response.send_message(f"Une erreur est survenue : {e}", ephemeral=True)

# --- Gestion d'erreur pour les permissions manquantes ---
@unban.error
async def on_unban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
    else:
        # Gérer d'autres types d'erreurs si nécessaire
        await interaction.response.send_message("Une erreur inconnue est survenue.", ephemeral=True)
        raise error


# Kick
@bot.tree.command(name="kick", description="Kick un utilisateur")
async def kick(interaction: discord.Interaction, target: discord.Member, reason: str):
    await interaction.response.send_message(f"L'utilisateur {target.mention} a été kick pour la raison : {reason} !")
    await target.send(f"Tu as été kick pour la raison : {reason} !")
    await target.kick(reason=reason)


# Embed
@bot.tree.command(name="embed", description="Envoie un embed")
async def embed(interaction: discord.Interaction):
    embed = discord.Embed(title="Titre", description="Description", color=discord.Color.blue())
    embed.set_author(name="Auteur", icon_url=interaction.user.avatar.url)
    embed.add_field(name="Python", value="Apprendre le python")
    embed.set_footer(text="Footer")
    embed.set_image(url="https://img.icons8.com/color/512/python.png")
    await interaction.response.send_message(embed=embed)


# Run
bot.run(os.getenv('DISCORD_TOKEN'))
