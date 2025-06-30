# 🤖 Bot Discord - Architecture Modulaire

Bot Discord moderne avec architecture modulaire et typage fort. Intégration avec l'API du plugin **Plan** pour Minecraft et système de killfeed en temps réel.

## 🏗️ Architecture

```
DiscordTestBot/
├── bot.py                     # Point d'entrée principal
├── api/                       # Clients API externes
│   ├── minecraft_client.py    # Client API Plan
│   └── models.py              # Modèles de données typés
├── commands/                  # Gestionnaires de commandes
│   ├── minecraft_commands.py  # Commandes Minecraft
│   └── moderation_commands.py # Commandes de modération
├── utils/                     # Utilitaires
│   ├── helpers.py             # Fonctions utilitaires
│   └── killfeed_manager.py    # Gestionnaire de killfeed
├── config/                    # Configuration
│   └── settings.py            # Configuration centralisée
└── requirements.txt           # Dépendances
```

## ✨ Fonctionnalités

### 🎮 Commandes Minecraft

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

### 🛡️ Modération

- `/warn <utilisateur>` - Avertir
- `/ban <utilisateur> <raison>` - Bannir (avec permissions)
- `/unban <user_id>` - Débannir (avec permissions)
- `/kick <utilisateur> <raison>` - Expulser

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

## 🏛️ Bonnes Pratiques

### 📝 Typage Fort

- Utilisation de `dataclasses` pour les modèles
- Annotations de type complètes
- Enums pour les types de classement

### 🔧 Architecture Modulaire

- Séparation des responsabilités
- Injection de dépendances
- Gestionnaires spécialisés (KillFeedManager)

### 🛡️ Gestion d'Erreurs

- Exceptions personnalisées (`APIError`)
- Décorateurs pour la gestion d'erreurs
- Logging centralisé

### ⚡ Performance

- Sessions HTTP réutilisées
- Réponses différées pour requêtes longues
- Monitoring asynchrone du killfeed

## 📝 Exemples d'Usage

### Classements

```bash
/minecraftranking kda 15    # Top 15 par ratio K/D
/minecraftranking kills 10  # Top 10 par kills
/minecraftranking deaths 5  # Top 5 par morts
```

### Killfeed

```bash
/killfeedstart   # Démarre le monitoring
/killfeedstop    # Arrête le monitoring
/killfeedstatus  # Vérifie le statut
```

### Statistiques

```bash
/statsminecraftforplayer NomDuJoueur
```

## 🔧 Intégration de Nouvelles Fonctionnalités

### Ajouter une nouvelle API

```python
# api/new_api_client.py
class NewAPIClient:
    async def get_data(self) -> List[DataModel]:
        # Implémentation
        pass

# commands/new_commands.py
class NewCommands:
    def __init__(self, api_client: NewAPIClient):
        self.api_client = api_client
```

### Ajouter une nouvelle commande

```python
@bot.tree.command(name="nouvellecommande", description="Description")
async def nouvelle_commande(interaction: discord.Interaction):
    await bot.new_commands.nouvelle_commande(interaction)
```

## 🔄 Évolutivité

L'architecture permet d'ajouter facilement :

- Nouvelles APIs externes
- Nouvelles commandes
- Systèmes de base de données
- Intégrations de jeux

## 🔗 Liens Utiles

- [Documentation Discord.py](https://discordpy.readthedocs.io/)
- [Plugin Plan](https://github.com/plan-player-analytics/Plan)
- [API Discord](https://discord.com/developers/docs)

## 📄 Licence

Ce projet est sous licence MIT.
