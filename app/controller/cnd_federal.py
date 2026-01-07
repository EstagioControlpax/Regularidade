from playwright.sync_api import sync_playwright
import os
import time

URL = "https://servicos.receitafederal.gov.br/servico/certidoes/#/home/cnpj"

<<<<<<< HEAD
def baixar_cnd_federal(cnpj: str, pasta_saida: str):
    os.makedirs(pasta_saida, exist_ok=True)
=======
def baixar_cnd_federal(cnpj: str, caminho_saida: str) -> None:
    os.makedirs(caminho_final, exist_ok=True)
>>>>>>> 1b33b999859da64f11c94b8675f188e9a38373e0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=80
        )

        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

<<<<<<< HEAD
        page.goto(URL, wait_until="domcontentloaded")

        campo = page.locator('input[placeholder="Digite o CNPJ"]')

        campo.wait_for(state="visible", timeout=30000)
        campo.wait_for(state="editable", timeout=30000)

        campo.click()
        campo.fill("")
        campo.type(cnpj, delay=120)

        time.sleep(1)
=======
        page.goto(URL, wait_until="networkidle")

        campo = page.locator('input[placeholder="Digite o CNPJ"]')
        campo.wait_for(state="visible", timeout=30000)
        campo.wait_for(state="editable", timeout=30000)

        page.evaluate("""
        (el, value) => {
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """, campo, cnpj)
>>>>>>> 1b33b999859da64f11c94b8675f188e9a38373e0

        with page.expect_response(lambda r: "certidao" in r.url.lower()):
            page.click('button:has-text("Consultar")')

        botao_pdf = page.locator('button:has-text("Gerar PDF")')
        botao_pdf.wait_for(state="visible", timeout=60000)

        with page.expect_download() as download_info:
            botao_pdf.click()

        download = download_info.value

        nome_arquivo = f"CND_FEDERAL_{cnpj}.pdf"
<<<<<<< HEAD
        caminho_final = os.path.join(pasta_saida, nome_arquivo)
=======
        caminho_final = os.path.join(caminho_saida, nome_arquivo)
>>>>>>> 1b33b999859da64f11c94b8675f188e9a38373e0
        download.save_as(caminho_final)

        browser.close()


if __name__ == "__main__":
    baixar_cnd_federal("12345678000195", r"C:\Users\valbe\PycharmProjects\12_CNDs\data\documentos\Federal")
