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
    aia = re.findall(r"CA Issuers - URI:(\S+)", folha)
    out["aia"] = aia
    inter_pem = None
    for u in aia:
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                b = r.read(200000)
            der = b if not b.startswith(b"-----BEGIN") else None
            inter_pem = sh(["openssl", "x509", "-inform", "DER" if der else "PEM", "-outform", "PEM"], b) or None
            if inter_pem:
                info = sh(["openssl", "x509", "-noout", "-subject", "-issuer", "-enddate", "-fingerprint", "-sha256"], inter_pem.encode())
                out["intermediario"] = {"baixado_de": u, "dados": info.strip().splitlines()}
                break
        except Exception as e:  # noqa: BLE001
            out.setdefault("falhas_aia", []).append(f"{u}: {type(e).__name__}")
    if not inter_pem:
        out["erro"] = "não foi possível baixar o intermediário pelo AIA"; return out
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / "suap-camaragyn-intermediario.pem"
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
