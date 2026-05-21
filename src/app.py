import sys
import os

# Adiciona o diretório raiz ao path para importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Form, Response
from pydantic import BaseModel
from datetime import datetime
from src.sheets_client import SheetsClient
from src.parser import parse_message
import uvicorn

app = FastAPI(title="API Financeira WhatsApp")
sheets_client = SheetsClient()

class Transaction(BaseModel):
    description: str
    value: float
    type: str  # 'Gasto' ou 'Ganho'

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API Financeira está rodando!"}

@app.post("/webhook")
async def receive_transaction(transaction: Transaction):
    try:
        # Formata os dados para a planilha
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        row = [
            data_atual,
            transaction.description,
            f"{transaction.value:.2f}",
            transaction.type
        ]
        
        # Salva no Google Sheets
        sheets_client.append_row(row)
        
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
    try:
        # Tenta interpretar a mensagem
        parsed_data = parse_message(Body)
        
        if not parsed_data:
            reply = "Desculpe, não entendi. Tente algo como: 'Lanche 25.50' ou 'Ganho Salário 5000'."
        else:
            # Formata os dados para a planilha
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            row = [
                data_atual,
                parsed_data["description"],
                f"{parsed_data['value']:.2f}",
                parsed_data["type"]
            ]
            
            # Salva no Google Sheets
            sheets_client.append_row(row)
            
            reply = f"✅ Registrado: {parsed_data['type']}\n📝 {parsed_data['description']}\n💰 R$ {parsed_data['value']:.2f}"

        # Retorna TwiML (XML) para o Twilio responder ao usuário
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""
        
        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        # Em caso de erro, avisa o usuário
        error_reply = f"❌ Erro ao processar: {str(e)}"
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{error_reply}</Message>
</Response>"""
        return Response(content=twiml_response, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
