"""CERTIFICADO INTERMEDIÁRIO DO SUAP (titular, 03/10/2026) — roda no GitHub.

O SUAP da Câmara de Goiânia (suap.camaragyn.go.gov.br) não envia a cadeia completa do certificado: o navegador completa
sozinho, mas o Python, o curl e a ponte recusam. Este script: (1) pega a cadeia que o servidor envia (openssl);
(2) lê no certificado do site o endereço OFICIAL da autoridade certificadora (AIA, "CA Issuers") e baixa o intermediário
que falta; (3) prova que, com ele, a leitura direta funciona com a verificação LIGADA; (4) grava o intermediário em
config/certificados/ e o relatório em docs/relatorios/certificado-suap/. Nunca desliga a verificação.
"""
from __future__ import annotations

import json
import re
import ssl
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = "suap.camaragyn.go.gov.br"
PASTA = ROOT / "config/certificados"
REL = ROOT / "docs/relatorios/certificado-suap"


def sh(cmd: list[str], entrada: bytes | None = None, t: int = 60) -> str:
    return subprocess.run(cmd, input=entrada, capture_output=True, timeout=t).stdout.decode("utf-8", "ignore")


def run() -> dict:
    out = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "host": HOST}
    cadeia = sh(["openssl", "s_client", "-connect", f"{HOST}:443", "-servername", HOST, "-showcerts"], b"", 40)
    pems = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", cadeia, re.S)
    out["certificados_enviados_pelo_servidor"] = len(pems)
    out["resultado_verificacao_openssl"] = (re.search(r"Verify return code: .*", cadeia) or [""])[0]
    if not pems:
        out["erro"] = "o servidor não respondeu ao openssl"; return out
    folha = sh(["openssl", "x509", "-noout", "-subject", "-issuer", "-enddate", "-text"], pems[0].encode())
    out["folha"] = {"assunto": (re.search(r"subject=.*", folha) or [""])[0], "emissor": (re.search(r"issuer=.*", folha) or [""])[0],
                    "validade": (re.search(r"notAfter=.*", folha) or [""])[0]}
    # segue a cadeia de emissores pelos endereços OFICIAIS que vêm dentro de cada certificado (AIA), até a raiz
    aia = re.findall(r"CA Issuers - URI:(\S+)", folha)
    out["aia"] = aia
    cadeia_pem, atual, vistos = [], aia, set()
    for _nivel in range(4):
        prox = []
        for u in atual:
            if u in vistos:
                continue
            vistos.add(u)
            try:
                with urllib.request.urlopen(u, timeout=30) as r:
                    b = r.read(200000)
                pem = sh(["openssl", "x509", "-inform", "PEM" if b.startswith(b"-----BEGIN") else "DER", "-outform", "PEM"], b)
                if not pem:
                    continue
                info = sh(["openssl", "x509", "-noout", "-subject", "-issuer", "-enddate", "-fingerprint", "-sha256", "-text"], pem.encode())
                cadeia_pem.append(pem)
                sub = (re.search(r"subject=(.*)", info) or ["", ""])[1].strip()
                iss = (re.search(r"issuer=(.*)", info) or ["", ""])[1].strip()
                out.setdefault("cadeia", []).append({"baixado_de": u, "assunto": sub, "emissor": iss,
                                                     "validade": (re.search(r"notAfter=(.*)", info) or ["", ""])[1].strip(),
                                                     "sha256": (re.search(r"Fingerprint=(\S+)", info) or ["", ""])[1]})
                if sub != iss:                                   # não é a raiz: segue para o emissor
                    prox += re.findall(r"CA Issuers - URI:(\S+)", info)
            except Exception as e:  # noqa: BLE001
                out.setdefault("falhas_aia", []).append(f"{u}: {type(e).__name__}")
        if not prox:
            break
        atual = prox
    inter_pem = "".join(cadeia_pem) or None
    if not inter_pem:
        out["erro"] = "não foi possível baixar a cadeia pelo AIA"; return out
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / "suap-camaragyn-cadeia.pem"      # intermediário + raiz, pelos endereços oficiais da Let's Encrypt
    arq.write_text(inter_pem, encoding="utf-8")
    # prova: sem o intermediário falha, com ele (e a verificação LIGADA) abre
    def tenta(ctx):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://{HOST}/", headers={"User-Agent": "Mozilla/5.0 (EldoradoBot)"}), timeout=30, context=ctx) as r:
                return {"status": r.status, "bytes": len(r.read(300000))}
        except Exception as e:  # noqa: BLE001
            return {"erro": f"{type(e).__name__}: {str(e)[:160]}"}
    out["sem_o_intermediario"] = tenta(ssl.create_default_context())
    ctx = ssl.create_default_context(); ctx.load_verify_locations(cafile=str(arq))
    out["com_o_intermediario"] = tenta(ctx)
    out["verificacao_ligada"] = ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
    REL.mkdir(parents=True, exist_ok=True)
    (REL / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: r.get(k) for k in ("certificados_enviados_pelo_servidor", "resultado_verificacao_openssl", "aia", "sem_o_intermediario", "com_o_intermediario", "erro")}, ensure_ascii=False, indent=1))
