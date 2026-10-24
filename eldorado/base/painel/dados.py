"""Os dados do painel, gerados do sistema novo (titular, 23/10/2026): o site é a imagem atual do sistema.

O painel é a mesma página do Eldorado0 (o HTML, os scripts e as imagens em painel/pagina/), mas NENHUM dado do Eldorado0:
cada seção que a página lê parte do molde (painel/molde/: só a estrutura, todos os valores vazios) e é preenchida com o
sistema novo quando ele tem o dado; a seção sem correspondente fica vazia, sem nada inventado.

De onde vem cada dado:
  - os motores: os 47 do estudo (config/motores_previstos.json), as configurações dos construídos
    (eldorado/motores/canal/config/), o registro (config/modulos.toml), a agenda de partida (config/agenda.toml), as
    execuções registradas no Cérebro (cerebro.db: execucao_motor) e o estado de cada motor (cerebro.db: motor_fonte);
  - os livros: a Biblioteca (biblioteca.db: livro, livro_dados, passaporte, certidao, achado, lei).
"""

from __future__ import annotations

import copy
import json
import shutil
import sqlite3
import tomllib
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

AQUI = Path(__file__).parent
MOLDE = AQUI / "molde"
PAGINA = AQUI / "pagina"
BR = ZoneInfo("America/Sao_Paulo")
ITENS_DO_CARTORIO = (
    "Objeto",
    "Prazo de inscrição",
    "Resultado",
    "Prazo de recurso",
    "Valor",
    "Órgão / financiador",
    "Território",
    "Esfera",
    "Requisitos",
    "Anexos",
    "Modalidade",
)
CATEGORIAS = {
    "diario_oficial": ("Diários oficiais", "#7a5c2e"),
    "api_oficial": ("APIs oficiais", "#2e6b7a"),
    "site_oficial": ("Sites de órgãos e programas", "#3f7a2e"),
    "plataforma": ("Portais do terceiro setor", "#6b2e7a"),
    "busca": ("Pilotos (Espião e Interceptador)", "#7a2e3f"),
}
CANAL_CATEGORIA = {"diario": "diario_oficial", "api": "api_oficial", "portal": "plataforma"}
FASES = {
    "recepcao": "Recepção",
    "certificacao": "Certificação",
    "preparacao": "Preparação",
    "validacao": "Validação",
    "analise externa": "Análise externa",
    "farol": "Farol",
    "arquivo": "Arquivo",
}


def _molde(nome: str) -> Any:
    return json.loads((MOLDE / nome).read_text(encoding="utf-8"))


def _item(qual: str, /, **valores) -> dict[str, Any]:
    base = copy.deepcopy(_molde("itens.json")[qual])
    base.update({k: v for k, v in valores.items() if k in base or k.startswith("_")})
    return base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _data_br(iso: str | None) -> str | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso).astimezone(BR).date().isoformat()
    except ValueError:
        return iso[:10]


class Sistema:
    """A leitura do sistema novo (somente leitura)."""

    def __init__(self, raiz: Path = Path(".")):
        self.raiz = raiz
        d = raiz / "dados"
        self.bib = sqlite3.connect(f"file:{d / 'biblioteca.db'}?mode=ro", uri=True)
        self.bib.row_factory = sqlite3.Row
        self.cer = sqlite3.connect(f"file:{d / 'cerebro.db'}?mode=ro", uri=True)
        self.cer.row_factory = sqlite3.Row
        self.estudo = json.loads((raiz / "config/motores_previstos.json").read_text(encoding="utf-8"))["motores"]
        self.configs = {p.stem: tomllib.loads(p.read_text(encoding="utf-8")) for p in (raiz / "eldorado/motores/canal/config").glob("*.toml")}
        mod = tomllib.loads((raiz / "config/modulos.toml").read_text(encoding="utf-8")).get("modulo", [])
        self.registrados = {Path(m["parametros"]["configuracao"]).stem for m in mod if "configuracao" in m.get("parametros", {})}
        self.registrados |= {m["parametros"].get("id") or m["classe"].split(":")[-1].lower() for m in mod if "configuracao" not in m.get("parametros", {})}
        ag = tomllib.loads((raiz / "config/agenda.toml").read_text(encoding="utf-8")).get("modulo", [])
        self.agenda = {a["id"]: a for a in ag}
        self.hoje = _agora().astimezone(BR).date().isoformat()
        cols = {r[1] for r in self.bib.execute("PRAGMA table_info(livro_dados)")}
        self._escada = "d.escada" if "escada" in cols else "NULL AS escada"   # um banco ainda não migrado (a produção migra antes)
        esp = d / "biblioteca.db"                                   # as empresas, na Biblioteca
        self.esp = sqlite3.connect(f"file:{esp}?mode=ro", uri=True) if esp.exists() else None
        if self.esp is not None:
            self.esp.row_factory = sqlite3.Row
            if not self.esp.execute("SELECT 1 FROM sqlite_master WHERE name = 'empresa'").fetchone():
                self.esp = None                                       # a Biblioteca ainda sem as empresas (antes da migração 9)

    def execucoes(self) -> dict[str, list[sqlite3.Row]]:
        por = defaultdict(list)
        for r in self.cer.execute("SELECT * FROM execucao_motor ORDER BY inicio DESC"):
            por[r["motor"]].append(r)
        return por

    def estado(self, mid: str) -> list[sqlite3.Row]:
        """O estado das fontes do motor, dentro do Cérebro (motor_fonte)."""
        try:
            from ...motores.canal.estado import SQL_FONTES
            return list(self.cer.execute(SQL_FONTES, (mid,)))
        except sqlite3.Error:
            return []

    def livros_abertos(self) -> list[sqlite3.Row]:
        return list(
            self.bib.execute(
                "SELECT l.*, d.abrangencia, d.esfera, d.inscricao_inicio, d.inscricao_fim, d.resultado_em, d.area AS area_d, d.validacao, "
                f"d.situacao_prazo, d.municipio, d.origem, {self._escada}, p.fase "
                "FROM livro l JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p ON p.livro_id = l.id "
                "WHERE d.situacao_prazo = 'aberta' AND l.situacao <> 'excluido' ORDER BY d.inscricao_fim"
            )
        )

    def certidoes(self, ids: list[str]) -> dict[str, dict[str, str]]:
        from ..missao import itens as I

        por = defaultdict(list)
        for r in self.bib.execute("SELECT livro_id, item, valor, fase, trecho, pagina, id FROM certidao WHERE situacao = 'comprovado'"):
            if r["livro_id"] in ids:
                por[r["livro_id"]].append(dict(r))
        return {lid: {k: v.get("valor") for k, v in I.melhor(cs).items()} for lid, cs in por.items()}

    def checklist(self, ids: list[str]) -> dict[str, dict[str, dict[str, str]]]:
        """O checklist dos 12 itens de cada livro, exatamente como o livro tem: comprovado (o valor) ou dispensado pelo
        Chrome (a justificativa); o resto, vazio."""
        from ..missao import itens as I
        alvo, por = set(ids), defaultdict(list)
        for r in self.bib.execute("SELECT livro_id, item, valor, situacao, fase, justificativa, trecho, pagina, id, em FROM certidao"):   # a regra do livro
            if r["livro_id"] in alvo:
                por[r["livro_id"]].append(dict(r))
        saida = {}
        for lid, cs in por.items():
            m = I.melhor(cs)
            saida[lid] = {k: ({"s": m[k]["situacao"], "v": (m[k].get("valor") if m[k]["situacao"] == "comprovado" else m[k].get("justificativa")) or ""}
                              if I.resolvido(m.get(k)) else {"s": "", "v": ""}) for k in I.DOZE}
        return saida

    def motor_do_livro(self) -> dict[str, str]:
        m = {}
        for r in self.bib.execute("SELECT livro_id, motor FROM achado WHERE livro_id IS NOT NULL ORDER BY encontrado_em"):
            m.setdefault(r["livro_id"], r["motor"])
        return m


def _categoria(sis: Sistema, mid: str, tipo: str) -> str:
    if tipo == "piloto":
        return "busca"
    canal = (sis.configs.get(mid, {}).get("motor") or {}).get("canal")
    return CANAL_CATEGORIA.get(canal or "", "site_oficial")


def _motores(sis: Sistema) -> tuple[list[dict], dict, dict]:
    """O estado de cada um dos 47 motores, a descrição e os números, pelo que o sistema registra."""
    ex = sis.execucoes()
    status, descricao, sala = [], {}, []
    for m in sis.estudo:
        mid, nome = m["id"], m["nome"]
        cfg = sis.configs.get(mid, {})
        construido = mid in sis.registrados or m["tipo"] == "piloto" and m["situacao"] == "conforme"
        execs = ex.get(mid, [])
        ultima = execs[0] if execs else None
        hoje = [e for e in execs if _data_br(e["inicio"]) == sis.hoje]
        fontes = sis.estado(mid)
        falhas = sum(1 for f in fontes if f["situacao"] == "erro") if fontes else 0
        if not construido:
            luz, res = "cinza", f"a construir ({m['situacao']})"
        elif not ultima:
            luz, res = "cinza", "construído; ainda sem execução registrada"
        elif ultima["erro"]:
            luz, res = "vermelho", f"a última execução falhou: {str(ultima['erro'])[:160]}"
        elif hoje:
            n = sum(e["achados"] or 0 for e in hoje)
            luz, res = (
                ("vermelho" if fontes and falhas == len(fontes) else "verde"),
                f"leu hoje ({len(hoje)}x): {n} achado(s)" + (f"; {falhas} de {len(fontes)} fonte(s) com erro" if falhas else ""),
            )
        else:
            luz, res = "cinza", f"não leu hoje (última leitura em {_data_br(ultima['inicio'])})"
        ag = sis.agenda.get(mid, {})
        status.append(
            _item(
                "status_motor",
                id=mid,
                nome=nome,
                luz=luz,
                resultado=res,
                leitura_do_dia={"estado": "leu" if hoje else "sem leitura", "texto": res},
                luz_do_dia=luz,
                resultado_do_dia=res,
                observacoes=[m["observacao"]] if m.get("observacao") else [],
                ultima_leitura=(ultima["inicio"] if ultima else ""),
                agenda=", ".join(ag.get("horarios", [])) and f"ponto de partida {', '.join(ag.get('horarios', []))} (o Cérebro decide)",
            )
        )
        sala.append(_item("sala_motor", id=mid, nome=nome, luz=luz, ultima_leitura=(ultima["inicio"] if ultima else ""), resultado=res))
        rotas = [{"nome": f.get("nome", ""), "url": f.get("url", ""), "tipo": f.get("tipo", "pagina")} for f in cfg.get("fonte", [])]
        rotas += [{"nome": f"alvo · {a.get('nome', '')}", "url": (a.get("enderecos") or [""])[0], "tipo": "alvo"} for a in cfg.get("alvo", [])]
        lex = cfg.get("lexico", {})
        descricao[mid] = _item(
            "descricao_motor",
            nome=nome,
            perfil=m["categoria_nome"],
            tipo=m["tipo"],
            finalidade=m["finalidade"] or (cfg.get("motor") or {}).get("finalidade", ""),
            coleta=("computador local" if any(f.get("exige_brasil") for f in cfg.get("fonte", [])) else "nuvem") if construido else "",
            objetivo=(cfg.get("motor") or {}).get("finalidade", ""),
            como_funciona=(
                f"{len(cfg.get('fonte', []))} rota(s) e {len(cfg.get('alvo', []))} alvo(s); canal {(cfg.get('motor') or {}).get('canal', '')}"
                if cfg
                else ("piloto" if m["tipo"] == "piloto" else "")
            ),
            agenda=", ".join(ag.get("horarios", [])),
            agenda_detalhe={
                "horarios_brt": ",".join(ag.get("horarios", [])),
                "dias": "todos" if ag else "",
                "cadencia_dias": 1 if ag else 0,
                "por_que_esta_hora": ag.get("motivo", ""),
            },
            para_afiar=list((cfg.get("aprendizado") or {}).get("licoes", []))[:5],
            rotas=rotas,
            dominios=sorted({urlsplit(r["url"]).hostname or "" for r in rotas} - {""}),
            lexico_1=list(lex.get("termos", [])),
            veto_motor=list(lex.get("vetos", [])),
            numeros={"execucoes": len(execs), "achados": sum(e["achados"] or 0 for e in execs), "fontes": len(fontes), "fontes_com_erro": falhas},
        )
    return status, descricao, {"motores": sala}


def _achados_por_motor(sis: Sistema) -> dict[str, dict]:
    prazo = {r[0]: r[1] for r in sis.bib.execute("SELECT livro_id, inscricao_fim FROM livro_dados")}
    out: dict[str, dict] = {}
    for mid, total, unicas in sis.bib.execute("SELECT motor, COUNT(*), COUNT(DISTINCT livro_id) FROM achado GROUP BY motor"):
        ult = [
            _item(
                "achado_ultimo",
                id=r["id"],
                titulo=r["titulo"],
                site_oficial=r["link_oficial"] or "",
                livro_vinculado={"id": r["livro_id"], "ligado": bool(r["livro_id"]), "estado": "ligado ao livro" if r["livro_id"] else "sem livro"},
                decisao=r["decisao"] or "",
                url=r["link_divulgacao"] or "",
                publicado_em=r["publicado_em"],
                visto_em=r["encontrado_em"],
                prazo=prazo.get(r["livro_id"]),
                uf=(json.loads(r["dados"] or "{}") or {}).get("uf"),
            )
            for r in sis.bib.execute("SELECT * FROM achado WHERE motor = ? ORDER BY encontrado_em DESC LIMIT 5", (mid,))
        ]
        out[mid] = {"total_registros": total, "total_unicas": unicas, "ultimas": ult}
    return out


def _editais(sis: Sistema) -> tuple[list[dict], list[dict], dict, list[dict]]:
    """As oportunidades abertas (os livros com prazo aberto), o calendário e a Bússola das fontes com editais."""
    livros = sis.livros_abertos()
    ids = [r["id"] for r in livros]
    certs = sis.certidoes(ids)
    motor_de = sis.motor_do_livro()
    nomes = {m["id"]: m["nome"] for m in sis.estudo}
    editais, eventos, sem_data, por_motor = [], [], [], defaultdict(list)
    for r in livros:
        c = certs.get(r["id"], {})
        mid = motor_de.get(r["id"], "")
        editais.append(
            _item(
                "edital",
                id=r["id"],
                titulo=r["titulo"],
                url=r["link_oficial"] or r["link_divulgacao"] or "",
                fonte_id=mid,
                fonte_nome=nomes.get(mid, mid),
                territorio=r["abrangencia"] or "",
                uf=r["uf"],
                uf_exibicao=r["uf"] or "",
                abrangencia=r["abrangencia"] or "",
                nivel=r["esfera"] or "",
                status="aberto",
                area=r["area_d"] or r["tema"] or "",
                objeto=c.get("Objeto") or "",
                inicio=r["inscricao_inicio"] or "",
                fim=r["inscricao_fim"] or "",
                estado_export="aberto",
                valor_texto=c.get("Valor") or "",
                etapa=r["fase"],
                etapa_nome=FASES.get(r["fase"], r["fase"]),
                selo_validacao=r["estrela"] or "",
                validacao=r["validacao"] or "",
                situacao_inscricao="aberta",
            )
        )
        for tipo, data in (("abertura", r["inscricao_inicio"]), ("encerramento", r["inscricao_fim"]), ("resultado", r["resultado_em"])):
            if data:
                eventos.append(_item("evento", data=data, tipo=tipo, edital_id=r["id"], titulo=r["titulo"], area=r["area_d"] or r["tema"] or ""))
        if not r["resultado_em"]:
            sem_data.append({"edital_id": r["id"], "titulo": r["titulo"], "alerta": "sem data de resultado certificada"})
        analise = [{"item": i, "valor": c.get(i), "comprovado": i in c} for i in ITENS_DO_CARTORIO]
        por_motor[mid].append(
            _item(
                "bussola_edital",
                id=r["id"],
                titulo=r["titulo"],
                url=r["link_oficial"] or r["link_divulgacao"] or "",
                uf=r["uf"],
                area=r["area_d"] or r["tema"] or "",
                nivel=r["esfera"] or "",
                fim=r["inscricao_fim"],
                estado_export="aberto",
                objeto=c.get("Objeto"),
                valor_texto=c.get("Valor"),
                analise_etapa2=analise,
                comprovados=sum(a["comprovado"] for a in analise),
                total_itens=len(ITENS_DO_CARTORIO),
                anexos_pendentes=not c.get("Anexos"),
            )
        )
    fontes = [
        dict(
            _item("bussola_fonte", fonte_id=mid, fonte_nome=nomes.get(mid, mid) or "sem motor registrado", categoria=_categoria(sis, mid, "regular")),
            editais=eds,
        )
        for mid, eds in sorted(por_motor.items(), key=lambda x: -len(x[1]))
    ]
    proximos = [
        {"data": r["inscricao_fim"], "tipo": "encerramento", "edital_id": r["id"], "titulo": r["titulo"]}
        for r in livros
        if r["inscricao_fim"] and r["inscricao_fim"] <= (datetime.fromisoformat(sis.hoje) + timedelta(days=30)).date().isoformat()
    ]
    cal = {
        "marcos": [e for e in eventos if e["tipo"] == "resultado"],
        "proximos": proximos,
        "total": len(eventos),
        "sem_data": sem_data,
        "recursos_abertos": 0,
        "nota": "datas certificadas pelo Cartório; sem data, alerta (nunca estimativa)",
    }
    return editais, eventos, cal, fontes


def _bussola(sis: Sistema, molde: dict, fontes: list[dict], status: list[dict]) -> tuple[dict, dict]:
    ex = sis.execucoes()
    por_dia: dict[str, dict] = defaultdict(lambda: {"ok": 0, "falha": 0, "novas": 0, "cats": set()})
    tipo = {m["id"]: m["tipo"] for m in sis.estudo}
    for mid, lst in ex.items():
        for e in lst:
            d = por_dia[_data_br(e["inicio"])]
            d["falha" if e["erro"] else "ok"] += 1
            d["novas"] += e["achados"] or 0
            d["cats"].add(_categoria(sis, mid, tipo.get(mid, "regular")))
    dias = [
        _item(
            "bussola_dia",
            data=d,
            houve_busca=True,
            camadas=sorted(v["cats"]),
            categorias_ativas=sorted(v["cats"]),
            fontes_ok=v["ok"],
            fontes_falha=v["falha"],
            novas=v["novas"],
            encontrado=v["novas"] > 0,
            situacao="encontrado" if v["novas"] else "sem novidade",
            integridade="com_falhas" if v["falha"] else "ok",
        )
        for d, v in sorted(por_dia.items())
    ]
    construidos = [s for s in status if not s["resultado"].startswith("a construir")]
    cobertura = Counter(_categoria(sis, s["id"], tipo.get(s["id"], "regular")) for s in construidos)
    b = copy.deepcopy(molde)
    b.update(
        {
            "dias": dias,
            "categorias": {k: {"rotulo": r, "cor": c} for k, (r, c) in CATEGORIAS.items()},
            "frentes_cobertura": {k: cobertura.get(k, 0) for k in CATEGORIAS},
            "frentes_sem_cobertura": [k for k in CATEGORIAS if not cobertura.get(k)],
            "fontes_com_editais": fontes,
            "regra": "cada dia mostra as execuções dos motores registradas no Cérebro; as fontes com editais são os livros com prazo aberto",
        }
    )
    abertos = [e for f in fontes for e in f["editais"]]
    urgentes = [e for e in abertos if e["fim"] and e["fim"] <= (datetime.fromisoformat(sis.hoje) + timedelta(days=7)).date().isoformat()]
    nomes = {f["fonte_id"]: f["fonte_nome"] for f in fontes}
    farol = sis.bib.execute("SELECT COUNT(*) FROM passaporte WHERE fase = 'farol'").fetchone()[0]
    dominios = {
        urlsplit(u).hostname
        for c in sis.configs.values()
        for u in [f.get("url", "") for f in c.get("fonte", [])] + [e for a in c.get("alvo", []) for e in a.get("enderecos", [])]
    } - {None, ""}
    painel = {
        "novas_ultima": dias[-1]["novas"] if dias else 0,
        "fontes_ativas": len(construidos),
        "sites": len(dominios),
        "verificados": farol,
        "verificados_semana": 0,
        "urgentes_7d": len(urgentes),
        "casos_farol": farol,
        "casos_nota": "",
        "atualizacoes": [
            _item(
                "atualizacao",
                data=e["fim"],
                tipo="prazo",
                titulo="Prazo se aproximando",
                sub=f"{next((nomes[f['fonte_id']] for f in fontes if e in f['editais']), '')} · encerra {e['fim'][8:10]}/{e['fim'][5:7]}",
                id=e["id"],
            )
            for e in sorted(urgentes, key=lambda x: x["fim"])
        ],
    }
    return b, painel


def _fluxo(sis: Sistema, agora: str) -> dict:
    """O mapa das oportunidades (fluxo_oportunidades.json), do banco: abertas são os livros com prazo aberto; confirmadas, as
    abertas com a origem confirmada e com o objeto e o prazo certificados; a validação aplicada é a do Cartório."""
    f = _molde("fluxo_oportunidades.json")
    livros = sis.livros_abertos()
    ids = [r["id"] for r in livros]
    certs = sis.certidoes(ids)
    listas = sis.checklist(ids)
    motor_de = sis.motor_do_livro()
    validados = sis.bib.execute("SELECT COUNT(*) FROM livro_dados").fetchone()[0]
    total = sis.bib.execute("SELECT COUNT(*) FROM livro WHERE situacao <> 'excluido'").fetchone()[0]
    itens, confirmadas, possiveis, por_uf, cal = [], [], [], defaultdict(lambda: {"confirmadas": 0, "possiveis": 0}), []
    origem_ct, tipo_ct, val_ct = Counter(), Counter(), Counter()
    for r in livros:
        c = certs.get(r["id"], {})
        conf = (r["estrela"] or "sem") in ("prata", "ouro")            # a régua da titular: o prazo e o link original
        mid = motor_de.get(r["id"], "")
        origem = "Piloto - Espião" if mid == "espiao" else "Piloto - Interceptador" if mid == "interceptador" else "motor"
        tipo = "empresa/instituto" if (r["esfera"] or "").lower().startswith("priv") else "ente público"
        origem_ct[origem] += 1
        tipo_ct[tipo] += 1
        val_ct[r["validacao"] or "pendente"] += 1
        uf = r["uf"] if r["uf"] and r["uf"] != "BR" and (r["abrangencia"] or "") not in ("nacional", "internacional") else "__nac__"
        por_uf[uf]["confirmadas" if conf else "possiveis"] += 1
        item = _item(
            "fluxo_item",
            id=r["id"],
            titulo=r["titulo"],
            orgao=r["orgao"],
            uf=r["uf"],
            inicio=r["inscricao_inicio"],
            fim=r["inscricao_fim"],
            link_oficial=r["link_oficial"] or "",
            origem=(f"motor {mid}" if mid else "livro migrado (sem motor registrado)") if origem == "motor" else origem,
            tipo=tipo,
            objeto=c.get("Objeto"),
            confirmada=conf,
            url=r["link_oficial"] or r["link_divulgacao"] or "",
            area=r["area_d"] or r["tema"] or "",
            livro_vinculado={"id": r["id"], "ligado": True},
            validacao=r["validacao"] or "",
            estado="aberta",
            selo_livro=r["selo_livro"] or "",
            selo=r["estrela"] or "",
            site_oficial_conhecido=r["origem"] == "confirmado",
            checklist=listas.get(r["id"]) or _item("fluxo_item")["checklist"],
            etapa=r["fase"] or "",
            escada=r["escada"] or "",
        )
        itens.append((uf, item))
        (confirmadas if conf else possiveis).append(item)
        cal.append(item)
    estrela = Counter(r["estrela"] or "sem" for r in livros)
    f["validacao"].update(
        {"aplicada": True, "decisoes": validados, "arquivos": ["biblioteca.db (livro_dados: a validação do Cartório)"], "sem_decisao": total - validados}
    )
    f["parametro"].update(
        {
            "regra": "oportunidade aberta = livro com prazo de inscrição aberto, validado pelo Cartório",
            "abertas": len(livros),
            "validadas": val_ct.get("aprovado", 0),
            "em_verificacao": sum(1 for r in livros if r["fase"] == "analise externa"),
            "em": agora[:10],
            "estantes": {"ouro": estrela.get("ouro", 0), "prata": estrela.get("prata", 0), "bronze": estrela.get("bronze", 0), "sem_livro": 0},
            "fonte": "biblioteca.db",
        }
    )
    f["etapas"].update(
        {
            "possiveis_abertas": len(livros),
            "confirmadas_com_minimo": len(confirmadas),
            "por_origem": {
                "motor": origem_ct.get("motor", 0),
                "Piloto - Espião": origem_ct.get("Piloto - Espião", 0),
                "Piloto - Interceptador": origem_ct.get("Piloto - Interceptador", 0),
            },
            "por_tipo": {
                "ente público": tipo_ct.get("ente público", 0),
                "empresa/instituto": tipo_ct.get("empresa/instituto", 0),
                "menção em diário oficial": 0,
            },
            "por_validacao": {"valida_aberta": val_ct.get("aprovado", 0), "valida_fora_abrangencia": 0, "pendente": len(livros) - val_ct.get("aprovado", 0)},
        }
    )
    por_mes = defaultdict(lambda: {"criados": 0, "com_resultado": 0})
    for (mes,) in sis.bib.execute("SELECT substr(criado_em, 1, 7) FROM livro WHERE situacao <> 'excluido'"):
        por_mes[mes]["criados"] += 1
    ligados = sis.bib.execute("SELECT COUNT(DISTINCT livro_id) FROM achado WHERE livro_id IS NOT NULL").fetchone()[0]
    agrupados = defaultdict(list)
    for uf, it in itens:
        agrupados[uf].append(it)
    f.update(
        {
            "em": agora,
            "regra": "o mapa das oportunidades abertas, da Biblioteca do sistema novo",
            "selos": {"ouro": estrela.get("ouro", 0), "prata": estrela.get("prata", 0), "bronze": estrela.get("bronze", 0)},
            "mapa": {"total": {"confirmadas": len(confirmadas), "possiveis": len(possiveis)}, "por_uf": dict(por_uf)},
            "calendario": sorted(cal, key=lambda x: x["fim"] or "9999"),
            "confirmadas": confirmadas,
            "possiveis_sem_minimo": possiveis,
            "itens_por_uf": dict(agrupados),
        }
    )
    com_edicoes = sis.bib.execute("SELECT COUNT(*) FROM livro WHERE situacao <> 'excluido' AND selo_livro IN ('bronze', 'prata', 'ouro')").fetchone()[0]
    f["livros_do_sistema"].update(
        {"por_mes": dict(por_mes), "catalogo": total, "ligados": ligados, "monitorados_abertos": len(livros), "com_historico_de_edicoes": com_edicoes}
    )
    return f


def _tabelas(sis: Sistema, status: list[dict], descricao: dict, agora: str) -> dict[str, dict]:
    """As tabelas compactas (campos + linhas): os motores (uma linha por motor do estudo), as abertas (uma por livro com prazo
    aberto) e as empresas (a base Especial)."""
    itens = _molde("itens.json")
    luz = {s["id"]: s for s in status}
    linhas_m = []
    for m in sis.estudo:
        cfg = sis.configs.get(m["id"], {})
        mot = cfg.get("motor") or {}
        d = descricao.get(m["id"], {})
        rotas = d.get("rotas") or []
        st = luz.get(m["id"], {})
        valores = {
            "id": m["id"],
            "nome_classificado": m["nome"],
            "programa": m["nome"],
            "objeto_area": m["categoria_nome"].split(" — ")[0].split(" (")[0],
            "geo": "GO" if mot.get("uf") == "GO" else "BR",
            "ativa": not st.get("resultado", "").startswith("a construir"),
            "achados": (d.get("numeros") or {}).get("achados", 0),
            "orgao": mot.get("orgao") or m["categoria_nome"],
            "pagina": rotas[0]["url"] if rotas else None,
            "tipo": m["categoria"],
            "familia": m["categoria_nome"],
            "uf": mot.get("uf"),
            "goias": mot.get("uf") == "GO",
            "ultima_leitura": st.get("ultima_leitura") or None,
            "motivo_status": st.get("resultado"),
            "validacao": m["situacao"],
            "papel": m["tipo"],
        }
        linhas_m.append([valores.get(c) for c in itens["campos_motores"]])
    mo = _molde("motores.json")
    mo.update({"campos": itens["campos_motores"], "dic": {}, "linhas": linhas_m})
    mo["resumo"] = {
        **(mo.get("resumo") or {}),
        "gerado_em": agora,
        "total": len(linhas_m),
        "dia_de_referencia": sis.hoje,
        "por_familia": dict(Counter(m["categoria_nome"] for m in sis.estudo)),
    }
    livros = sis.livros_abertos()
    certs = sis.certidoes([r["id"] for r in livros])
    motor_de = sis.motor_do_livro()
    nomes = {m["id"]: m["nome"] for m in sis.estudo}
    linhas_a = []
    for r in livros:
        c = certs.get(r["id"], {})
        fim = r["inscricao_fim"]
        valores = {
            "id": r["id"],
            "titulo": r["titulo"],
            "url": r["link_oficial"] or r["link_divulgacao"],
            "fonte_nome": nomes.get(motor_de.get(r["id"], ""), motor_de.get(r["id"])),
            "orgao": r["orgao"],
            "uf": r["uf"],
            "nivel": r["esfera"],
            "area": r["area_d"] or r["tema"],
            "fim": fim,
            "prazo_texto": f"até {fim[8:10]}/{fim[5:7]}/{fim[:4]}" if fim else None,
            "valor_texto": c.get("Valor"),
            "coletado_em": r["criado_em"],
            "situacao": "aberta",
            "objeto": c.get("Objeto"),
            "selo_validacao": r["estrela"],
            "validacao": r["validacao"],
        }
        linhas_a.append([valores.get(cc) for cc in itens["campos_abertas"]])
    ab = _molde("abertas.json")
    ab.update({"campos": itens["campos_abertas"], "dic": {}, "linhas": linhas_a, "total": len(linhas_a)})
    ab["contabilidade"] = {**(ab.get("contabilidade") or {}), "publicadas": len(linhas_a)}
    em = _molde("empresas.json")
    em["gerado_em"] = agora
    if sis.esp is not None:
        inc = defaultdict(list)
        for r in sis.esp.execute("SELECT cnpj, lei, ano, valor, fonte FROM incentivo"):
            inc[r["cnpj"]].append({"lei": r["lei"], "ano": r["ano"], "valor": r["valor"], "fonte": r["fonte"]})
        por_uf: dict[str, list] = defaultdict(list)                  # todas as empresas da Biblioteca, cada uma na aba do seu estado
        for r in sis.esp.execute("SELECT * FROM empresa ORDER BY razao_social"):
            por_uf["GO" if r["uf"] in ("GO", "BR", None, "") else r["uf"]].append(_item(
                "empresa",
                id=r["cnpj"],
                nome=r["razao_social"],
                nome_fantasia=r["nome_fantasia"],
                cnpj=r["cnpj"],
                municipio=r["municipio_ibge"],
                cnae=r["atividade_principal"],
                porte=r["porte"],
                elegivel=bool(inc.get(r["cnpj"])),
                destinacoes=inc.get(r["cnpj"], []),
                fontes=sorted({i["fonte"] for i in inc.get(r["cnpj"], []) if i["fonte"]}),
            ))
        for uf, empresas in por_uf.items():
            aba = em["estados"].get(uf) or {"nome": uf}
            aba.update({"ativo": True, "gerado_em": agora, "total": len(empresas), "com_cadastro": len(empresas),
                        "elegiveis": sum(1 for e in empresas if e["elegivel"]), "empresas": empresas})
            if uf == "GO":
                aba["nome"] = "Goiás"
            em["estados"][uf] = aba
    return {"motores.json": mo, "abertas.json": ab, "empresas.json": em}


def gerar(saida: Path, raiz: Path = Path(".")) -> dict[str, int]:
    sis = Sistema(raiz)
    agora = _agora().isoformat(timespec="seconds")
    D = _molde("dashboard-dados.json")
    status, descricao, sala = _motores(sis)
    editais, eventos, cal, fontes = _editais(sis)
    bussola, bussola_painel = _bussola(sis, D["bussola"], fontes, status)
    D.update({"gerado_em": agora, "editais": editais, "eventos": eventos, "calendario_decisao": cal, "bussola": bussola, "bussola_painel": bussola_painel})
    total = sis.bib.execute("SELECT COUNT(*) FROM livro WHERE situacao <> 'excluido'").fetchone()[0]
    leis = sis.bib.execute("SELECT COUNT(*) FROM lei").fetchone()[0]
    D["biblioteca"].update(
        {"biblioteca": "Biblioteca do Eldorado (biblioteca.db)", "atualizado_em": agora, "acervos": {"leis": leis, "oportunidades": total, "associacoes": 0}}
    )
    fases = dict(sis.bib.execute("SELECT fase, COUNT(*) FROM passaporte GROUP BY fase").fetchall())
    D["fila_verificacao"].update({"gerado_em": agora, "total": fases.get("analise externa", 0)})
    D["farol_resumo"]["decisoes"].update({"elegiveis": fases.get("farol", 0)})
    arquivos: dict[str, Any] = {}
    sm = _molde("status_motores.json")
    cont = Counter(s["luz"] for s in status)
    sm.update(
        {
            "gerado_em": agora,
            "regra": "os 47 motores do estudo, com o que o sistema registra: verde leu hoje sem erro; vermelho falhou; cinza não leu hoje ou a construir",
            "contagem": {
                "verde": cont.get("verde", 0),
                "vermelho": cont.get("vermelho", 0),
                "cinza": cont.get("cinza", 0),
                "legenda": {
                    "verde": "leu hoje, sem erro",
                    "vermelho": "a última execução falhou (ou todas as fontes com erro)",
                    "cinza": "não leu hoje, ou a construir",
                },
            },
            "motores": status,
        }
    )
    arquivos["status_motores.json"] = sm
    dm = _molde("descricao_motores.json")
    dm.update({"em": agora, "regra": "a descrição de cada motor, das configurações do sistema novo", "motores": descricao})
    arquivos["descricao_motores.json"] = dm
    am = _molde("achados_motores.json")
    am.update({"em": agora, "regra": "os achados registrados na Biblioteca, por motor", "motores": _achados_por_motor(sis)})
    arquivos["achados_motores.json"] = am
    sc = _molde("sala_controle.json")
    sc.update({"em": agora, "regra": "o estado dos motores registrado pelo sistema"})
    sc["detalhes"].update(sala)
    arquivos["sala_controle.json"] = sc
    ca = _molde("cartorio.json")
    pontos = sis.bib.execute("SELECT COUNT(DISTINCT livro_id || '|' || item) FROM certidao WHERE situacao = 'comprovado'").fetchone()[0]
    confirmados = sis.bib.execute("SELECT COUNT(*) FROM livro_dados WHERE origem = 'confirmado'").fetchone()[0]
    ca.update({"em": agora, "regra": "as certidões da Biblioteca"})
    ca["resumo"].update(
        {
            "pontos_12_total": total * 12,
            "pontos_certificados": pontos,
            "pontos_faltam": max(total * 12 - pontos, 0),
            "pct_certificado_12": round(100 * pontos / (total * 12), 1) if total else 0,
            "fila_livros": fases.get("preparacao", 0),
            "com_link_oficial": confirmados,
        }
    )
    arquivos["cartorio.json"] = ca
    arquivos["fluxo_oportunidades.json"] = _fluxo(sis, agora)
    arquivos.update(_tabelas(sis, status, descricao, agora))
    for p in MOLDE.glob("*.json"):  # os demais arquivos: a estrutura, vazia (sem dado do Eldorado0)
        if p.name not in arquivos and p.name not in ("dashboard-dados.json", "itens.json"):
            arquivos[p.name] = _molde(p.name)
    if saida.exists():
        shutil.rmtree(saida)
    shutil.copytree(PAGINA, saida)
    (saida / "dados").mkdir(exist_ok=True)
    for nome, v in arquivos.items():
        (saida / "dados" / nome).write_text(json.dumps(v, ensure_ascii=False), encoding="utf-8")
    texto = json.dumps(D, ensure_ascii=False)
    (saida / "dashboard-dados.json").write_text(texto, encoding="utf-8")
    (saida / "dashboard-dados.js").write_text(f"window.DADOS={texto};", encoding="utf-8")
    return {
        "motores": len(status),
        "verde": cont.get("verde", 0),
        "vermelho": cont.get("vermelho", 0),
        "cinza": cont.get("cinza", 0),
        "oportunidades_abertas": len(editais),
        "eventos": len(eventos),
        "livros": total,
        "arquivos": len(arquivos),
    }
