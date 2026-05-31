# API Financeira WhatsApp 🚀 (Evolution API Version)

Esta API permite registrar gastos e ganhos em uma planilha do Google Sheets diretamente pelo WhatsApp, utilizando a **Evolution API** (instância Docker própria).

## 📋 Funcionalidades
- **Fluxo Guiado (Chatbot):** O bot conversa com você (Valor -> Categoria -> Tipo) para garantir que os dados caiam na coluna certa.
- **Mapeamento de Planilha Mensal:** Identifica automaticamente o mês atual (Linha) e as categorias disponíveis (Coluna na Linha 3).
- **Soma Inteligente:** Valores registrados na mesma categoria e mês são somados automaticamente.
- **Auto-Hospedado:** Maior controle e flexibilidade usando Evolution API em Docker.

## 💬 Como usar no WhatsApp
1. **Envie o valor:** Ex: `50.00` ou `Gasolina 150`.
2. **Escolha a Categoria:** O bot enviará a lista baseada na sua planilha. Responda com o número ou nome.
3. **Escolha o Tipo:** Responda `1` para Gasto (subtrai) ou `2` para Ganho (soma).
4. **Confirmação:** O bot confirma o novo total daquela categoria no mês.

---

## 🚀 Guia de Instalação e Configuração

### 1. Requisitos Prévios
- Instância da [Evolution API](https://github.com/evolution-foundation/evolution-api) rodando (Docker).
- Planilha Google com meses na Coluna A e categorias na Linha 3.
- Conta no [Render.com](https://render.com/) (ou similar) para hospedar esta API.

### 2. Configuração da Planilha (Google Sheets)
- Crie uma **Service Account** no Google Cloud Console.
- Baixe o arquivo `credentials.json` e coloque-o na raiz do projeto.
- Compartilhe sua planilha com o e-mail da Service Account (permissão de Editor).

### 3. Configuração da Evolution API
- Crie uma instância na sua Evolution API (ex: `claudio_bot`).
- No painel da Evolution, configure o **Webhook**:
    - **URL:** `https://seu-app.onrender.com/whatsapp`
    - **Events:** Selecione `MESSAGES_UPSERT`.
- Pegue a sua **Global API Key** e o **Instance Name**.

### 4. Configuração no Render.com (Variáveis de Ambiente)
Configure as seguintes variáveis em **Environment**:

| Key | Descrição |
| :--- | :--- |
| `SPREADSHEET_ID` | O ID longo da sua planilha Google. |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | `credentials.json` |
| `EVOLUTION_API_URL` | A URL base da sua API (ex: `https://api.meudominio.com`). |
| `EVOLUTION_API_KEY` | Sua Global API Key da Evolution. |
| `EVOLUTION_INSTANCE_NAME` | O nome da instância criada (ex: `claudio_bot`). |

**Secret File:** Adicione um arquivo secreto chamado `credentials.json` com o conteúdo do seu arquivo local.

---

## 🛠️ Comandos Úteis
- **Rodar Localmente:** `python src/app.py`
- **Testar Webhook:** `ngrok http 8000` (Use o link do ngrok na Evolution para testes locais).

## 🛠️ Manutenção e Solução de Problemas

### 1. Criar Nova Instância
Para criar uma nova instância, execute o comando abaixo (substitua o nome da instância conforme necessário):

curl -X POST http://34.24.60.83:8080/instance/create -H "apikey: 4224771A-8F1E-4630-B740-2ED005697F6F" -H "Content-Type: application/json" -d '{"instanceName": "instancia_langa", "integration": "WHATSAPP-BAILEYS", "qrcode": true}'

### 2. Regenerar QR Code (Se falhar)
Caso o QR Code não abra ou expire, force uma nova conexão:

Logout da conexão atual:
curl -H "apikey: 4224771A-8F1E-4630-B740-2ED005697F6F" -X DELETE http://34.24.60.83:8080/instance/logout/instancia_langa

Gerar novo QR Code:
curl -H "apikey: 4224771A-8F1E-4630-B740-2ED005697F6F" http://34.24.60.83:8080/instance/connect/instancia_langa

### 3. Deletar Instância
Para deletar uma instância existente, execute:

curl -X DELETE "http://34.24.60.83:8080/instance/delete/instancia_claudio" -H "apikey: 4224771A-8F1E-4630-B740-2ED005697F6F"

### 3. Gerar QR Code
Após criar a instância, gere o QR Code para conectar o WhatsApp:

curl -H "apikey: 4224771A-8F1E-4630-B740-2ED005697F6F" http://34.24.60.83:8080/instance/connect/instancia_langa

### 4. Visualizar QR Code
1. Copie o conteúdo base64 retornado no comando de conexão.
2. Acesse codebeautify.org/base64-to-image-converter.
3. Cole o código para visualizar a imagem e escanear.

### 5. Resetar Instâncias (Botão de Pânico)
Se encontrar erros persistentes, você pode resetar o volume de instâncias:

docker stop evolution_api
docker volume rm evolution_instances
docker start evolution_api
