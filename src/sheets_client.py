import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

class SheetsClient:
    def __init__(self, spreadsheet_id=None, credentials_path=None):
        # Define a pasta raiz do projeto (um nível acima de src)
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Carrega o .env explicitamente da raiz
        load_dotenv(os.path.join(self.base_path, '.env'))
        
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")
        if not self.spreadsheet_id:
            raise ValueError("SPREADSHEET_ID não definido no ambiente ou no construtor.")

        self.credentials_filename = credentials_path or os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
        
        # Se for um caminho relativo, resolve a partir da base_path
        if not os.path.isabs(self.credentials_filename):
            self.credentials_path = os.path.join(self.base_path, self.credentials_filename)
        else:
            self.credentials_path = self.credentials_filename

        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.client = self._authenticate()

    def _authenticate(self):
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Arquivo de credenciais não encontrado em: {self.credentials_path}. "
                "Verifique se o arquivo existe ou se a variável GOOGLE_SHEETS_CREDENTIALS_PATH está correta."
            )
        
        try:
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=self.scopes)
            return gspread.authorize(creds)
        except Exception as e:
            raise RuntimeError(f"Falha na autenticação com o Google Sheets: {str(e)}")

    def get_all_values(self, sheet_name=None):
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.get_worksheet(0)
        return worksheet.get_all_values()

    def update_cell_value(self, row, col, value, sheet_name=None):
        """
        Adiciona o valor ao conteúdo atual da célula.
        """
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.get_worksheet(0)
        
        current_val_str = worksheet.cell(row, col).value
        
        # Tenta converter o valor atual para float (removendo R$, etc)
        current_val = 0.0
        if current_val_str:
            try:
                # Remove R$, espaços e troca vírgula por ponto
                clean_val = current_val_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
                current_val = float(clean_val)
            except ValueError:
                current_val = 0.0
        
        new_total = current_val + value
        
        # Formata de volta para o padrão da planilha (R$ XX,XX)
        formatted_val = f"R${new_total:.2f}".replace(".", ",")
        worksheet.update_cell(row, col, formatted_val)
        return new_total

if __name__ == "__main__":
    # Teste rápido se rodar o arquivo diretamente
    client = SheetsClient()
    print("Autenticação realizada com sucesso!")
