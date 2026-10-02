"""CHAVE DE ACIONAMENTO DOS LIVROS E LÉXICO TEMPORÁRIO (titular, 02/10/2026).

Cada livro da Biblioteca ganha um indicador novo, a CHAVE DE ACIONAMENTO:
  · termos   — o que costuma acionar aquela oportunidade: o nome do programa sem anos e números, as siglas
               (PNAB, FIA, CMDCA…) e o financiador;
  · motores  — o ÍNDICE dos motores de busca que já encontraram aquela oportunidade (tirado do histórico do livro);
  · consulta — uma busca pronta para aquela oportunidade.
LÉXICO TEMPORÁRIO: quando a análise preditiva marca a janela de ativação (30 dias antes da abertura prevista até o
encerramento), os termos da chave passam a compor, TEMPORARIAMENTE, o léxico da camada 1 dos motores do índice — ou de
todos os motores regulares, se nenhum ainda encontrou a oportunidade. Fora da janela, saem sozinhos.
Saída: o campo chave_acionamento de cada livro e estado/lexico_temporario_livros.json
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "biblioteca_alexandria/fontes/motores.json"
LEXICO = ROOT / "estado/lexico_temporario_livros.json"
GENERICOS = set(("edital editais chamamento chamada publico publica selecao processo seletivo programa projeto projetos credenciamento aviso "
                 "inscricoes abertas premio concurso fundo municipal estadual federal governo prefeitura secretaria ministerio de da do das dos "
                 "para com em e a o as os no na nos nas sobre ref objeto organizacoes sociedade civil osc oscs entidades apoio fomento termo "
                 "colaboracao brasil goias nacional nova novo publicado diario oficial municipio estado "
                 # 02/10: palavras comuns demais para servir de chave (afogariam o léxico do motor)
                 "organizacao social sociais cultura cultural culturais clima economia comunicacao fisica juridica pessoa pessoas continue lendo "
                 "ongs ong nordeste sudeste sul norte centro oeste regiao metropolitana sao paulo rio janeiro grande minas gerais bahia parana "
                 "santa catarina pernambuco ceara para amazonas brasilia distrito acao acoes artisticas educacao saude esporte infancia juventude "
                 "crianca adolescente idoso idosa mulher mulheres arte artes empresa empresas instituicao instituicoes procedimento subsidiar "
                 "associacoes associacao objetivando firmar parceria parcerias futuro bem maior viva observatorio divulgada divulgado "
                 "refere forma conselho regional estudos festejos agente agentes hospital seccionais natal outorga patrocinadores "
                 "profissionais ministrantes tutores exames abertura prorrogado doacao doacoes solicitar como").split())


def sem(t) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(t or "").lower()) if not unicodedata.combining(c))


def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _ids_dos_motores() -> dict[str, str]:
    """Nome ou rótulo de origem → id do sensor (para o índice dos motores)."""
    m = {}
    for f in (_j(ROOT / "config/investigacao.json", {}).get("fontes") or []):
        m[sem(f.get("nome"))] = "plat-" + f["id"]; m[sem(f["id"])] = "plat-" + f["id"]
    for s in (_j(ROOT / "config/sensores.json", {}).get("sensores_especiais") or []):
        if isinstance(s, dict) and s.get("id"):
            m[sem(s.get("nome"))] = s["id"]; m[sem(s["id"])] = s["id"]
    m.update({"motor pncp": "pncp-api", "pncp": "pncp-api", "piloto - espiao": "piloto-aberto", "piloto - interceptador": "piloto-interceptador"})
    return m


VERBOS = set(("abre abrem abriu lanca lancam lancou apoiar apoia apoio foco que ate mil milhoes milhao reais estabelece criterios voltados "
              "presente tem por selecionar fins celebracao duracao certa inscricoes inscrever inscreva podem pode se recebe recebem oferece "
              "oferecem cria incentivar incentiva divulga publica publicou seleciona selecionar visando visa objetivo destinado destinada "
              "guia captacao captar recursos novo nova edicao primeira segunda terceira").split())
AGREGADOR = re.compile(r"observat[oó]rio|\babcr\b|captadores|prosas|\bcapta\b|agregador|farol cultural|editais|portal de editais|—")
CONECTORES = {"de", "da", "do", "das", "dos", "e"}


def _limpa(t: str) -> str:
    return re.sub(r"\s+", " ", " ".join(w for w in re.findall(r"[a-z0-9]+", sem(t)) if w not in GENERICOS and w not in VERBOS)).strip()


def _siglas(texto: str, caixa_alta: bool) -> list[str]:
    """Sigla de verdade: até 6 letras; em título todo maiúsculo (onde tudo parece sigla), só as de até 5 letras."""
    lim = 5 if caixa_alta else 6
    return [s.lower() for s in re.findall(r"\b[A-Z][A-Z0-9-]{2,%d}\b" % (lim - 1), texto)
            if sem(s) not in GENERICOS and sem(s) not in VERBOS and not COMUM.search(sem(s))]


def termos_da_chave(x: dict) -> list[str]:
    """Nomes próprios e siglas do título (o que identifica a oportunidade) + o financiador real."""
    _bruto = str(x.get("nome_classificado") or x.get("programa") or "").split(" — ")[0]
    if _bruto.rstrip().endswith(("…", "...")):                # título cortado: a última palavra pode estar pela metade
        _bruto = _bruto.rstrip(" .…").rsplit(" ", 1)[0]
    nome = re.sub(r"\b(19|20)\d\d\b|\bn[ºo°.]*\s*\d+[\w/.-]*|r\$\s*[\d.,]+\s*\w*", " ", _bruto)
    letras = [c for c in nome if c.isalpha()]
    caixa_alta = letras and sum(c.isupper() for c in letras) / len(letras) > 0.6
    out = []
    if not caixa_alta:
        palavras = re.findall(r"[A-Za-zÀ-ÿ0-9]+", nome); seq = []
        for w in palavras + ["."]:
            if w[:1].isupper() or (seq and w.lower() in CONECTORES):
                seq.append(w)
            else:
                while seq and seq[-1].lower() in CONECTORES:
                    seq.pop()
                frase = _limpa(" ".join(seq))
                if frase and len(frase) >= 4:
                    out.append(" ".join(w.lower() for w in seq if sem(w) not in GENERICOS and sem(w) not in VERBOS or w.lower() in CONECTORES).strip())
                seq = []
        out = [re.sub(r"^(de|da|do|das|dos|e) |( de| da| do| das| dos| e)$", "", sem(o)).strip() for o in out]
    siglas = _siglas(nome, caixa_alta)
    out = siglas + [o for o in out if o and o not in siglas]
    if siglas and len(out) > len(siglas) and len(out[len(siglas)].split()) == 1:   # "PNAB" + "Audiovisual" → "pnab audiovisual"
        out.insert(len(siglas), f"{siglas[0]} {out[len(siglas)]}")
    # 02/10: título todo em caixa alta (PNCP) não gera frase solta — valem as siglas e o município do órgão (abaixo)
    org = str(x.get("orgao") or "")
    if org and not AGREGADOR.search(sem(org)):
        sig = re.search(r"\(([A-Za-z][\w-]{2,12})\)", org)
        org_t = sig.group(1).lower() if sig else _limpa(re.sub(r"(?i)^(munic[ií]pio de|prefeitura (municipal )?de|secretaria (de estado )?(da|de|do)|governo d[eo]|fundo (municipal|estadual) d[aeo]s?)\s+", "", org))
        if 4 <= len(org_t) <= 40:
            out.append(org_t)
    vist, res = set(), []
    for t in out:
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) >= 4 and t not in vist and t not in GENERICOS and not AGREGADOR.search(t) and not all(w in GENERICOS or w in CONECTORES for w in t.split()):
            vist.add(t); res.append(t)
    return res[:4]


def motores_do_livro(x: dict, ids: dict[str, str]) -> tuple[list[str], list[str]]:
    origens = Counter()
    for h in x.get("historico") or []:
        if h.get("origem"):
            origens[str(h["origem"])] += 1
    for v in ((x.get("livro") or {}).get("checklist") or {}).values():
        if isinstance(v, dict) and v.get("de"):
            origens[str(v["de"])] += 1
    m = re.search(r"criado (?:pelo|por) (.+?) \(", str(x.get("motivo_status") or ""))
    if m:
        origens[m.group(1)] += 1
    resolvidos = []
    for o in origens:
        so = sem(o)
        alvo = ids.get(so) or next((v for k, v in ids.items() if k and len(k) > 4 and (k in so or so in k)), None)
        if alvo and alvo not in resolvidos:
            resolvidos.append(alvo)
    return resolvidos, [o for o, _ in origens.most_common(8)]


def run(hoje: date | None = None) -> dict:
    hoje = hoje or datetime.now(timezone(timedelta(hours=-3))).date()
    C = _j(CAT, {}); ids = _ids_dos_motores(); itens = []; com = 0
    livros = [x for x in C.get("motores") or [] if x.get("papel") != "fonte_de_busca"]
    cand = {x["id"]: termos_da_chave(x) for x in livros}
    # RARIDADE (02/10): uma chave só identifica o livro se for rara na Biblioteca — palavra que aparece em muitos livros
    # ("contratação", "instituto", "meio") não aciona nenhum. Vale a palavra mais rara do termo; siglas sempre valem.
    df = Counter(w for x in livros for w in set(re.findall(r"[a-z0-9]+", sem(f"{x.get('nome_classificado') or x.get('programa') or ''} {x.get('orgao') or ''}"))))
    for x in livros:
        _txt = f"{x.get('nome_classificado') or ''} {x.get('orgao') or ''}"; _l = [c for c in _txt if c.isalpha()]
        siglas = set(_siglas(_txt, bool(_l) and sum(c.isupper() for c in _l) / len(_l) > 0.6))
        bons = []
        for t in cand[x["id"]]:
            ws = [w for w in t.split() if w not in CONECTORES]
            lim = MAX_LIVROS_POR_CHAVE if len(ws) > 1 else MAX_LIVROS_PALAVRA_SOLTA
            raras = [w for w in ws if df[w] <= lim and _proprio(w) and (len(ws) > 1 or len(w) >= 6)]
            if t in siglas or raras:          # sigla, ou ao menos uma palavra rara com cara de nome próprio
                bons.append(t)
        cand[x["id"]] = bons
    for x in livros:
        termos = cand[x["id"]]
        if not termos:
            x.pop("chave_acionamento", None)
            continue
        motores, origens = motores_do_livro(x, ids)
        ch = {"termos": termos, "motores": motores, "origens": origens,
              "consulta": f'"{termos[0]}" ' + ("edital" if "edital" not in termos[0] else "") + f" {hoje.year}".rstrip(),
              "atualizada_em": hoje.isoformat()}
        pv = x.get("previsao") or {}
        try:
            ini, fim = date.fromisoformat(pv.get("ativar_em") or ""), date.fromisoformat(pv.get("encerramento") or "")
        except ValueError:
            ini = fim = None
        if pv.get("situacao") == "prevista" and ini and fim and ini <= hoje <= fim:
            ch["lexico_ativo"] = {"desde": ini.isoformat(), "ate": fim.isoformat()}
            itens.append({"livro": x["id"], "nome": x.get("nome_classificado"), "termos": termos, "motores": motores,
                          "desde": ini.isoformat(), "ate": fim.isoformat(), "abertura_prevista": pv.get("abertura")})
        x["chave_acionamento"] = ch; com += 1
    CAT.write_text(json.dumps(C, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    LEXICO.parent.mkdir(parents=True, exist_ok=True)
    LEXICO.write_text(json.dumps({"gerado_em": hoje.isoformat(), "regra": __doc__.split("Saída")[0].strip(), "itens": itens}, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    return {"livros_com_chave": com, "lexicos_temporarios_ativos": len(itens)}


MAX_TERMOS_POR_MOTOR = 30
MAX_LIVROS_POR_CHAVE = 12                # frase: a palavra mais rara aparece em no máximo 12 livros (Goyazes tem várias faixas)
MAX_LIVROS_PALAVRA_SOLTA = 12           # palavra solta (não sigla): nome próprio com 6+ letras
COMUM = re.compile(r"(cao|coes|mento|mentos|dade|dades|ivo|iva|ivos|ivas|ica|ico|icas|icos|ente|entes|ado|ada|ados|adas|ncia|ncias|vel|veis|"
                   r"oso|osa|ando|endo|indo|ar|er|ir|ao|oes|ista|istas|ismo|agem|ura|uras|eiro|eira|ario|aria)$")


def _proprio(w: str) -> bool:
    """Palavra com cara de nome próprio: não termina como palavra comum do português e não é curta demais."""
    return len(w) >= 5 and not COMUM.search(w) and w not in GENERICOS and w not in VERBOS


def termos_temporarios(sensor_id: str, hoje: date | None = None) -> list[str]:
    """Os termos que entram HOJE no léxico da camada 1 deste motor, pelos livros em janela de ativação.
    Prioridade: livros que JÁ têm este motor no índice; depois os sem índice; dentro de cada grupo, a abertura mais
    próxima. No máximo 30 termos por motor, para o léxico temporário não afogar o léxico próprio do motor."""
    hoje = hoje or date.today()
    vigentes = [it for it in (_j(LEXICO, {}).get("itens") or []) if str(it.get("desde")) <= hoje.isoformat() <= str(it.get("ate"))]
    proprios = sorted([it for it in vigentes if sensor_id in (it.get("motores") or [])], key=lambda it: str(it.get("abertura_prevista") or "9999"))
    gerais = sorted([it for it in vigentes if not it.get("motores")], key=lambda it: str(it.get("abertura_prevista") or "9999"))
    out = []
    for it in proprios + gerais:
        for t in it.get("termos") or []:
            if t not in out and len(out) < MAX_TERMOS_POR_MOTOR:
                out.append(t)
    return out


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=1))
