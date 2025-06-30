import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
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
    
    async def setup_hook(self):
        """Configuration initiale du bot."""
        # Chargement des Cogs
        await self.load_extension("cogs.minecraft")
        await self.load_extension("cogs.moderation")
        print("Cogs chargés avec succès.")
        
        # Synchronisation des commandes
        try:
            await self.tree.sync()
            print(f"Commandes synchronisées avec succès - {len(self.tree.get_commands())} commandes")
        except Exception as e:
            print(f"Erreur lors de la synchronisation des commandes : {e}")

# Instance du bot
bot = DiscordBot()

### Events ###

@bot.event
async def on_ready():
    """Événement déclenché quand le bot est prêt."""
    print(f'Bot connecté en tant que {bot.user}')

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

# Lancement du bot
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
