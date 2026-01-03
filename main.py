from __future__ import annotations

import argparse
import os
from getpass import getpass
from pathlib import Path
from typing import Iterable

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    args = _parse_args()
    target = Path(args.input).expanduser()
    try:
        pfx_files = _collect_pfx(target)
    except FileNotFoundError as exc:
        print(exc)
        return

    if not pfx_files:
        print(f"Nenhum arquivo .pfx encontrado em {target}")
        return

    output_dir = Path(args.output).expanduser() if args.output else None
    exported: list[tuple[Path, Path]] = []

    for pfx_path in pfx_files:
        password = _resolve_password(pfx_path, args.password)
        if password is None:
            print(f"Senha não fornecida. Pulando {pfx_path.name}.")
            continue

        try:
            key_path, cert_path = _export_bundle(
                pfx_path=pfx_path,
                password=password,
                output_dir=output_dir,
                overwrite=args.force,
            )
        except FileExistsError as exc:
            print(exc)
        except ValueError as exc:
            print(f"Falha ao processar {pfx_path.name}: {exc}")
        else:
            exported.append((key_path, cert_path))
            print(f"OK {pfx_path.name} -> {key_path.name}, {cert_path.name}")

    if not exported:
        print("Nenhum certificado foi exportado.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrai arquivos .key e .cert a partir de pacotes PKCS#12 (.pfx)."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=".",
        help="Arquivo .pfx ou diretório contendo certificados (padrão: diretório atual).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Diretório onde os arquivos serão gravados. Por padrão, usa o diretório de cada .pfx.",
    )
    parser.add_argument(
        "--password",
        help="Senha padrão para todos os arquivos.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescreve arquivos de saída se já existirem.",
    )
    return parser.parse_args()


def _collect_pfx(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".pfx":
        return [path]
    if not path.exists():
        raise FileNotFoundError(f"Caminho não encontrado: {path}")
    return sorted(p for p in path.rglob("*.pfx") if p.is_file())


_PASSWORD_CACHE: dict[str, bytes] = {}


def _resolve_password(pfx_path: Path, cli_password: str | None) -> bytes | None:
    cache_key = str(pfx_path)
    if cache_key in _PASSWORD_CACHE:
        return _PASSWORD_CACHE[cache_key]

    env_key = "PFX_PASSWORD_" + "".join(
        ch if ch.isalnum() else "_" for ch in pfx_path.stem
    ).upper()

    password = cli_password or os.getenv(env_key) or os.getenv("PFX_PASSWORD")

    if password is None:
        try:
            password = getpass(f"Senha para {pfx_path.name}: ")
        except (EOFError, KeyboardInterrupt):
            return None

    resolved = password.encode("utf-8")
    _PASSWORD_CACHE[cache_key] = resolved
    return resolved


def _export_bundle(
    *,
    pfx_path: Path,
    password: bytes,
    output_dir: Path | None,
    overwrite: bool,
) -> tuple[Path, Path]:
    data = pfx_path.read_bytes()
    key, cert, _ = load_key_and_certificates(data, password)

    if key is None or cert is None:
        raise ValueError("O arquivo não contém chave/certificado principal.")

    destination_dir = output_dir or pfx_path.parent
    destination_dir.mkdir(parents=True, exist_ok=True)

    key_path = destination_dir / f"{pfx_path.stem}.key"
    cert_path = destination_dir / f"{pfx_path.stem}.cert"

    if not overwrite:
        _ensure_not_exists([key_path, cert_path])

    key_bytes = key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption(),
    )
    cert_bytes = cert.public_bytes(Encoding.PEM)

    key_path.write_bytes(key_bytes)
    cert_path.write_bytes(cert_bytes)

    return key_path, cert_path


def _ensure_not_exists(paths: Iterable[Path]) -> None:
    clashes = [str(path) for path in paths if path.exists()]
    if clashes:
        raise FileExistsError(
            "Arquivos já existem. Use --force para sobrescrever: " + ", ".join(clashes)
        )


if __name__ == "__main__":
    main()
