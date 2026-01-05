from playwright.sync_api import sync_playwright

def baixar_cnd(cnpj: str, caminho_saida: str = "cnd.pdf"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://consultapublica.sefaz.ce.gov.br/certidaonegativa/preparar-consultar")

        # Selecionar tipo devedor CNPJ
        page.click('label[for="cnpj"]')
        page.fill("#codigoDevedor", cnpj)
        page.click("button:has-text('Pesquisar')")

        # Esperar a tabela carregar
        page.wait_for_selector("#tabelaDados tr button.btn-outline-secondary")

        # Abrir a nova aba do PDF
        with page.expect_popup() as popup_info:
            page.click("#tabelaDados tr button.btn-outline-secondary")
        pdf_page = popup_info.value

        # Esperar carregar
        pdf_page.wait_for_load_state("networkidle")

        # Salvar PDF
        pdf_bytes = pdf_page.pdf(format="A4", print_background=True)
        with open(caminho_saida, "wb") as f:
            f.write(pdf_bytes)

        browser.close()