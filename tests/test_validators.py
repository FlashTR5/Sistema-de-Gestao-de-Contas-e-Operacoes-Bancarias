"""
Testes Unitários para o Módulo de Validações (validators.py)
"""
import unittest
import sys
import os

# Adiciona o diretório app ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from validators import (
    validar_busca_id_cpf,
    validar_codigo_agencia,
    validar_cpf,
    validar_cnpj,
    validar_cpf_cnpj,
    validar_email,
    validar_telefone,
    validar_numero_conta,
    validar_numero_cartao,
    formatar_moeda
)

class TestValidators(unittest.TestCase):

    def test_busca_id_cpf_rejeita_letras(self):
        validar = validar_busca_id_cpf
        mensagem = "O campo de busca por ID/CPF aceita exclusivamente dígitos numéricos (0-9). Letras não são permitidas."
        for termo in ("sfasdasdAWS", "4A", "abc"):
            with self.subTest(termo=termo):
                self.assertEqual(validar(termo), (False, mensagem))

    def test_busca_id_cpf_aceita_digitos(self):
        validar = validar_busca_id_cpf
        for termo in ("4", "004", "52998224725", "12345678901234"):
            with self.subTest(termo=termo):
                ok, msg = validar(termo)
                self.assertTrue(ok, msg)

    def test_busca_id_cpf_rejeita_outros_caracteres(self):
        validar = validar_busca_id_cpf
        for termo in ("", " ", "4 5", "4%", "4_", "4-5", "４", "á", "4\n"):
            with self.subTest(termo=termo):
                self.assertFalse(validar(termo)[0])

    def test_codigo_agencia_aceita_um_a_cinco_digitos(self):
        validar = validar_codigo_agencia
        for agencia in ("0", "1", "0042", "12345"):
            with self.subTest(agencia=agencia):
                ok, msg = validar(agencia)
                self.assertTrue(ok, msg)

    def test_codigo_agencia_rejeita_letras(self):
        validar = validar_codigo_agencia
        for agencia in ("abc", "12A", "sfasdasdAWS"):
            with self.subTest(agencia=agencia):
                self.assertFalse(validar(agencia)[0])

    def test_codigo_agencia_rejeita_tamanho_e_caracteres_invalidos(self):
        validar = validar_codigo_agencia
        for agencia in ("", "123456", " ", "1 2", "12-3", "１２", "1\n"):
            with self.subTest(agencia=agencia):
                self.assertFalse(validar(agencia)[0])

    def test_cpf_valido(self):
        # CPFs com dígitos verificadores matematicamente válidos
        ok, msg = validar_cpf("52998224725")
        self.assertTrue(ok, msg)
        
        ok2, msg2 = validar_cpf("004.819.531-67")
        self.assertTrue(ok2, msg2)

    def test_cpf_invalido_digitos_iguais(self):
        # Sequências repetidas devem ser rejeitadas
        ok, msg = validar_cpf("111.111.111-11")
        self.assertFalse(ok)
        self.assertIn("repetidos", msg)

        ok2, msg2 = validar_cpf("00000000000")
        self.assertFalse(ok2)

    def test_cpf_invalido_digito_verificador(self):
        # Dígito final errado
        ok, msg = validar_cpf("52998224729")
        self.assertFalse(ok)
        self.assertIn("verificador", msg)

    def test_cpf_tamanho_invalido(self):
        ok, msg = validar_cpf("12345")
        self.assertFalse(ok)
        self.assertIn("11 dígitos", msg)

    def test_email_valido(self):
        self.assertTrue(validar_email("cliente@banco.com.br")[0])
        self.assertTrue(validar_email("guilherme.barcelos@aluno.ucb.br")[0])
        self.assertTrue(validar_email("user123+tag@empresa.io")[0])

    def test_email_invalido(self):
        self.assertFalse(validar_email("email_sem_arroba.com")[0])
        self.assertFalse(validar_email("@sem_usuario.com")[0])
        self.assertFalse(validar_email("usuario@")[0])
        self.assertFalse(validar_email("")[0])

    def test_telefone_valido(self):
        self.assertTrue(validar_telefone("(61) 98765-4321")[0])
        self.assertTrue(validar_telefone("61987654321")[0])
        self.assertTrue(validar_telefone("(61) 3344-5566")[0])
        self.assertTrue(validar_telefone("")[0])  # Opcional

    def test_telefone_invalido(self):
        self.assertFalse(validar_telefone("12345")[0])
        self.assertFalse(validar_telefone("(05) 98765-4321")[0]) # DDD 05 não existe
        self.assertFalse(validar_telefone("(61) 88765-4321")[0]) # Celular de 11 dígitos sem 9

    def test_numero_conta_valido(self):
        self.assertTrue(validar_numero_conta("10001-X")[0])
        self.assertTrue(validar_numero_conta("10023-0")[0])
        self.assertTrue(validar_numero_conta("10099-x")[0])

    def test_numero_conta_invalido_letras(self):
        # Bloqueia estritamente letras aleatórias (conforme Print 2: aasdad)
        ok, msg = validar_numero_conta("aasdad")
        self.assertFalse(ok)
        self.assertIn("inválido", msg)

        self.assertFalse(validar_numero_conta("123")[0])
        self.assertFalse(validar_numero_conta("abcde-1")[0])
        self.assertFalse(validar_numero_conta("")[0])

    def test_numero_cartao_valido(self):
        self.assertTrue(validar_numero_cartao("4000123456789010")[0])
        self.assertTrue(validar_numero_cartao("5500 1234 5678 9010")[0])

    def test_numero_cartao_invalido(self):
        # Bloqueia letras em números de cartão
        ok, msg = validar_numero_cartao("4000aasdad123")
        self.assertFalse(ok)
        self.assertIn("letras", msg)

        self.assertFalse(validar_numero_cartao("12345")[0])
        self.assertFalse(validar_numero_cartao("")[0])

    def test_formatar_moeda(self):
        self.assertEqual(formatar_moeda(1500.5), "R$ 1.500,50")
        self.assertEqual(formatar_moeda(1000000.0), "R$ 1.000.000,00")

if __name__ == "__main__":
    unittest.main()
