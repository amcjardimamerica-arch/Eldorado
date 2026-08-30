#!/usr/bin/env python3
"""Camada de acesso do dashboard — senha mensal, cifragem e envio.

Como funciona, de ponta a ponta:

1. **Senha do mês** — derivada de um segredo-mestre (`ACESSO_MASTER`, em GitHub
   Actions Secrets) + o mês corrente, via HMAC-SHA256. Formato AMC-XXXX-XXXX,
   alfabeto sem caracteres ambíguos. Determinística para o robô (que precisa
   cifrar a cada varredura), imprevisível para quem não tem o segredo, e
   **troca sozinha todo dia 1º** — a do mês anterior deixa de abrir qualquer
   coisa, o que implementa a expiração no último dia do mês.
2. **Cifragem** — o dashboard-dados é cifrado com AES-256-GCM (chave derivada
   da senha por PBKDF2-SHA256, 200k iterações). O arquivo publicado no Pages é
   ilegível sem a senha; o navegador decifra localmente via WebCrypto.
3. **Envio** — a senha vai por WhatsApp ao número no Secret `WHATSAPP_PHONE`,
   pela API do CallMeBot (Secret `CALLMEBOT_APIKEY`). Sem credenciais, nada é
   enviado e o job declara a pendência — nunca simula envio.

Subcomandos: senha | proteger | enviar | ciclo (proteger+enviar).
`cryptography` é dependência exclusiva desta ferramenta de CI (justificativa:
AES-GCM não existe na biblioteca-padrão); o núcleo do sistema segue puro.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sem 0/O/1/I

def mes_corrente() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")

def derivar_senha(master: str, mes: str | None = None) -> str:
    mes = mes or mes_corrente()
    dig = hmac.new(master.encode(), f"eldorado-acesso|{mes}".encode(), hashlib.sha256).digest()
    letras = "".join(ALFABETO[b % len(ALFABETO)] for b in dig[:8])
    return f"AMC-{letras[:4]}-{letras[4:]}"

def proteger(master: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # dependência de CI
    senha = derivar_senha(master)
    plano = (ROOT / "docs/dashboard-dados.json").read_bytes()
    salt = os.urandom(16)
    chave = hashlib.pbkdf2_hmac("sha256", senha.strip().upper().encode(), salt, 200_000, dklen=32)
    iv = os.urandom(12)
    ct = AESGCM(chave).encrypt(iv, plano, None)
    b64 = lambda b: base64.b64encode(b).decode()
    (ROOT / "docs/dashboard-dados.enc.js").write_text(
        "window.DADOS_ENC=" + json.dumps({
            "v": 1, "kdf": "PBKDF2-SHA256", "it": 200_000, "cifra": "AES-256-GCM",
            "mes": mes_corrente(), "salt": b64(salt), "iv": b64(iv), "ct": b64(ct),
        }) + ";\n", encoding="utf-8")
    # com proteção ativa, NADA legível vai ao ar
    (ROOT / "docs/dashboard-dados.js").write_text(
        "/* dados protegidos — decifrados no navegador com a senha do mês */\n", encoding="utf-8")
    (ROOT / "docs/dashboard-dados.json").write_text(
        json.dumps({"protegido": True, "mes": mes_corrente(),
                    "nota": "conteúdo cifrado em dashboard-dados.enc.js"}) + "\n", encoding="utf-8")
    return {"protegido": True, "mes": mes_corrente(), "bytes_cifrados": len(ct)}

def enviar(master: str) -> dict:
    fone = os.getenv("WHATSAPP_PHONE", "").strip()
    apikey = os.getenv("CALLMEBOT_APIKEY", "").strip()
    if not fone or not apikey:
        return {"enviado": False,
                "pendencia": "configure os Secrets WHATSAPP_PHONE e CALLMEBOT_APIKEY para envio automático por WhatsApp"}
    senha = derivar_senha(master)
    mes = datetime.now(timezone.utc).strftime("%m/%Y")
    texto = (f"A.M.C. Jardim América — painel de captação.\n"
             f"Senha de {mes}: {senha}\n"
             f"Válida até o último dia do mês. Uso pessoal; não repasse.")
    url = ("https://api.callmebot.com/whatsapp.php?" +
           urllib.parse.urlencode({"phone": fone, "text": texto, "apikey": apikey}))
    req = urllib.request.Request(url, headers={"User-Agent": "Eldorado-OSC/3.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        corpo = r.read(2000).decode("utf-8", "replace")
    ok = r.status == 200
    return {"enviado": ok, "http": r.status, "resposta": corpo[:120]}

def main():
    acao = sys.argv[1] if len(sys.argv) > 1 else "ciclo"
    master = os.getenv("ACESSO_MASTER", "").strip()
    if not master:
        print(json.dumps({"erro": "Secret ACESSO_MASTER ausente — proteção não ativada",
                          "efeito": "o dashboard permanece sem cifragem até o segredo ser criado"},
                         ensure_ascii=False))
        return
    if acao == "senha":
        print(derivar_senha(master)); return
    saida = {}
    if acao in ("proteger", "ciclo"):
        saida["proteger"] = proteger(master)
    if acao in ("enviar", "ciclo"):
        saida["enviar"] = enviar(master)
    print(json.dumps(saida, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
