from __future__ import annotations

import os
from pathlib import Path

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from dotenv import load_dotenv

BASE_DIR = Path("credenciais")
CERT_SOURCE_DIR = BASE_DIR / "certificados"
KEYS_DIR = BASE_DIR / "keys"
CERTS_DIR = BASE_DIR / "certs"
PEMS_DIR = BASE_DIR / "pems"


def main() -> None:
    load_dotenv()
    _prepare_directories()
    pfx_files = sorted(CERT_SOURCE_DIR.glob("*.pfx"))

    if not pfx_files:
        print("Nenhum arquivo .pfx encontrado em credenciais/certificados.")
        return

    password = _resolve_password()
    exported = 0

    for pfx_path in pfx_files:
        try:
            key_path, cert_path, pem_path = _export_bundle(
                pfx_path=pfx_path,
                password=password,
            )
        except ValueError as exc:
            print(f"Falha ao processar {pfx_path.name}: {exc}")
            continue

        exported += 1
        print(
            f"{pfx_path.name} -> "
            f"{KEYS_DIR.name}/{key_path.name}, "
            f"{CERTS_DIR.name}/{cert_path.name}, "
            f"{PEMS_DIR.name}/{pem_path.name}"
        )

    if exported == 0:
        print("Nenhum certificado foi exportado.")


def _prepare_directories() -> None:
    for folder in (BASE_DIR, CERT_SOURCE_DIR, KEYS_DIR, CERTS_DIR, PEMS_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def _resolve_password() -> bytes:
    password = (
        os.getenv("PFX_PASSWORD")
        or os.getenv("DEFAULT_CERT_PASSWORD")
        or "1234"
    )
    return password.encode("utf-8")


def _export_bundle(*, pfx_path: Path, password: bytes) -> tuple[Path, Path, Path]:
    data = pfx_path.read_bytes()
    key, cert, _ = load_key_and_certificates(data, password)

    if key is None or cert is None:
        raise ValueError("O arquivo nao contem chave/certificado principal.")

    key_bytes = key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption(),
    )
    cert_bytes = cert.public_bytes(Encoding.PEM)
    pem_bytes = key_bytes + b"\n" + cert_bytes

    key_path = KEYS_DIR / f"{pfx_path.stem}.key"
    cert_path = CERTS_DIR / f"{pfx_path.stem}.cert"
    pem_path = PEMS_DIR / f"{pfx_path.stem}.pem"

    key_path.write_bytes(key_bytes)
    cert_path.write_bytes(cert_bytes)
    pem_path.write_bytes(pem_bytes)

    return key_path, cert_path, pem_path


if __name__ == "__main__":
    main()
