import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

class SheetsClient:
    def __init__(self):
        # Define a pasta raiz do projeto (um nível acima de src)
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Carrega o .env explicitamente da raiz
        load_dotenv(os.path.join(self.base_path, '.env'))
        
        self.credentials_filename = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
        self.credentials_path = os.path.join(self.base_path, self.credentials_filename)
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self._authenticate()

    def _authenticate(self):
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
        
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=self.scopes)
        return gspread.authorize(creds)

    def append_row(self, data, sheet_name=None):
        """
        Adiciona uma linha na planilha.
        data: lista de valores (ex: ["2023-10-27", "Almoço", "35.00", "Gasto"])
        sheet_name: nome da aba (opcional)
        """
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        if sheet_name:
            worksheet = spreadsheet.worksheet(sheet_name)
        else:
            worksheet = spreadsheet.get_worksheet(0)
        
        return worksheet.append_row(data)

if __name__ == "__main__":
    # Teste rápido se rodar o arquivo diretamente
    client = SheetsClient()
    print("Autenticação realizada com sucesso!")
