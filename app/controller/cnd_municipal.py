from playwright.sync_api import sync_playwright
import os, dotenv, requests
from app.utils.resolver_capcha import resolver_captcha_2captcha

dotenv.load_dotenv()
API_2CAPTCHA = os.getenv("API_2CAPTCHA")
URL = "https://grpfordam.sefin.fortaleza.ce.gov.br/grpfor/pagesPublic/certidoes/emitirCertidao.seam"

def baixar_cnd_fortaleza(cnpj):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")

        page.select_option("#pesquisaForm\\:tipoCertidaoDecorate\\:tipoCertidao", "6")
        page.click("#pesquisaForm\\:tipoPessoaDecorate\\:j_id358\\:1")

        page.fill("#pesquisaForm\\:cpfPessoaDec\\:cpf", cnpj)

        captcha_src = page.get_attribute("#pesquisaForm\\:imagem", "src")
        cookies = page.context.cookies()

        sess = requests.Session()
        for c in cookies:
            sess.cookies.set(c["name"], c["value"])

        captcha_img = sess.get(captcha_src).content
        captcha = resolver_captcha_2captcha(API_2CAPTCHA, captcha_img)

        page.fill("#pesquisaForm\\:captchaDecor\\:inputCaptcha", captcha)

        with page.expect_download() as download_info:
            page.click("#pesquisaForm\\:btnEmitir")

        download = download_info.value
        path = f"CND_Fortaleza_{cnpj}.pdf"
        download.save_as(path)

        browser.close()