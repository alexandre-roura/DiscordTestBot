# Discord Bot - TestBot

Un bot Discord simple développé en Python avec des fonctionnalités de modération et d'accueil.

## Fonctionnalités

- **Commandes slash** : Utilise les commandes slash modernes de Discord
- **Modération** : Ban, unban, kick, warn
- **Accueil** : Messages automatiques pour les nouveaux membres
- **Embeds** : Création d'embeds personnalisés

## Installation

1. Clonez ce repository :

```bash
git clone <URL_DU_REPO>
cd TestBot
```

2. Créez un environnement virtuel :

```bash
python -m venv testBotEnv
testBotEnv\Scripts\activate  # Windows
```

3. Installez les dépendances :

```bash
pip install discord.py python-dotenv
```

4. Créez un fichier `.env` avec vos variables d'environnement :

```env
DISCORD_TOKEN=votre_token_discord
WELCOME_CHANNEL=id_du_canal_bienvenue
BAN_CHANNEL=id_du_canal_ban
```

5. Lancez le bot :

```bash
python bot.py
```

## Commandes disponibles

- `/hello` - Salue l'utilisateur
- `/warn <membre>` - Avertit un membre
- `/ban <membre> <raison>` - Bannit un membre
- `/unban <user_id>` - Débannit un utilisateur
- `/kick <membre> <raison>` - Expulse un membre
- `/embed` - Envoie un embed d'exemple

## Configuration

Assurez-vous que votre bot Discord a les permissions nécessaires :

- Gérer les membres
- Envoyer des messages
- Utiliser les commandes slash

## Licence

Ce projet est sous licence MIT.
