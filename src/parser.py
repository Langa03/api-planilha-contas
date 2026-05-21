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

    # Tenta encontrar todos os números na mensagem
    # Regex para encontrar números (inteiros ou decimais com ponto ou vírgula)
    matches = list(re.finditer(r"(\d+([.,]\d+)?)", text))
    
    if not matches:
        return None
    
    # Assume que o último número encontrado é o valor da transação
    last_match = matches[-1]
    value_str = last_match.group(1).replace(",", ".")
    value = float(value_str)
    
    # A descrição é o texto original removendo o valor encontrado
    # Mas apenas a ocorrência específica do valor (o último match)
    start, end = last_match.span()
    description = (text[:start] + text[end:]).strip()
    
    # Remove espaços duplos que podem ter surgido
    description = re.sub(r'\s+', ' ', description)
    
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
