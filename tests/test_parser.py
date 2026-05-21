import sys
import os
import unittest

# Adiciona o diretório src ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_message

class TestParser(unittest.TestCase):
    def test_basic_gasto(self):
        result = parse_message("Lanche 25.50")
        self.assertEqual(result["description"], "Lanche")
        self.assertEqual(result["value"], 25.50)
        self.assertEqual(result["type"], "Gasto")

    def test_basic_ganho(self):
        result = parse_message("Ganho Salário 5000")
        self.assertEqual(result["description"], "Salário")
        self.assertEqual(result["value"], 5000.0)
        self.assertEqual(result["type"], "Ganho")

    def test_comma_decimal(self):
        result = parse_message("Mercado 100,50")
        self.assertEqual(result["value"], 100.50)

    def test_explicit_gasto(self):
        result = parse_message("Gasto Aluguel 1200")
        self.assertEqual(result["description"], "Aluguel")
        self.assertEqual(result["value"], 1200.0)
        self.assertEqual(result["type"], "Gasto")

    def test_no_description(self):
        result = parse_message("50")
        self.assertEqual(result["description"], "Sem descrição")
        self.assertEqual(result["value"], 50.0)
        self.assertEqual(result["type"], "Gasto")

    def test_invalid_message(self):
        result = parse_message("mensagem sem numero")
        self.assertIsNone(result)

    def test_mixed_case(self):
        result = parse_message("GaNho Bonus 200")
        self.assertEqual(result["type"], "Ganho")
        self.assertEqual(result["description"], "Bonus")
        self.assertEqual(result["value"], 200.0)

    def test_number_in_description(self):
        # Este é um caso difícil para o parser atual
        result = parse_message("Pizza para 2 pessoas 45.00")
        # O parser atual provavelmente vai falhar ou pegar o '2'
        # Vamos ver o que acontece.
        self.assertEqual(result["value"], 45.00)
        self.assertEqual(result["description"], "Pizza para 2 pessoas")

if __name__ == "__main__":
    unittest.main()
