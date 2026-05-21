import re

def parse_message(text: str):
    """
    Interpreta o texto da mensagem do WhatsApp.
    Exemplos:
    - "Lanche 25.50" -> Gasto, Lanche, 25.50
    - "Ganho Venda 100" -> Ganho, Venda, 100.00
    - "Gasto Aluguel 1200" -> Gasto, Aluguel, 1200.00
    """
    text = text.strip()
    
    # Padroniza para minúsculas para facilitar a busca
    text_lower = text.lower()
    
    transaction_type = "Gasto"
    if text_lower.startswith("ganho"):
        transaction_type = "Ganho"
        text = text[5:].strip()
    elif text_lower.startswith("gasto"):
        transaction_type = "Gasto"
        text = text[5:].strip()

    # Tenta encontrar o valor (número) no final ou no meio
    # Regex para encontrar números (inteiros ou decimais com ponto ou vírgula)
    match = re.search(r"(\d+([.,]\d+)?)", text)
    
    if not match:
        return None
    
    value_str = match.group(1).replace(",", ".")
    value = float(value_str)
    
    # A descrição é o que sobra tirando o valor
    description = text.replace(match.group(1), "").strip()
    
    # Se a descrição ficar vazia, tenta pegar do início
    if not description:
        description = "Sem descrição"
        
    return {
        "description": description,
        "value": value,
        "type": transaction_type
    }

if __name__ == "__main__":
    # Testes simples
    print(parse_message("Lanche 25,50"))
    print(parse_message("Ganho Venda 100"))
    print(parse_message("Gasto Aluguel 1200"))
    print(parse_message("Padaria 5"))
