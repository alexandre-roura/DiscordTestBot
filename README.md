# Discord Bot - Architecture Modulaire

Bot Discord moderne avec architecture modulaire, typage fort et bonnes pratiques Python.

## 🏗️ Architecture

```
DiscordTestBot/
├── bot.py                     # Point d'entrée principal
├── api/                       # Clients API externes
│   ├── __init__.py
│   ├── minecraft_client.py    # Client API Minecraft
│   └── models.py              # Modèles de données typés
├── commands/                  # Gestionnaires de commandes
│   ├── __init__.py
│   ├── minecraft_commands.py  # Commandes Minecraft
│   └── moderation_commands.py # Commandes de modération
├── utils/                     # Utilitaires
│   ├── __init__.py
│   └── helpers.py             # Fonctions utilitaires
├── config/                    # Configuration
│   ├── __init__.py
│   └── settings.py            # Configuration centralisée
└── requirements.txt           # Dépendances
```

## ✨ Fonctionnalités

### 🎮 Commandes Minecraft

- `/statsminecraftforplayer` - Affiche les statistiques de combat d'un joueur
  - Kills sur d'autres joueurs
  - Nombre de morts
  - Ratio K/D calculé automatiquement

### 🛡️ Commandes de Modération

- `/warn` - Avertir un utilisateur
- `/ban` - Bannir un utilisateur (avec permissions)
- `/unban` - Débannir un utilisateur (avec permissions)
- `/kick` - Expulser un utilisateur

### 🎯 Commandes Générales

- `/hello` - Salutation
- `/embed` - Envoie un embed de test

## 🚀 Installation

1. **Cloner le projet**

```bash
git clone <repository-url>
cd DiscordTestBot
```

2. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

3. **Configuration**
   Créer un fichier `.env` :

```env
DISCORD_TOKEN=votre_token_discord
WELCOME_CHANNEL=id_du_channel_bienvenue
BAN_CHANNEL=id_du_channel_bans
```

4. **Lancer le bot**

```bash
python bot.py
```

## 🏛️ Bonnes Pratiques Implémentées

### 📝 Typage Fort

- Utilisation de `dataclasses` pour les modèles de données
- Annotations de type complètes
- Validation des types à la compilation

### 🔧 Architecture Modulaire

- **Séparation des responsabilités** : API, commandes, configuration séparées
- **Injection de dépendances** : Clients injectés dans les commandes
- **Classes spécialisées** : Chaque module a sa responsabilité

### 🛡️ Gestion d'Erreurs

- Exceptions personnalisées (`APIError`)
- Décorateurs pour la gestion d'erreurs (`@handle_api_errors`)
- Logging centralisé avec rotation de fichiers

### ⚡ Performance

- Sessions HTTP réutilisées avec contexte managers
- Réponses différées pour les requêtes longues
- Gestion asynchrone optimisée

### 🔒 Sécurité

- Configuration via variables d'environnement
- Validation des permissions Discord
- Gestion sécurisée des IDs utilisateur

## 🧪 Tests

Le code est structuré pour faciliter les tests unitaires :

- Classes avec injection de dépendances
- Méthodes statiques pour les commandes
- Séparation claire entre logique métier et interface

## 📊 Logging

Le système de logging est configuré pour :

- Afficher les logs dans la console
- Sauvegarder dans `bot.log`
- Différents niveaux de log (INFO, ERROR, DEBUG)

## 🔄 Évolutivité

L'architecture permet d'ajouter facilement :

- Nouvelles APIs externes
- Nouvelles commandes
- Nouvelles fonctionnalités de modération
- Systèmes de base de données

## 📝 Exemples d'Usage

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

## 🤝 Contribution

1. Respecter l'architecture modulaire
2. Ajouter le typage pour toutes les fonctions
3. Documenter les nouvelles fonctionnalités
4. Tester les modifications

## 📄 Licence

Ce projet est sous licence MIT.
