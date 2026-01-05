from app.model.ler_csv import ler_csv
from app.controller.cnd_estadual import baixar_cnd
import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/execucao.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

empresas = ler_csv("data/planilhas/CNPJs.csv")
max_tentativas = 5

for cnpj, empresa in empresas.items():
    tentativa = 0
    while tentativa < max_tentativas:
        try:
            baixar_cnd(cnpj, f"data/documentos/Estadual/CND_Estadual - {cnpj} - {empresa}.pdf")
            logging.info(f"CND baixada com sucesso: {cnpj} - {empresa}")
            break
        except Exception as e:
            tentativa += 1
            logging.error(f"Tentativa {tentativa}/{max_tentativas} - Erro ao baixar CND para {cnpj} ({empresa}): {e}")

logging.info("Processo concluído.")
