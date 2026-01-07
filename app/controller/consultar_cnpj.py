import requests
from bs4 import BeautifulSoup
import time
import json


# ============================================================
# Função para consultar inscrição estadual CE
# ============================================================
def consultar_ie(cnpj: str) -> str:
    url = f"https://consultapublica.sefaz.ce.gov.br/sintegra/consultar?tipdocumento=2&numcnpjcgf={cnpj}"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if response.status_code != 200:
            return "Sem Inscrição"
        
        html = response.text.replace("\n", "").replace("\t", "").replace("&nbsp;", "")
        soup = BeautifulSoup(html, "html.parser")
        
        # Procura o <td> com o CNPJ
        td = soup.find("td", string=cnpj)
        if not td:
            return "Sem Inscrição"
        
        tr = td.find_parent("tr")
        tds = tr.find_all("td")
        if len(tds) < 3:
            return "Sem Inscrição"
        
        inscricao = tds[2].get_text(strip=True)
        return inscricao if inscricao else "Sem Inscrição"
    
    except Exception:
        return "Sem Inscrição"


def consultar_cnpjs(lista_cnpjs: list) -> list:
    resultados = []
    for cnpj in lista_cnpjs:
        url = f"https://open.cnpja.com/office/{cnpj}"
        resposta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).text

        if not resposta:
            resultados.append({
                "cnpj": cnpj,
                "erro": "Erro HTTP ao consultar."
            })
            continue

        try:
            data = json.loads(resposta)
        except json.JSONDecodeError:
            resultados.append({
                "cnpj": cnpj,
                "erro": "Resposta JSON inválida."
            })
            continue

        # CNAE principal
        main_activity = data.get("mainActivity", {})
        cnae_principal = main_activity.get("id", "")
        cnae_descricao = main_activity.get("text", "")

        # CNAEs secundários
        sec_activities = data.get("sideActivities", [])
        cnae2 = ";".join([str(a.get("id", "")) for a in sec_activities])
        cnae2desc = ";".join([str(a.get("text", "")) for a in sec_activities])

        # Endereço / situação
        endereco = data.get("address", {})
        municipio = endereco.get("city", "")
        estado = endereco.get("state", "")
        situacao = data.get("status", {}).get("text", "")

        # Registros estaduais
        regs = data.get("registrations", [])
        ie_estados = ";".join([r.get("state", "") for r in regs])
        ie_atividade = ";".join([str(r.get("enabled", "")) for r in regs])
        ie_tipo = ";".join([r.get("type", {}).get("text", "") for r in regs])
        ie_restricao = ";".join([r.get("status", {}).get("text", "") for r in regs])

        # Porte, Simples, Simei
        porte = data.get("company", {}).get("size", {}).get("acronym", "")
        simples = "Sim" if data.get("company", {}).get("simples", {}).get("optant") else "Não"
        simei = "Sim" if data.get("company", {}).get("simei", {}).get("optant") else "Não"

        # Sócios
        membros = data.get("company", {}).get("members", [])
        nomes = ";".join([m.get("person", {}).get("name", "") for m in membros])
        cargos = ";".join([m.get("role", {}).get("text", "") for m in membros])
        idades = ";".join([str(m.get("person", {}).get("age", "")) for m in membros])

        # Inscrição estadual
        inscricao = consultar_ie(cnpj) if estado == "CE" else "Consultar Manualmente"

        # Monta resultado
        resultados.append({
            "cnpj": cnpj,
            "cnae_principal": cnae_principal,
            "cnae2": cnae2,
            "municipio": municipio,
            "estado": estado,
            "situacao": situacao,
            "porte": porte,
            "simples": simples,
            "simei": simei,
            "inscricao": inscricao,
            "nomes": nomes,
            "idades": idades,
            "cargos": cargos,
            "ie_estados": ie_estados,
            "ie_atividade": ie_atividade,
            "ie_tipo": ie_tipo,
            "ie_restricao": ie_restricao
        })

        if lista_cnpjs.index(cnpj) % 5 == 0:
            time.sleep(5)

    return resultados