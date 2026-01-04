from app.model.ler_csv import ler_csv
from app.controller.cnd_estadual import baixar_cnd


cnpjs, nomes = ler_csv("planilhas/CNPJs.csv")
for cnpj in cnpjs:
    for nome in nomes:
        baixar_cnd(cnpj, f"documentos/CND_Estadual - {cnpj} - {nome}.pdf")