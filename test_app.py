from tempfile import TemporaryDirectory
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from app import run

ROOT = Path(__file__).resolve().parent


class ProjetoTest(unittest.TestCase):
    def test_exemplo_documentado(self):
        data = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        result = run(data)
        self.assertEqual(result['sugeridas'], [{'titulo': 'Mutirão da comunidade', 'resumo': 'Divisão de tarefas em um mutirão fictício.', 'origem': 'Ilustração original fictícia.', 'ultimo_uso': None}])

    def test_usos_recentes_aparecem_do_mais_novo_ao_mais_antigo(self):
        comum = {"temas": ["fé"], "resumo": "Resumo", "origem": "Arquivo local"}
        result = run({
            "tema": "fé", "data_sermao": "2026-11-15", "intervalo_dias": 10,
            "ilustracoes": [
                dict(comum, titulo="Primeiro uso", ultimo_uso="2026-11-08"),
                dict(comum, titulo="Zebra", ultimo_uso="2026-11-14"),
                dict(comum, titulo="Água", ultimo_uso="2026-11-14"),
            ],
        })
        self.assertEqual([item["titulo"] for item in result["usadas_recentemente"]],
                         ["Água", "Zebra", "Primeiro uso"])

    def test_cli_com_exemplo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), str(ROOT / "exemplo.json")],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(json.loads(result.stdout)['sugeridas'], [{'titulo': 'Mutirão da comunidade', 'resumo': 'Divisão de tarefas em um mutirão fictício.', 'origem': 'Ilustração original fictícia.', 'ultimo_uso': None}])

    def test_rejeita_dados_incompletos(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            run({})

    def test_cli_aceita_json_com_bom(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "exemplo-bom.json"
            arquivo.write_text(exemplo, encoding="utf-8-sig")
            result = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(arquivo)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
        self.assertEqual(json.loads(result.stdout), run(json.loads(exemplo)))

    def test_cli_rejeita_chave_json_repetida(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8").lstrip()
        chave = next(iter(json.loads(exemplo)))
        conteudo = "{" + json.dumps(chave) + ": null," + exemplo[1:]
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "exemplo-repetido.json"
            arquivo.write_text(conteudo, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(arquivo)],
                capture_output=True, text=True, encoding="utf-8",
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("Campo JSON repetido", result.stderr)


class JsonEstritoCliTest(unittest.TestCase):
    def test_cli_rejeita_constantes_numericas_nao_padronizadas(self):
        exemplo = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        with TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "entrada.json"
            for constante in ("NaN", "Infinity", "-Infinity"):
                with self.subTest(constante=constante):
                    exemplo["metadados"] = {"observacao": "CONSTANTE_TESTE"}
                    entrada.write_text(
                        json.dumps(exemplo).replace('"CONSTANTE_TESTE"', constante),
                        encoding="utf-8",
                    )
                    resultado = subprocess.run(
                        [sys.executable, str(ROOT / "app.py"), str(entrada)],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(resultado.returncode, 2)
                    self.assertIn(constante, resultado.stderr)
                    self.assertEqual(resultado.stdout, "")
