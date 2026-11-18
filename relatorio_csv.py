import csv


def celula(valor):
    """Mantém texto com aparência de fórmula como texto em planilhas."""
    if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + valor
    return valor


def linhas(relatorio):
    for situacao in ("sugeridas", "usadas_recentemente"):
        for item in relatorio[situacao]:
            yield situacao, item["titulo"], item["resumo"], item["origem"], item["ultimo_uso"]


def escrever_csv(relatorio, destino):
    escritor = csv.writer(destino, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\n")
    escritor.writerow(('situacao', 'titulo', 'resumo', 'origem', 'ultimo_uso'))
    for linha in linhas(relatorio):
        escritor.writerow([celula(valor) for valor in linha])
