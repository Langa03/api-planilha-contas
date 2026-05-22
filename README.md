# API Financeira WhatsApp 🚀

Esta API permite registrar gastos e ganhos em uma planilha do Google Sheets diretamente pelo WhatsApp, utilizando Twilio como ponte.

## 🛠️ Tecnologias
- **Python 3.12**
- **FastAPI** (Backend)
- **Google Sheets API** (Armazenamento)
- **Twilio WhatsApp API** (Interface)

## 📋 Funcionalidades
- **Fluxo Guiado (Chatbot):** O bot conversa com você para garantir que os dados caiam na coluna certa.
- **Mapeamento de Planilha Mensal:** Identifica automaticamente o mês atual e as categorias disponíveis na sua planilha.
- **Soma Inteligente:** Se você já registrou algo em "Gasolina" este mês, o novo valor será somado ao anterior automaticamente.
- **Logging:** Acompanhamento detalhado das transações e erros.

## 💬 Como usar no WhatsApp
1. **Envie o valor:** `50.00` ou `Almoço 35`.
2. **Escolha a Categoria:** O bot enviará uma lista numerada baseada na sua planilha (ex: 1. Gasolina, 2. Moradia...). Digite o número ou o nome.
3. **Escolha o Tipo:** Responda `Gasto` (diminui o total) ou `Ganho` (aumenta o total).
4. **Pronto!** O valor será formatado como `R$ 50,00` e inserido na célula correta da sua planilha mensal.

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure o arquivo `.env`:**
   Crie um arquivo `.env` na raiz com:
   ```env
   SPREADSHEET_ID=seu_id_da_planilha
   GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json
   ```

3. **Adicione as credenciais do Google:**
   Coloque o arquivo `credentials.json` (Service Account) na raiz do projeto.

4. **Inicie o servidor:**
   ```bash
   python src/app.py
   ```

5. **Exponha a API (para teste com Twilio):**
   ```bash
   ngrok http 8000
   ```
   Configure o Webhook no Twilio Sandbox para: `https://<seu-link-ngrok>/whatsapp`.

## 🧪 Testes
Para rodar os testes do parser:
```bash
python tests/test_parser.py
```

## ☁️ Deploy no Render.com
1. Conecte seu GitHub ao Render.
2. Crie um **Web Service**.
3. Configure as **Environment Variables** (`SPREADSHEET_ID`, etc.).
4. Use o **Secret File** para o `credentials.json`.
5. Start Command: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
