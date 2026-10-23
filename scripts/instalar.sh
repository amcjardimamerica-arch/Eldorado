#!/usr/bin/env bash
# A instalação completa do Eldorado (plano C: as ferramentas adotadas), usada por todos os fluxos.
#   1. as bibliotecas de todos os grupos (motores, base, banco, leitura, OCR, leitor universal, idioma, navegador...);
#   2. os programas do sistema: Tesseract com português (e o que o tesserocr exige), Java (o leitor universal);
#   3. os navegadores: Patchright (degrau 4), Camoufox (degrau 5) e Lightpanda (degrau 3, o navegador leve);
#   4. o SearXNG como serviço do próprio fluxo (a metabusca própria), em http://127.0.0.1:8888.
# Cada parte que falhar vira aviso: o sistema segue com as reservas de cada ferramenta (nada é simulado).
set -u
aviso() { echo "::warning::$1"; }
sudo apt-get -qq update && sudo apt-get -qq install -y tesseract-ocr tesseract-ocr-por libtesseract-dev libleptonica-dev pkg-config default-jre-headless > /dev/null \
  || aviso "programas do sistema (Tesseract, Java): a instalação falhou"
python -m pip install -q --upgrade pip uv || aviso "uv não instalou"
GRUPOS="leitura,acesso,descoberta,metabusca,navegador,ocr,universal,idioma,leitura_completa,base,banco,motores"
uv pip install --system -q -e ".[$GRUPOS]" || pip install -q -e ".[$GRUPOS]" || aviso "bibliotecas: a instalação completa falhou"
patchright install --with-deps chromium > /dev/null 2>&1 || aviso "Patchright (degrau 4) não instalou"
python -m camoufox fetch > /dev/null 2>&1 || aviso "Camoufox (degrau 5) não instalou"
LP="${RUNNER_TEMP:-/tmp}/lightpanda"
curl -sfL -o "$LP" https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux && chmod +x "$LP" \
  && echo "ELDORADO_LIGHTPANDA=$LP" >> "${GITHUB_ENV:-/dev/null}" || aviso "Lightpanda (degrau 3) não instalou"
if command -v docker > /dev/null; then
  docker run -d --name searxng -p 127.0.0.1:8888:8080 -v "$PWD/config/searxng:/etc/searxng:rw" searxng/searxng:latest > /dev/null 2>&1 \
    && for i in $(seq 1 30); do curl -sf "http://127.0.0.1:8888/search?q=teste&format=json" > /dev/null && break; sleep 2; done \
    && echo "ELDORADO_SEARXNG=http://127.0.0.1:8888" >> "${GITHUB_ENV:-/dev/null}" || aviso "SearXNG não subiu; a metabusca segue pelo ddgs"
fi
python - <<'P' || true
import importlib
ok = []
for m in ("fitz", "rapidocr", "tesserocr", "tika", "trafilatura", "extruct", "lingua", "usp", "waybackpy", "cdx_toolkit", "ckanapi", "aiolimiter",
          "scrapling", "polars", "xmltodict", "lxml", "liteparse", "dateparser", "datefinder", "htmldate", "duckdb", "datasette", "sqlite_utils", "fastapi",
          "sklearn", "dspy", "pydantic_ai", "orjson", "googleapiclient", "patchright", "camoufox"):
    try:
        importlib.import_module(m); ok.append(m)
    except Exception as e:
        print(f"::warning::ferramenta do plano não importou: {m} ({type(e).__name__}: {str(e)[:80]})")
import os, shutil
binarios = {"tesseract": shutil.which("tesseract"), "java": shutil.which("java"), "lightpanda": os.environ.get("ELDORADO_LIGHTPANDA") or os.path.exists(os.environ.get("RUNNER_TEMP", "/tmp") + "/lightpanda")}
print(f"::notice::instalação completa: {len(ok)} bibliotecas do plano importam; programas: " + ", ".join(f"{k}={'sim' if v else 'não'}" for k, v in binarios.items()))
P
