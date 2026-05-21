import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sheets_client import SheetsClient

def run_test():
    try:
        print("Iniciando teste de conexão com Google Sheets...")
        client = SheetsClient()
        
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        row = [data_atual, "Teste de Conexão", "0.00", "Teste"]
        
        print(f"Tentando adicionar linha: {row}")
        client.append_row(row)
        
        print("Sucesso! A linha foi adicionada à planilha.")
        
    except Exception:
        import traceback
        print("Erro durante o teste:")
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
