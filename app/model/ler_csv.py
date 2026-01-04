def ler_csv(caminho_arquivo: str) -> list:
    cnpjs = []
    empresas = []
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            cnpj = linha.strip()
            cnpj = linha.split(";")[0].strip()
            cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
            empresa = linha.split(";")[1].strip()
            if empresa:
                empresas.append(empresa)
            if cnpj:
                cnpjs.append(cnpj)
    return cnpjs, empresa