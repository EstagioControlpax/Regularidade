def ler_csv(caminho_arquivo: str) -> dict:
    empresas = {}
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split(";")
            if len(partes) < 2:
                continue
            cnpj = partes[0].strip().replace(".", "").replace("/", "").replace("-", "")
            empresa = partes[1].strip()
            empresas[cnpj] = empresa
    return empresas