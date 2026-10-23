#!/usr/bin/env bash
# A instalação completa do Eldorado (plano C: as ferramentas adotadas), usada por todos os fluxos.
#   1. as bibliotecas de todos os grupos (motores, base, banco, leitura, OCR, leitor universal, idioma, navegador...);
#   2. os programas do sistema: Tesseract com português (e o que o tesserocr exige), Java (o leitor universal);
#   3. os navegadores: Patchright (degrau 4), Camoufox (degrau 5) e Lightpanda (degrau 3, o navegador leve);
#   4. o SearXNG como serviço do próprio fluxo (a metabusca própria), em http://127.0.0.1:8888.
# Cada parte que falhar vira aviso: o sistema segue com as reservas de cada ferramenta (nada é simulado).
set -u
# cada parte tem um tempo máximo: passou, vira aviso, e o sistema segue com as reservas (o funcionamento não espera)
inicio=$(date +%s); TEMPOS=""; marca() { TEMPOS="$TEMPOS $1=$(( $(date +%s) - inicio ))s"; }
aviso() { echo "::warning::$1"; }
PROGRAMAS="tesseract-ocr tesseract-ocr-por libtesseract-dev libleptonica-dev pkg-config"
# primeiro sem atualizar a lista (os executores do GitHub já a trazem; a atualização é lenta); só atualiza se faltar
timeout 300 sudo apt-get install -y -qq --no-install-recommends $PROGRAMAS > /dev/null 2>&1 \
  || { timeout 300 sudo apt-get update -qq > /dev/null 2>&1; timeout 300 sudo apt-get install -y -qq --no-install-recommends $PROGRAMAS > /dev/null 2>&1; } \
  || aviso "programas do sistema (Tesseract): a instalação falhou"
marca "programas do sistema"
timeout 120 python -m pip install -q --upgrade pip uv || aviso "uv não instalou"
timeout 1800 python scripts/instalar_bibliotecas.py || { echo "::error::o núcleo do Eldorado não instalou"; exit 1; }
marca "bibliotecas"
timeout 300 patchright install --with-deps chromium > /dev/null 2>&1 || aviso "Patchright (degrau 4) não instalou"
timeout 300 python -m camoufox fetch > /dev/null 2>&1 || aviso "Camoufox (degrau 5) não instalou"
marca "navegadores"
LP="${RUNNER_TEMP:-/tmp}/lightpanda"
curl -sfL -m 120 -o "$LP" https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux && chmod +x "$LP" \
  && echo "ELDORADO_LIGHTPANDA=$LP" >> "${GITHUB_ENV:-/dev/null}" || aviso "Lightpanda (degrau 3) não instalou"
marca "Lightpanda"
if command -v docker > /dev/null; then
  timeout 240 docker run -d --name searxng -p 127.0.0.1:8888:8080 -v "$PWD/config/searxng:/etc/searxng:rw" searxng/searxng:latest > /dev/null 2>&1 \
    && for i in $(seq 1 30); do curl -sf "http://127.0.0.1:8888/search?q=teste&format=json" > /dev/null && break; sleep 2; done \
    && echo "ELDORADO_SEARXNG=http://127.0.0.1:8888" >> "${GITHUB_ENV:-/dev/null}" || aviso "SearXNG não subiu; a metabusca segue pelo ddgs"
fi
marca "SearXNG"
marca "SearXNG"; export TEMPOS
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
print(f"::notice::instalação completa: {len(ok)} de 31 ferramentas do plano importam; programas: " + ", ".join(f"{k}={'sim' if v else 'não'}" for k, v in binarios.items()) + "; tempos:" + os.environ.get("TEMPOS", ""))
P
