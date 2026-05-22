import sys
import os
import logging
import httpx
from fastapi import FastAPI, HTTPException, Request, Response, Query
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

app = FastAPI(title="API Financeira WhatsApp (Meta API)")
sheets_client = SheetsClient()

# Configurações da Meta (Devem ser setadas no Render)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "api_financeira_secret_123")

class Transaction(BaseModel):
    description: str
    value: float
    type: str  # 'Gasto' ou 'Ganho'

# Estados da conversa
AWAITING_VALUE = "AWAITING_VALUE"
AWAITING_CATEGORY = "AWAITING_CATEGORY"
AWAITING_TYPE = "AWAITING_TYPE"

user_states = {}

# Mapeamento de Meses
MONTHS_MAP = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}

async def send_whatsapp_message(to: str, text: str):
    """
    Envia uma mensagem de texto usando a API do WhatsApp Cloud (Meta).
    """
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                logger.error(f"Erro da Meta ({response.status_code}): {response.text}")
            response.raise_for_status()
            logger.info(f"Mensagem enviada para {to}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {to}: {str(e)}")

def get_sheet_layout():
    """
    Lê a planilha para descobrir as categorias e meses.
    """
    try:
        data = sheets_client.get_all_values()
        if not data or len(data) < 3:
            logger.warning("Planilha com poucas linhas ou não acessível.")
            return None, None
        
        headers = [h.strip().upper() for h in data[2]]
        
        if len([h for h in headers if h]) < 2:
            headers = [h.strip().upper() for h in data[1]]

        valid_months = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
                        "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
        
        months = []
        for row in data:
            if row and row[0].strip().upper() in valid_months:
                months.append(row[0].strip().upper())
        
        return headers, months
    except Exception as e:
        logger.error(f"Erro ao ler layout da planilha: {e}")
        return None, None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API Financeira Meta está rodando!"}

@app.get("/whatsapp")
async def verify_webhook(request: Request):
    """
    Endpoint de verificação exigido pela Meta para configurar o Webhook.
    """
    params = request.query_params
    hub_mode = params.get("hub.mode")
    hub_verify_token = params.get("hub.verify_token")
    hub_challenge = params.get("hub.challenge")

    # Força o token que o usuário definiu se o ENV falhar
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "api_contas_123")

    logger.info(f"--- TENTATIVA DE VERIFICAÇÃO ---")
    logger.info(f"Recebido do Facebook: {hub_verify_token}")
    logger.info(f"Esperado pelo Servidor: {expected_token}")

    if hub_mode == "subscribe" and (hub_verify_token == expected_token or hub_verify_token == "api_contas_123"):
        logger.info("VERIFICAÇÃO BATEU! Respondendo ao Facebook...")
        # A resposta DEVE ser apenas o challenge puro (texto simples)
        return Response(content=hub_challenge, media_type="text/plain")
    
    logger.warning("VERIFICAÇÃO FALHOU!")
    return Response(content="Token Incorreto", status_code=403)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Recebe notificações da Meta (WhatsApp Cloud API).
    """
    body = await request.json()
    logger.info(f"Evento recebido da Meta: {body}")

    # Verifica se é uma mensagem válida
    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        message = value.get("messages", [{}])[0]
        
        if not message:
            return {"status": "ignored"}

        from_number = message.get("from")
        message_body = message.get("text", {}).get("body", "").strip()

        if not message_body:
            return {"status": "ignored"}

        # Gerenciamento de Estado
        state_data = user_states.get(from_number, {"state": AWAITING_VALUE})
        reply = ""

        if state_data["state"] == AWAITING_VALUE:
            parsed = parse_message(message_body)
            if not parsed:
                reply = "Olá! Para começar, envie o valor que deseja registrar (ex: 50 ou 150.50)."
            else:
                headers, _ = get_sheet_layout()
                if not headers:
                    reply = "⚠️ Erro ao acessar a planilha. Verifique as permissões."
                else:
                    categories = [h for i, h in enumerate(headers) if h and h not in ["TOTAL", "MESES", "DESPESAS", ""] and i > 0]
                    
                    if not categories:
                        reply = "⚠️ Nenhuma categoria encontrada na Linha 3 da planilha."
                    else:
                        state_data.update({
                            "value": parsed["value"],
                            "description": parsed["description"],
                            "state": AWAITING_CATEGORY,
                            "categories": categories
                        })
                        user_states[from_number] = state_data
                        options = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories)])
                        reply = f"💰 R$ {parsed['value']:.2f} ({parsed['description']})\n\nEscolha a **categoria**:\n\n{options}\n\n(Responda com o número ou nome)"

        elif state_data["state"] == AWAITING_CATEGORY:
            categories = state_data["categories"]
            selected_cat = None
            if message_body.isdigit():
                idx = int(message_body) - 1
                if 0 <= idx < len(categories):
                    selected_cat = categories[idx]
            else:
                for cat in categories:
                    if message_body.upper() in cat:
                        selected_cat = cat
                        break
            
            if not selected_cat:
                reply = "⚠️ Categoria inválida. Escolha uma das opções da lista."
            else:
                state_data.update({"category": selected_cat, "state": AWAITING_TYPE})
                user_states[from_number] = state_data
                reply = f"📁 Selecionado: {selected_cat}.\n\nIsso é um **1. Gasto** ou um **2. Ganho**?"

        elif state_data["state"] == AWAITING_TYPE:
            choice = message_body.lower()
            if "gasto" in choice or "1" == choice:
                final_value = -state_data["value"]
            elif "ganho" in choice or "2" == choice:
                final_value = state_data["value"]
            else:
                await send_whatsapp_message(from_number, "Por favor, responda '1' para Gasto ou '2' para Ganho.")
                return {"status": "ok"}

            headers, months = get_sheet_layout()
            current_month_name = MONTHS_MAP[datetime.now().month]
            
            try:
                row_idx = months.index(current_month_name) + 4 # Offset conforme estrutura (Título + Vazio + Header = 3, data começa na 4)
                col_idx = headers.index(state_data["category"]) + 1
                
                new_total = sheets_client.update_cell_value(row_idx, col_idx, final_value)
                reply = f"✅ Sucesso!\n📅 Mês: {current_month_name}\n📁 Categoria: {state_data['category']}\n💰 Novo Total: R$ {new_total:.2f}"
                user_states[from_number] = {"state": AWAITING_VALUE}
            except Exception as e:
                logger.error(f"Erro ao salvar: {e}")
                reply = f"❌ Erro ao localizar célula: {str(e)}"

        if reply:
            await send_whatsapp_message(from_number, reply)
            
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Erro geral: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
