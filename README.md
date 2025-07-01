# 🤖 Bot Discord - Architecture Modulaire

Bot Discord moderne avec architecture Cogs et typage fort. Intégration avec l'API du plugin **Plan** pour Minecraft, système de killfeed en temps réel et synchronisation avec Google Sheets.

## 🏗️ Architecture

```
DiscordTestBot/
├── bot.py                     # Point d'entrée principal
├── api/                       # Clients API externes
│   ├── minecraft_client.py    # Client API Plan
│   └── models.py              # Modèles de données typés
├── cogs/                      # Cogs Discord.py
│   ├── minecraft.py           # Cog pour les commandes Minecraft
│   └── moderation.py          # Cog pour les commandes de modération
├── services/                  # Services
│   ├── killfeed_service.py    # Service de killfeed
│   └── google_sheets_service.py # Service Google Sheets
├── utils/                     # Utilitaires
│   ├── helpers.py             # Fonctions utilitaires
│   └── killfeed_manager.py    # Gestionnaire de killfeed
├── config/                    # Configuration
│   └── settings.py            # Configuration centralisée
└── requirements.txt           # Dépendances
```

## ✨ Fonctionnalités

### 🎮 Commandes Minecraft (MinecraftCog)

#### 📊 Statistiques et Classements

- `/statsminecraftforplayer <nom>` - Statistiques détaillées d'un joueur

  - Kills, morts et ratio K/D
  - Informations de performance

- `/listminecraftplayers` - Liste des joueurs connectés

  - Formatage avec embeds Discord

- `/minecraftranking <type> [limite]` - Classements des joueurs
  - **Types** : `kda` (ratio), `kills`, `deaths`
  - Limite configurable (défaut: 10, max: 25)
  - Emojis pour les 3 premiers (🥇🥈🥉)

#### 🔥 Killfeed en Temps Réel

- `/killfeedstart` - Démarre le monitoring automatique

  - Surveillance via l'API Plan
  - Vérification toutes les 30 secondes

- `/killfeedstop` - Arrête le monitoring
- `/killfeedstatus` - Statut du killfeed

**Fonctionnalités :**

- 🎯 Détection automatique des kills
- 🗡️ Emojis selon l'arme utilisée
- 📏 Affichage de la distance de tir
- ⏰ Horodatage des événements

### 🛡️ Modération (ModerationCog)

- `/warn <utilisateur>` - Avertir (nécessite `kick_members`)
- `/ban <utilisateur> <raison>` - Bannir (nécessite `ban_members`)
- `/unban <user_id>` - Débannir (nécessite `ban_members`)
- `/kick <utilisateur> <raison>` - Expulser (nécessite `kick_members`)

### 🎯 Général

- `/hello` - Salutation
- Messages de bienvenue automatiques
- Commandes préfixées (`!hello`, `!welcome`)

## 🚀 Installation

### Prérequis

- Python 3.8+
- Serveur Discord avec bot configuré
- Serveur Minecraft avec le plugin **Plan**

### Configuration

Créer un fichier `.env` :

```env
DISCORD_TOKEN=votre_token_discord
WELCOME_CHANNEL=id_du_channel_bienvenue
BAN_CHANNEL=id_du_channel_bans
MINECRAFT_KILLFEED_CHANNEL=id_du_channel_killfeed
MINECRAFT_API_URL=http://localhost:8804
```

### Lancement

```bash
git clone <repository-url>
cd DiscordTestBot
pip install -r requirements.txt
python bot.py
```

## ⚙️ Configuration

### API Plan

- **URL** : `http://localhost:8804` (défaut)
- **Timeout** : 30 secondes
- **Plugin requis** : Plan installé sur le serveur Minecraft

### Permissions Discord

- **Modération** : `ban_members`, `kick_members`
- **Killfeed** : `manage_channels`
- **Général** : `send_messages`, `embed_links`

## 📊 Google Sheets Integration

Le bot synchronise automatiquement les données avec Google Sheets pour :

- Le classement des joueurs
- L'historique des kills (killfeed)

### Configuration de Google Sheets

1. **Créer un projet Google Cloud** :

   - Allez sur [Google Cloud Console](https://console.cloud.google.com)
   - Créez un nouveau projet ou sélectionnez un existant
   - Activez l'API Google Sheets pour ce projet

2. **Créer un compte de service** :

   - Dans "APIs & Services" > "Credentials"
   - Cliquez sur "Create Credentials" > "Service Account"
   - Donnez un nom au compte de service
   - Attribuez le rôle "Editor"
   - Créez une clé au format JSON

3. **Configurer les credentials** :

   - Renommez le fichier JSON téléchargé en `google_credentials.json`
   - Placez-le à la racine du projet (même niveau que `bot.py`)

4. **Créer et partager le Google Sheets** :
   - Créez un nouveau Google Sheets nommé exactement "Minecraft_Stats"
   - Partagez-le avec l'email du compte de service (trouvable dans `google_credentials.json`)
   - Donnez les droits d'édition au compte de service

Le fichier Google Sheets contiendra deux onglets :

- **Ranking** : Classement des joueurs (Rang, Joueur, Kills, Morts, K/D Ratio)
- **KillFeed** : Historique des kills (Timestamp, Tueur, Victime, Arme, Distance)

## 🏛️ Bonnes Pratiques

### 📝 Typage Fort

- Utilisation de `dataclasses` pour les modèles
- Annotations de type complètes
- Enums pour les types de classement

### 🔧 Architecture Cogs

- Séparation des responsabilités par Cog
- Gestion du cycle de vie des Cogs
- Injection de dépendances
- Gestionnaires spécialisés (KillFeedManager)

### 🛡️ Gestion d'Erreurs

- Exceptions personnalisées (`APIError`)
- Décorateurs pour la gestion d'erreurs
- Logging centralisé
- Gestionnaires d'erreurs par Cog

### ⚡ Performance

- Sessions HTTP réutilisées
- Réponses différées pour requêtes longues
- Monitoring asynchrone du killfeed

## 📝 Exemples d'Usage

### Classements

```bash
# Affiche le top des joueurs selon différents critères
/minecraftranking kd_ratio 15    # Top 15 par ratio K/D
/minecraftranking kills 10       # Top 10 par kills
/minecraftranking deaths 5       # Top 5 par morts

# Les données sont automatiquement synchronisées avec Google Sheets
# Consultables dans l'onglet "Ranking" du fichier Minecraft_Stats
```

### Killfeed

```bash
# Commande unifiée avec choix d'action
/killfeed start    # Démarre le monitoring
/killfeed stop     # Arrête le monitoring

# Les kills sont automatiquement :
# - Affichés dans le canal configuré
# - Enregistrés dans l'onglet "KillFeed" du Google Sheets
```

### Statistiques

```bash
/statsminecraftforplayer NomDuJoueur  # Stats détaillées d'un joueur
/listminecraftplayers                 # Liste des joueurs en ligne
```

## 🔧 Intégration de Nouvelles Fonctionnalités

### Ajouter un nouveau Cog

```python
# cogs/new_feature.py
from discord.ext import commands

class NewFeatureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def new_command(self, ctx):
        await ctx.send("Nouvelle fonctionnalité!")

async def setup(bot):
    await bot.add_cog(NewFeatureCog(bot))
```

### Charger le nouveau Cog

```python
# bot.py
async def setup_hook(self):
    await self.load_extension("cogs.new_feature")
```

## 🔄 Évolutivité

L'architecture Cogs permet d'ajouter facilement :

- Nouveaux Cogs pour de nouvelles fonctionnalités
- Nouvelles commandes dans les Cogs existants
- Systèmes de base de données
- Intégrations de jeux

## 🔗 Liens Utiles

- [Documentation Discord.py](https://discordpy.readthedocs.io/)
- [Guide des Cogs Discord.py](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html)
- [Plugin Plan](https://github.com/plan-player-analytics/Plan)
- [API Discord](https://discord.com/developers/docs)

## 📄 Licence

Ce projet est sous licence MIT.
