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

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Recebe mensagens do Twilio WhatsApp Sandbox.
    """
    logger.info(f"Mensagem recebida de {From}: {Body}")
    try:
        # Tenta interpretar a mensagem
        parsed_data = parse_message(Body)
        
        if not parsed_data:
            reply = "Desculpe, não entendi. Tente algo como: 'Lanche 25.50' ou 'Ganho Salário 5000'."
            logger.warning(f"Não foi possível interpretar a mensagem: {Body}")
        else:
            # Registra a transação
            record_transaction(
                parsed_data["description"],
                parsed_data["value"],
                parsed_data["type"]
            )
            
            reply = f"✅ Registrado: {parsed_data['type']}\n📝 {parsed_data['description']}\n💰 R$ {parsed_data['value']:.2f}"

        # Retorna TwiML (XML) para o Twilio responder ao usuário
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""
        
        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        # Em caso de erro, avisa o usuário
        logger.error(f"Erro no processamento do WhatsApp: {str(e)}")
        error_reply = f"❌ Erro ao processar: {str(e)}"
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{error_reply}</Message>
</Response>"""
        return Response(content=twiml_response, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
