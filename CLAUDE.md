```markdown
# Projeto: Registro de Gastos e Ganhos via WhatsApp no Google Sheets

Este projeto visa criar uma API que permite registrar gastos e ganhos em uma planilha do Google Sheets enviando mensagens via WhatsApp.

## Visão Geral da Arquitetura:

1.  **Integração WhatsApp:** Receber mensagens do WhatsApp (via Twilio ou WhatsApp Business API).
2.  **API Backend:** Uma aplicação Python que receberá as mensagens do WhatsApp e se comunicará com o Google Sheets.
3.  **Integração Google Sheets:** Usar a API do Google Sheets para autenticar e manipular os dados na planilha.
4.  **Processamento de Mensagens:** A API interpretará o texto do WhatsApp e formatará para a planilha.

## Plano de Ação:

### Fase 1: Configuração e Escrita no Google Sheets

1.  **Configurar Google Cloud Project para Google Sheets API:**
    *   Criar um projeto no Google Cloud Platform.
    *   Habilitar a Google Sheets API.
    *   Criar credenciais de conta de serviço e baixar o arquivo JSON.

2.  **Autenticação Google Sheets API (Python):**
    *   Instalar a biblioteca `gspread` e `oauth2client`.
    *   Escrever um script Python para autenticar na Google Sheets API usando as credenciais da conta de serviço.

3.  **Escrever dados em uma planilha de exemplo (Python):**
    *   Escrever um script Python para abrir uma planilha do Google Sheets específica.
    *   Adicionar uma nova linha com dados de exemplo (ex: data, descrição, valor, tipo).

### Fase 2: Desenvolvimento da API Backend

4.  **Criar interface básica para receber dados (Python Flask/FastAPI):**
    *   Configurar um ambiente virtual Python.
    *   Instalar Flask ou FastAPI.
    *   Criar uma API simples com um endpoint HTTP para receber dados.

5.  **Integrar API com Google Sheets:**
    *   Chamar o script de escrita no Google Sheets a partir do endpoint da API.

### Fase 3: Integração com WhatsApp e Processamento de Mensagens

6.  **Configurar integração com WhatsApp:**
    *   Pesquisar e escolher um provedor de integração WhatsApp (ex: Twilio, WhatsApp Business API).
    *   Configurar o webhook para direcionar as mensagens recebidas para a nossa API.

7.  **Processar mensagens do WhatsApp:**
    *   Implementar a lógica na API para interpretar o texto das mensagens do WhatsApp.
    *   Extrair informações como tipo (gasto/ganho), valor e descrição.
    *   Validar os dados e formatá-los para serem inseridos na planilha.

```