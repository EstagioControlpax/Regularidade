from app.model.ler_csv import ler_csv
from app.controller.cnd_estadual import baixar_cnd
from app.controller.consultar_cnpj import consultar_cnpjs
import logging
import os

CAMINHO_EMPRESAS = "data/planilhas/CNPJs.csv"

def consultar_cnd_estadual(caminho_csv: str) -> None:
    os.makedirs("logs/cnd_estadual", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/cnd_estadual/execucao.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    empresas = ler_csv(caminho_csv)
    max_tentativas = 5

    for cnpj, empresa in empresas.items():
        tentativa = 0
        while tentativa < max_tentativas:
            try:
                baixar_cnd(cnpj, f"data/documentos/Estadual/CND_Estadual - {cnpj} - {empresa}.pdf")
                break
            except Exception as e:
                tentativa += 1
                if tentativa == max_tentativas:
                    logging.error(f"{empresa} - {cnpj}: {e}")

def consultar_cnd_federal():
    pass

def consultar_cnpj(caminho_csv: str):
    empresas = ler_csv(caminho_csv)

    lista_cnpjs = list(empresas.keys())

    resultados = consultar_cnpjs(lista_cnpjs)

    for resultado in resultados:
        print(resultado)

    
    
if __name__ == "__main__":
    consultar_cnpjs(CAMINHO_EMPRESAS)