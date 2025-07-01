# services/google_sheets_service.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Tuple

# Définir la portée des permissions
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
CREDS_FILE = "google_credentials.json"
SHEET_NAME = "Minecraft_Stats" # Le nom de votre fichier Google Sheets

class GoogleSheetsService:
    """Service pour interagir avec Google Sheets."""

    def __init__(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
            self.client = gspread.authorize(creds)
            print("Autorisation gspread réussie.")
            
            self.sheet = self.client.open(SHEET_NAME)
            print("Connexion à Google Sheets réussie.")
        except FileNotFoundError as e:
            self.client = None
            self.sheet = None
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Erreur: Le fichier Google Sheets '{SHEET_NAME}' n'a pas été trouvé. Assurez-vous qu'il existe et qu'il est partagé avec {creds.service_account_email}")
            self.client = None
            self.sheet = None
        except Exception as e:
            print(f"Erreur de connexion à Google Sheets: {type(e).__name__} - {str(e)}")
            self.client = None
            self.sheet = None

    def _get_worksheet(self, worksheet_name: str):
        """Récupère ou crée une feuille de calcul (onglet)."""
        if not self.sheet:
            return None
        try:
            return self.sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            return self.sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

    def update_ranking(self, ranking_data: List[Tuple[str, int, int, float]]):
        """Met à jour la feuille de classement avec de nouvelles données."""
        if not self.sheet:
            print("Google Sheets non connecté.")
            return
        print("Mise à jour du classement dans Google Sheets...")
        worksheet = self._get_worksheet("Ranking")
        if not worksheet:
            print("Feuille de classement non trouvée.")
            return
        print("Feuille de classement trouvée.")

        worksheet.clear()
        header = ["Rang", "Joueur", "Kills", "Morts", "K/D Ratio"]
        rows_to_insert = [header]

        for i, (name, kills, deaths, kd_ratio) in enumerate(ranking_data, 1):
            kd_text = "∞" if kd_ratio == float('inf') else f"{kd_ratio:.2f}"
            rows_to_insert.append([i, name, kills, deaths, kd_text])
        
        worksheet.append_rows(rows_to_insert, value_input_option='USER_ENTERED')
        print("Feuille de classement mise à jour.")

    def log_kill(self, kill_event):
        """Ajoute une ligne pour un nouvel événement de kill."""
        if not self.sheet:
            return

        worksheet = self._get_worksheet("KillFeed")
        if not worksheet:
            return

        # Si la feuille est vide, ajouter un en-tête
        if worksheet.row_count == 1 and worksheet.acell('A1').value is None:
             header = ["Timestamp", "Tueur", "Victime", "Arme", "Distance"]
             worksheet.append_row(header, value_input_option='USER_ENTERED')

        row = [
            kill_event.timestamp,
            kill_event.killer,
            kill_event.victim,
            kill_event.weapon,
            f"{kill_event.distance:.2f}m"
        ]
        worksheet.append_row(row, value_input_option='USER_ENTERED')
        print(f"Kill de {kill_event.killer} sur {kill_event.victim} enregistré.")