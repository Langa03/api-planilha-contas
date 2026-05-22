# API Financeira WhatsApp 🚀 (Meta API Version)

Esta API permite registrar gastos e ganhos em uma planilha do Google Sheets diretamente pelo WhatsApp, utilizando a **API Oficial da Meta (WhatsApp Cloud API)** para garantir um serviço gratuito e estável.

## 📋 Funcionalidades
- **Fluxo Guiado (Chatbot):** O bot conversa com você (Valor -> Categoria -> Tipo) para garantir que os dados caiam na coluna certa.
- **Mapeamento de Planilha Mensal:** Identifica automaticamente o mês atual (Linha) e as categorias disponíveis (Coluna na Linha 3).
- **Soma Inteligente:** Valores registrados na mesma categoria e mês são somados automaticamente.
- **Custo Zero:** Utiliza o plano gratuito do Render e as primeiras 1.000 mensagens mensais gratuitas da Meta.

## 💬 Como usar no WhatsApp
1. **Envie o valor:** Ex: `50.00` ou `Gasolina 150`.
2. **Escolha a Categoria:** O bot enviará a lista baseada na sua planilha. Responda com o número ou nome.
3. **Escolha o Tipo:** Responda `1` para Gasto (subtrai) ou `2` para Ganho (soma).
4. **Confirmação:** O bot confirma o novo total daquela categoria no mês.

---

## 🚀 Guia de Instalação e Configuração

### 1. Requisitos Prévios
- Conta no [Meta for Developers](https://developers.facebook.com/).
- Planilha Google com meses na Coluna A e categorias na Linha 3.
- Conta no [Render.com](https://render.com/).

### 2. Configuração da Planilha (Google Sheets)
- Crie uma **Service Account** no Google Cloud Console.
- Baixe o arquivo `credentials.json` e coloque-o na raiz do projeto.
- Compartilhe sua planilha com o e-mail da Service Account (permissão de Editor).

### 3. Configuração da API da Meta
- Crie um App do tipo **Business**.
- Configure o WhatsApp e pegue o `Phone Number ID` e o `Temporary Access Token`.
- No menu **Configuration**, defina o Webhook:
    - **Callback URL:** `https://seu-app.onrender.com/whatsapp`
    - **Verify Token:** (O que você definiu no Render, ex: `api_contas_123`)
- Em **Manage Webhook Fields**, assine o campo `messages`.

### 4. Configuração no Render.com
Crie um **Web Service** conectado ao seu GitHub e configure as seguintes variáveis em **Environment**:

| Key | Descrição |
| :--- | :--- |
| `SPREADSHEET_ID` | O ID longo da sua planilha Google. |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | `credentials.json` |
| `WHATSAPP_PHONE_NUMBER_ID` | O ID do número que você pegou na Meta. |
| `WHATSAPP_VERIFY_TOKEN` | A senha de verificação (ex: `api_contas_123`). |
| `WHATSAPP_ACCESS_TOKEN` | O Token de acesso (temporário ou permanente) da Meta. |

**Secret File:** Adicione um arquivo secreto chamado `credentials.json` com o conteúdo do seu arquivo local.

---

## 🛠️ Comandos Úteis
- **Rodar Localmente:** `python src/app.py`
- **Testar Webhook:** `ngrok http 8000` (Use o link do ngrok na Meta para testes rápidos).
- **Testes de Lógica:** `python tests/test_parser.py`
