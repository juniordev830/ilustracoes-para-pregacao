'Encontre ilustrações por assunto e veja quando cada uma foi usada pela última vez.'


from unicodedata import combining, normalize


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return value.strip()


def textos(items):
    if not isinstance(items, list):
        raise ValueError("Use uma lista de textos.")
    return [texto(item) for item in items]


def inteiro(value, minimo=0):
    if type(value) is not int or value < minimo:
        raise ValueError(f"Use um número inteiro a partir de {minimo}.")
    return value


def chave(value):
    return "".join(c for c in normalize("NFKD", texto(value).casefold()) if not combining(c))


from datetime import date


def run(data):
    if not isinstance(data, dict):
        raise ValueError("A entrada deve ser um objeto JSON.")
    if not isinstance(data["ilustracoes"], list) or any(not isinstance(item, dict) for item in data["ilustracoes"]):
        raise ValueError("O campo ilustracoes deve ser uma lista de objetos.")
    tema = chave(data["tema"])
    hoje = date.fromisoformat(texto(data["data_sermao"]))
    intervalo = inteiro(data["intervalo_dias"])
    sugeridas, recentes = [], []
    for item in data["ilustracoes"]:
        if tema not in {chave(t) for t in textos(item["temas"])}:
            continue
        uso = item.get("ultimo_uso")
        dia = None if uso is None else date.fromisoformat(texto(uso))
        if dia is not None and dia > hoje:
            raise ValueError("O último uso precisa ser anterior ou igual à data do sermão.")
        resultado = {k: texto(item[k]) for k in ("titulo", "resumo", "origem")}
        resultado["ultimo_uso"] = dia.isoformat() if dia else None
        grupo = sugeridas if dia is None or (hoje - dia).days >= intervalo else recentes
        grupo.append(resultado)
    sugeridas.sort(key=lambda item: (item["ultimo_uso"] or "", item["titulo"]))
    recentes.sort(key=lambda item: (-date.fromisoformat(item["ultimo_uso"]).toordinal(), chave(item["titulo"])))
    return {"sugeridas": sugeridas, "usadas_recentemente": recentes}


import argparse
import sys
from relatorio_csv import escrever_csv
import json
from pathlib import Path


def objeto_sem_campos_repetidos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Campo JSON repetido: {chave!r}.")
        objeto[chave] = valor
    return objeto


def rejeitar_constante_json(constante):
    raise ValueError(f"Constante numérica inválida em JSON: {constante}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="Arquivo JSON com os dados")
    parser.add_argument("--csv", action="store_true", help="Exportar as ilustrações e seu histórico de uso em CSV")
    args = parser.parse_args()

    try:
        with args.entrada.open(encoding="utf-8-sig") as source:
            data = json.load(
                source,
                object_pairs_hook=objeto_sem_campos_repetidos,
                parse_constant=rejeitar_constante_json,
            )
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    if args.csv:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        escrever_csv(result, sys.stdout)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

