import requests, time

def resolver_captcha_2captcha(api_key, imagem_bytes):
    files = {"file": ("captcha.png", imagem_bytes)}
    data = {"key": api_key, "method": "post"}
    r = requests.post("http://2captcha.com/in.php", files=files, data=data).text

    if not r.startswith("OK|"):
        raise Exception("Erro 2captcha envio: " + r)

    captcha_id = r.split("|")[1]

    for _ in range(20):
        time.sleep(5)
        res = requests.get(
            "http://2captcha.com/res.php",
            params={"key": api_key, "action": "get", "id": captcha_id}
        ).text

        if res == "CAPCHA_NOT_READY":
            continue
        if res.startswith("OK|"):
            return res.split("|")[1]

        raise Exception("Erro 2captcha retorno: " + res)

    raise Exception("Timeout 2captcha")
