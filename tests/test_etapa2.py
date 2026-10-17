"""Regressões das demonstrações complementares da Etapa 2."""
import ast
from contextlib import nullcontext
import importlib.util
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from auth import hash_senha, verificar_senha


def carregar_script(nome):
    spec = importlib.util.spec_from_file_location(nome, ROOT / 'scripts' / f'{nome}.py')
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def trecho(predicate):
    tree = ast.parse((ROOT / 'app/app.py').read_text())
    node = next(n for n in ast.walk(tree) if predicate(n))
    return compile(ast.Module(body=[node], type_ignores=[]), '<fluxo-streamlit>', 'exec')


class Stop(Exception):
    pass


class TestEtapa2(unittest.TestCase):
    def test_hash_bcrypt_sal_aleatorio_e_autenticacao(self):
        primeiro = hash_senha('MinhaSenha#2026')
        segundo = hash_senha('MinhaSenha#2026')
        self.assertEqual(len(primeiro), 60)
        self.assertTrue(primeiro.startswith('$2b$'))
        self.assertNotEqual(primeiro, segundo)
        self.assertTrue(verificar_senha('MinhaSenha#2026', primeiro))
        self.assertFalse(verificar_senha('SenhaErrada', primeiro))
        self.assertFalse(verificar_senha('MinhaSenha#2026', 'hash-invalido'))

    def test_saldo_insuficiente_interrompe_antes_da_transferencia(self):
        code = trecho(lambda n: isinstance(n, ast.If) and isinstance(n.test, ast.Call)
                      and n.test.args and isinstance(n.test.args[0], ast.Constant)
                      and n.test.args[0].value == 'Executar Transferência com Sucesso')
        mensagens, chamadas = [], []
        def stop():
            raise Stop
        env = {'st': SimpleNamespace(button=lambda *a, **kw: True, stop=stop,
                                     warning=mensagens.append, error=mensagens.append),
               'c_origem': '10001-X', 'c_destino': '10002-X', 'saldo_o': 50.0,
               'valor_transf': 100.0, 'formatar_moeda': lambda v: f'R$ {v:.2f}',
               'render_callout': lambda *a, **kw: mensagens.append(a),
               'executar_transferencia_transacional': lambda *a, **kw: (chamadas.append((a, kw)) or (False, 'executada'))}
        with self.assertRaises(Stop):
            exec(code, env)
        self.assertFalse(chamadas)
        self.assertTrue(any('insuficiente' in str(m).lower() for m in mensagens))

    def test_demonstracao_hash_persiste_e_verifica_no_rerun(self):
        try:
            code = trecho(lambda n: isinstance(n, ast.With) and any(
                isinstance(i.context_expr, ast.Name) and i.context_expr.id == 'tab_hash' for i in n.items))
        except StopIteration:
            self.fail('Aba de demonstração bcrypt ainda não implementada')
        estado, mensagens = {}, []
        def executar(gerar, testar, senha):
            st = SimpleNamespace(
                markdown=lambda *a, **kw: None, caption=lambda *a, **kw: None,
                info=lambda m: mensagens.append(('info', m)),
                error=lambda m: mensagens.append(('error', m)),
                success=lambda m: mensagens.append(('success', m)),
                text_input=lambda label, **kw: 'MinhaSenha#2026' if kw.get('key') == 'bcrypt_senha_plana' else senha,
                button=lambda label, **kw: gerar if label == 'Gerar Hash com Sal (bcrypt)' else testar,
                spinner=lambda *a, **kw: nullcontext(), code=lambda *a, **kw: None,
                session_state=estado)
            exec(code, {'st': st, 'tab_hash': nullcontext(),
                        'hash_senha': hash_senha, 'verificar_senha': verificar_senha})
        executar(True, False, '')
        self.assertEqual(len(estado['bcrypt_hash_demo']), 60)
        executar(False, True, 'MinhaSenha#2026')
        self.assertEqual(mensagens[-1][0], 'success')
        executar(False, True, 'incorreta')
        self.assertEqual(mensagens[-1][0], 'error')

    def test_smoke_reporta_falha_continua_e_retorna_exit_code(self):
        try:
            modulo = carregar_script('smoke_test_etapa2')
        except FileNotFoundError:
            self.fail('Smoke test ainda não implementado')
        executados = []
        def falhar():
            raise RuntimeError('falha controlada')
        def passar():
            executados.append(True)
            return 'ok'
        saida = io.StringIO()
        status = modulo.executar_verificacoes([('Falha', falhar), ('Sucesso', passar)], saida, color=False)
        self.assertEqual(status, 1)
        self.assertEqual(executados, [True])
        self.assertIn('[FAIL]', saida.getvalue())
        self.assertIn('[PASS]', saida.getvalue())
        self.assertNotIn('\x1b', saida.getvalue())
        self.assertEqual(modulo.executar_verificacoes([('Sucesso', passar)], io.StringIO(), color=False), 0)


if __name__ == '__main__':
    unittest.main()
