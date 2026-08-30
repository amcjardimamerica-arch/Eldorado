from __future__ import annotations
import hashlib, json, mimetypes, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INJECTION=re.compile(r"ignore .*instruction|disregard .*previous|system prompt|prompt injection|reveal .*secret",re.I)

def main(folder: str):
    base=Path(folder).resolve(); items=[]
    if not base.is_dir(): raise SystemExit("Informe um diretório válido.")
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        data=path.read_bytes(); rel=path.relative_to(base).as_posix()
        sample=data[:300000].decode("utf-8","ignore")
        low=rel.lower()
        categoria=("lei" if any(x in low for x in ["lei ","decreto","constituição","constituicao","resolução","resolucao"]) else
                   "manual" if any(x in low for x in ["manual","guia","orientaç","requisitos"]) else
                   "modelo" if any(x in low for x in ["modelo","declaração","declaracao","plano de trabalho"]) else "referencia")
        items.append({"arquivo":rel,"categoria":categoria,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"tipo":mimetypes.guess_type(path.name)[0] or "application/octet-stream","quarentena_prompt_injection":bool(INJECTION.search(sample)),"status_juridico":"verificar_vigencia_e_fonte_oficial"})
    out=ROOT/"acervo_importado/catalogo.json"; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"origem":"04 - Legislação e Modelos.rar","politica":"Catálogo por hash; documentos não são executados e não substituem fonte oficial consolidada.","arquivos":items},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{len(items)} arquivos catalogados em {out}")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Uso: python scripts/importar_acervo.py DIRETORIO")
    main(sys.argv[1])
