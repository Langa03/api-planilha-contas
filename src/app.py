import sys
import os
import logging
from fastapi import FastAPI, HTTPException, Form, Response
from pydantic import BaseModel
from datetime import datetime
from src.sheets_client import SheetsClient
from src.parser import parse_message
import uvicorn

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Adiciona o diretório raiz ao path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI(title="API Financeira WhatsApp")
sheets_client = SheetsClient()

class Transaction(BaseModel):
    description: str
    value: float
    type: str  # 'Gasto' ou 'Ganho'

def record_transaction(description: str, value: float, trans_type: str):
    """
    Helper para formatar e salvar a transação no Google Sheets.
    """
    try:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        row = [
            data_atual,
            description,
            f"{value:.2f}",
            trans_type
        ]
        
        logger.info(f"Registrando transação: {row}")
        sheets_client.append_row(row)
        return row
    except Exception as e:
        logger.error(f"Erro ao salvar no Sheets: {str(e)}")
        raise e

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API Financeira está rodando!"}

@app.post("/webhook")
async def receive_transaction(transaction: Transaction):
    try:
        row = record_transaction(
            transaction.description,
            transaction.value,
            transaction.type
        )
        
        return {
            "status": "success",
            "message": "Transação registrada com sucesso!",
            "data": row
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar transação: {str(e)}")

# Estados da conversa
AWAITING_VALUE = "AWAITING_VALUE"
AWAITING_CATEGORY = "AWAITING_CATEGORY"
AWAITING_TYPE = "AWAITING_TYPE"

user_states = {}

# Mapeamento de Meses (para encontrar a linha na planilha)
MONTHS_MAP = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}

def get_sheet_layout():
    """
    Lê a planilha para descobrir as categorias e meses.
    """
    try:
        data = sheets_client.get_all_values()
        if not data:
            return None, None
        
        headers = [h.strip().upper() for h in data[0]] # Linha 1: Categorias
        months = [row[0].strip().upper() for row in data[1:] if row] # Coluna A: Meses
        
        return headers, months
    except Exception as e:
        logger.error(f"Erro ao ler layout da planilha: {e}")
        return None, None

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Recebe mensagens do Twilio WhatsApp Sandbox e gerencia o fluxo da conversa.
    """
    logger.info(f"Mensagem recebida de {From}: {Body}")
    state_data = user_states.get(From, {"state": AWAITING_VALUE})
    
    try:
        if state_data["state"] == AWAITING_VALUE:
            # Tenta extrair o valor da mensagem
            parsed = parse_message(Body)
            if not parsed:
                reply = "Olá! Para começar, envie o valor que deseja registrar (ex: 50 ou 150.50)."
            else:
                headers, _ = get_sheet_layout()
                if not headers:
                    raise Exception("Não foi possível carregar as categorias da planilha.")
                
                # Categorias válidas (excluindo a primeira coluna de meses e a última de Total)
                # Na imagem: MORADIA está na coluna B (index 1)
                categories = [h for h in headers if h and h != "TOTAL" and h != "MESES" and headers.index(h) > 0]
                
                state_data["value"] = parsed["value"]
                state_data["description"] = parsed["description"]
                state_data["state"] = AWAITING_CATEGORY
                state_data["categories"] = categories
                user_states[From] = state_data
                
                options = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories)])
                reply = f"Recebi R$ {parsed['value']:.2f} ({parsed['description']}).\nQual a **categoria**?\n\n{options}\n\n(Digite o número ou o nome)"

        elif state_data["state"] == AWAITING_CATEGORY:
            categories = state_data["categories"]
            selected_cat = None
            
            # Tenta encontrar por número ou nome
            if Body.isdigit():
                idx = int(Body) - 1
                if 0 <= idx < len(categories):
                    selected_cat = categories[idx]
            else:
                # Busca aproximada por nome
                search_term = Body.strip().upper()
                for cat in categories:
                    if search_term in cat:
                        selected_cat = cat
                        break
            
            if not selected_cat:
                reply = "Categoria inválida. Por favor, escolha uma das opções da lista."
            else:
                state_data["category"] = selected_cat
                state_data["state"] = AWAITING_TYPE
                user_states[From] = state_data
                reply = f"Selecionado: {selected_cat}.\nIsso é um **Gasto** ou um **Ganho**?"

        elif state_data["state"] == AWAITING_TYPE:
            choice = Body.strip().lower()
            if "gasto" in choice or "1" in choice:
                trans_type = "Gasto"
                final_value = -state_data["value"]
            elif "ganho" in choice or "2" in choice:
                trans_type = "Ganho"
                final_value = state_data["value"]
            else:
                return Response(content=format_twiml("Por favor, responda 'Gasto' ou 'Ganho'."), media_type="application/xml")

            # Finaliza o registro
            headers, months = get_sheet_layout()
            
            # Encontra a linha (Mês atual)
            current_month_name = MONTHS_MAP[datetime.now().month]
            try:
                row_idx = months.index(current_month_name) + 2 # +1 do header, +1 pois 1-indexed
                col_idx = headers.index(state_data["category"]) + 1 # 1-indexed
                
                logger.info(f"Atualizando célula: Mês {current_month_name} (Row {row_idx}), Cat {state_data['category']} (Col {col_idx})")
                new_total = sheets_client.update_cell_value(row_idx, col_idx, final_value)
                
                reply = f"✅ Sucesso!\n📅 Mês: {current_month_name}\n📁 Categoria: {state_data['category']}\n💰 Novo Total: R$ {new_total:.2f}"
                # Limpa o estado
                user_states[From] = {"state": AWAITING_VALUE}
            except Exception as e:
                logger.error(f"Erro ao encontrar célula: {e}")
                reply = f"❌ Erro ao localizar célula na planilha: {str(e)}"

        return Response(content=format_twiml(reply), media_type="application/xml")

    except Exception as e:
        logger.error(f"Erro no processamento do WhatsApp: {str(e)}")
        return Response(content=format_twiml(f"❌ Erro: {str(e)}"), media_type="application/xml")

def format_twiml(message: str):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
