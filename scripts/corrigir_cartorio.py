#!/usr/bin/env python3
"""Correção do Cartório: o percentual e os quadradinhos passam a ser sobre os 12 pontos.

CAUSA (diagnosticada no site publicado, cartorio.html + dados/cartorio.json):
  * `eficiencia` de cada certidão = resolvidos / faltavam, e `faltavam` é só a lista de itens
    que estavam indisponíveis quando a oportunidade entrou na fila (1 a 12). Uma certidão que
    entrou com 1 item faltando e o resolveu mostra "1 de 1 · 100%" e UM quadradinho verde.
  * Os outros 11 itens (que o motor já tinha lido da notícia/página) eram desenhados com a
    classe "" = cinza, igual a "nada", e a legenda dizia "cinza: ainda falta" (errado: o que
    falta é vermelho). Resultado: 100% com 1 verde, ou "9 de 10" com 9 verdes e 3 sem cor.
  * Os cartões do topo ("Eficiência dos itens 55%", "Completas 26") usam o mesmo denominador.

CORREÇÃO: cada certidão passa a mostrar os 12 pontos em 4 estados (verde = certificado no
documento oficial; amarelo = dispensado com justificativa; azul = já constava antes do Cartório,
SEM certidão; vermelho = falta) e o % principal = (verde + amarelo) / 12. O % do pedido
(resolvidos/faltavam) continua, rotulado como "pedido". Cartões e filtro "completas" idem.

USO (na raiz do repositório):
    python scripts/corrigir_cartorio.py            # aplica nos arquivos que contêm a página/gerador
    python scripts/corrigir_cartorio.py --dados    # também enriquece docs/dados/cartorio.json
    python scripts/corrigir_cartorio.py --verificar
É idempotente (marcador CARTORIO-12-PONTOS-V1). Funciona em .html estático e em template Python
(tenta também com chaves duplicadas {{ }} de f-string).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MARCA = "CARTORIO-12-PONTOS-V1"
DOZE = ["Objeto", "Prazo de inscrição", "Resultado", "Prazo de recurso", "Valor", "Órgão / financiador",
        "Território", "Esfera", "Requisitos", "Anexos", "Destinação", "Área de atuação"]

# (antigo, novo) — cada antigo é um trecho EXATO da página publicada em 10/10/2026.
JS_COB = (
    '/* ' + MARCA + ' */\n'
    'function cob(c){const I=c.itens||{},D=c.dispensas||{},F=c.faltavam||[];'
    'const o=DOZE.filter(k=>I[k]).length,d=DOZE.filter(k=>!I[k]&&D[k]).length,'
    'f=DOZE.filter(k=>!I[k]&&!D[k]&&F.includes(k)).length,j=DOZE.length-o-d-f;'
    'return{o,d,f,j,cert:(o+d)/DOZE.length,cobre:(o+d+j)/DOZE.length}}\n'
)
PATCHES = [
    # 1) função auxiliar (antes de montar)
    ("function montar(){\n  const R=DADOS.resumo||{};",
     JS_COB + "function montar(){\n  const R=DADOS.resumo||{};\n"
     "  const KS=(DADOS.certidoes||[]).map(cob),SOMA=g=>KS.reduce((a,k)=>a+g(k),0),N12=KS.length*DOZE.length;"),
    # 2) cartões: dois números honestos no lugar de um
    ('["Eficiência dos itens",pct(R.eficiencia_itens),`${R.itens_obtidos||0} obtidos + ${R.itens_dispensados||0} dispensados de ${R.itens_que_faltavam||0}`,1],',
     '["Certificado nos 12 pontos",pct(N12?SOMA(k=>k.o+k.d)/N12:null),`${SOMA(k=>k.o)} verdes + ${SOMA(k=>k.d)} dispensados de ${N12} (${KS.length} certidões × 12) · ${SOMA(k=>k.j)} já constavam sem certidão · ${SOMA(k=>k.f)} faltam`,1],'
     '["Eficiência do pedido",pct(R.eficiencia_itens),`${R.itens_obtidos||0} obtidos + ${R.itens_dispensados||0} dispensados de ${R.itens_que_faltavam||0} que faltavam na entrada da fila (não é % dos 12)`],'),
    ('["Completas",R.certidoes_completas||0,"site oficial + todos os itens que faltavam"],',
     '["12 de 12 certificados",KS.filter(k=>k.o+k.d===12).length,"todos os 12 em verde/amarelo, com certidão"],'
     '["Sem item faltando",KS.filter((k,i)=>k.f===0&&(DADOS.certidoes[i].link_oficial)).length,`site oficial + nenhum vermelho (pedido atendido: ${R.certidoes_completas||0}) · pode haver itens só da notícia (azuis)`],'),
    # 3) barras por item: deixa claro que o denominador é "pedidos"
    ("<small>${pct(x.eficiencia)} de ${f}</small>", "<small>${pct(x.eficiencia)} de ${f} pedidos</small>"),
    # 4) filtro "completas" = nenhum ponto vermelho
    ('(s==="completa"?(!(c.ainda_faltam||[]).length&&c.link_oficial)', '(s==="completa"?(cob(c).f===0&&c.link_oficial)'),
    # 5) ordena pela cobertura real
    ('.toLowerCase().includes(q)));\n  const el=document.getElementById("lista");',
     '.toLowerCase().includes(q)));\n  L.sort((a,b)=>cob(b).cert-cob(a).cert||cob(b).cobre-cob(a).cobre);\n  const el=document.getElementById("lista");'),
    # 6) quadradinhos: 4 estados (azul = já constava)
    ('const mini=DOZE.map(k=>`<i class="${(c.itens||{})[k]?"o":(c.dispensas||{})[k]?"d":(c.faltavam||[]).includes(k)?"f":""}" title="${esc(k)}"></i>`).join("");',
     'const K=cob(c);const mini=DOZE.map(k=>`<i class="${(c.itens||{})[k]?"o":(c.dispensas||{})[k]?"d":(c.faltavam||[]).includes(k)?"f":"j"}" title="${esc(k)}"></i>`).join("");'),
    # 7) linha de resumo da certidão: mostra os 12, não só os que faltavam
    ('${(c.resolvidos||[]).length} de ${(c.faltavam||[]).length} itens resolvidos',
     '${K.o+K.d} de 12 pontos certificados (${K.o} verdes, ${K.d} dispensados) · ${K.j} já constavam sem certidão · ${K.f} faltam · pedido: ${(c.resolvidos||[]).length} de ${(c.faltavam||[]).length}'),
    # 8) % principal = pontos certificados / 12
    ('<div class="pct">${pct(c.eficiencia)}</div>',
     '<div class="pct">${pct(K.cert)}<br><small style="font-size:11px;font-weight:400;color:var(--suave)">com os já constantes ${pct(K.cobre)}</small></div>'),
    # 9) texto do item azul
    ("já constava antes do Cartório</div>", "já constava antes do Cartório · sem certidão (não conferido no documento oficial)</div>"),
    # 10) CSS do quadradinho azul
    (".corpo{padding:12px 14px}", ".mini i.j{background:#8FB1D9}\n.corpo{padding:12px 14px}"),
    # 11) legenda (estava errada: cinza ≠ falta)
    ("Verde: obtido no documento oficial · amarelo: dispensado (o edital comprova que o requisito não se aplica) · cinza: ainda falta.",
     "Cada certidão tem 12 quadradinhos. Verde: certificado no documento oficial · amarelo: dispensado (o edital comprova que o requisito não se aplica) · azul: já constava antes do Cartório, sem certidão (ainda não conferido no documento) · vermelho: ainda falta. O % grande da certidão é (verde + amarelo) ÷ 12; o % do pedido (resolvidos ÷ os que faltavam na entrada) aparece só como “pedido”."),
]


def _variantes(antigo: str, novo: str):
    yield antigo, novo
    # templates Python (f-string/.format) duplicam as chaves
    a2, n2 = antigo.replace("{", "{{").replace("}", "}}"), novo.replace("{", "{{").replace("}", "}}")
    if a2 != antigo:
        yield a2, n2


def aplicar_em_texto(txt: str) -> tuple[str, list[str], list[str]]:
    """Devolve (texto novo, aplicados, ausentes). Idempotente."""
    if MARCA in txt:
        return txt, [], []
    aplicados, ausentes = [], []
    for i, (a, n) in enumerate(PATCHES, 1):
        for av, nv in _variantes(a, n):
            if av in txt:
                txt = txt.replace(av, nv, 1)
                aplicados.append(f"{i:02d}")
                break
        else:
            ausentes.append(f"{i:02d}")
    return txt, aplicados, ausentes


def candidatos(raiz: Path) -> list[Path]:
    try:
        arqs = subprocess.run(["git", "ls-files"], cwd=raiz, capture_output=True, text=True, timeout=60).stdout.split("\n")
    except Exception:
        arqs = [str(p.relative_to(raiz)) for p in raiz.rglob("*") if p.is_file()]
    out = []
    for a in arqs:
        p = raiz / a
        if not a or p.suffix not in (".html", ".py", ".js", ".tmpl", ".j2") or not p.is_file() or "tests/" in a:
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "Eficiência dos itens" in t and "DOZE" in t:
            out.append(p)
    return out


def cobertura(c: dict) -> dict:
    """Mesma conta do navegador, para quem consome o JSON (relatórios, planilhas)."""
    it, ds, fa = c.get("itens") or {}, c.get("dispensas") or {}, c.get("faltavam") or []
    estados = {}
    for k in DOZE:
        estados[k] = "certificado" if k in it else "dispensado" if k in ds else "falta" if k in fa else "ja_constava"
    n = lambda e: sum(1 for v in estados.values() if v == e)
    return {"estados": estados, "certificados": n("certificado"), "dispensados": n("dispensado"),
            "ja_constavam": n("ja_constava"), "faltam": n("falta"),
            "pct_certificado_12": round((n("certificado") + n("dispensado")) / 12, 4),
            "pct_cobertura_12": round((n("certificado") + n("dispensado") + n("ja_constava")) / 12, 4)}


def enriquecer_dados(d: dict) -> dict:
    cs = d.get("certidoes") or []
    tot = {"certificados": 0, "dispensados": 0, "ja_constavam": 0, "faltam": 0}
    doze_certos = sem_falta = 0
    for c in cs:
        cb = cobertura(c)
        c["cobertura_12"] = cb
        for k in tot:
            tot[k] += cb[k]
        doze_certos += cb["certificados"] + cb["dispensados"] == 12
        sem_falta += cb["faltam"] == 0 and bool(c.get("link_oficial"))
    n12 = len(cs) * 12
    d.setdefault("resumo", {}).update({
        "pontos_12_total": n12, **{f"pontos_{k}": v for k, v in tot.items()},
        "pct_certificado_12": round((tot["certificados"] + tot["dispensados"]) / n12, 4) if n12 else None,
        "certidoes_12_de_12": doze_certos, "certidoes_sem_item_faltando": sem_falta,
        "nota_denominador": "eficiencia_itens = resolvidos/faltavam na ENTRADA da fila (não é % dos 12); use pct_certificado_12.",
    })
    return d


def main(argv: list[str]) -> int:
    raiz = Path.cwd()
    if "--verificar" in argv:
        faltam = [str(p) for p in candidatos(raiz)]
        print("Arquivos ainda NÃO corrigidos:" if faltam else "Nada pendente.", *faltam, sep="\n  ")
        return 1 if faltam else 0
    alvos = candidatos(raiz)
    if not alvos:
        print("Nenhum arquivo com a página do Cartório encontrado (procurei 'Eficiência dos itens' + DOZE).\n"
              "Procure o gerador (grep -ril 'Eficiência dos itens' .) e rode:\n"
              "  python scripts/corrigir_cartorio.py --arquivo CAMINHO", file=sys.stderr)
    if "--arquivo" in argv:
        alvos = [Path(argv[argv.index("--arquivo") + 1])]
    rc = 0
    for p in alvos:
        txt = p.read_text(encoding="utf-8")
        novo, ap, au = aplicar_em_texto(txt)
        if MARCA in txt:
            print(f"{p}: já corrigido")
            continue
        if au:
            print(f"{p}: ATENÇÃO — trechos não encontrados (página mudou?): {au}", file=sys.stderr)
            rc = 2
        if ap:
            p.write_text(novo, encoding="utf-8")
            print(f"{p}: corrigido ({len(ap)} trechos)")
    if "--dados" in argv:
        for dj in [raiz / "docs/dados/cartorio.json"]:
            if dj.exists():
                d = json.loads(dj.read_text(encoding="utf-8"))
                dj.write_text(json.dumps(enriquecer_dados(d), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
                print(f"{dj}: cobertura_12 gravada em cada certidão e no resumo")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
