import csv
import os
from datetime import datetime
from config import CSV_PATH

HEADER = [
    "",  # coluna vazia (A)
    "DATA",
    "ESPORTE",
    "TIPSTER",
    "PARTIDA",
    "TIP",
    "BOOKIE",
    "VALOR",
    "ODD",
    "RESULTADO",
    "LUCRO/PERDA"
]

def salvar_csv(dados):
    file_exists = os.path.isfile(CSV_PATH)

    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # escreve header só na primeira vez
        if not file_exists:
            writer.writerow(HEADER)

        linha = [
            "",  # coluna vazia
            datetime.now().strftime("%d/%m/%Y"),
            dados.get("esporte", ""),
            dados.get("tipster", ""),
            dados.get("partida", ""),
            dados.get("tip", ""),
            dados.get("casa", ""),
            dados.get("valor", ""),
            dados.get("odd", ""),
            dados.get("resultado", "PENDENTE"),
            ""   # lucro/perda vazio
        ]

        writer.writerow(linha)