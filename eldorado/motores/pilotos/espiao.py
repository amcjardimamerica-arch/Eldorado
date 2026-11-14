"""O PILOTO ESPIÃO (do Eldorado0, titular, 09 e 16/10/2026): caça só o que nenhum motor alcança.

Avaliação que motivou o foco (Eldorado0, 08 e 09/10): 792 missões, 2 com resultado; as buscas eram de editais
públicos, território dos motores. Por isso o Espião busca só:
  editais e chamadas de institutos, fundações e empresas privadas; patrocínio, doação, investimento social,
  voluntariado, matching e cessão (mesmo sem edital); e o internacional (fundos, embaixadas, cooperação), em várias línguas.
Descarta: domínio de governo (é dos motores), buscadores, agregadores, redes sociais, o que um motor já vigia e o que
já está na Biblioteca. Fica só a página com sinal de oportunidade E sinal de OSC.

A família de busca é escolhida por amostragem de Thompson (aprende sozinha qual rende); consulta usada 3 vezes sem
resultado é aposentada. O achado vai à Pertinência e entra no Cartório pela recepção (etapa 1). Estado próprio em
o Cérebro (cerebro.db, tabelas espiao_*; só o Espião escreve nelas); o descanso das rotas de busca vale entre as execuções.
"""

from __future__ import annotations

import json
import random
import re
import sqlite3
import tomllib
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

from ...base.nucleo.contratos import Achado

SETORES = [
    "mineradora",
    "agronegócio",
    "cooperativa agroindustrial",
    "energia elétrica",
    "saneamento",
    "rede de supermercados",
    "atacarejo",
    "banco",
    "cooperativa de crédito",
    "operadora de telefonia",
    "indústria farmacêutica",
    "frigorífico",
    "construtora",
    "empresa de tecnologia",
    "seguradora",
    "montadora",
    "indústria de alimentos",
    "indústria de bebidas",
    "shopping center",
    "rede de farmácias",
    "transportadora",
    "usina de etanol",
    "indústria de fertilizantes",
    "hospital privado",
]
APOIOS = [
    "edital de patrocínio",
    "chamada de projetos sociais",
    "programa de investimento social",
    "seleção de projetos",
    "fundo de doação para ONGs",
    "doação de equipamentos para entidades",
    "voluntariado corporativo",
    "doação casada (matching)",
    "prêmio de iniciativas sociais",
    "patrocínio a projetos culturais",
    "patrocínio a projetos esportivos",
    "apoio a projetos comunitários",
    "doação de alimentos para instituições",
    "edital do instituto",
    "chamada pública de parceiros sociais",
]
PUBLICOS = [
    "crianças e adolescentes",
    "pessoa idosa",
    "mulheres",
    "juventude",
    "pessoas com deficiência",
    "comunidades periféricas",
    "catadores de recicláveis",
    "agricultura familiar",
    "cultura popular",
    "esporte de base",
    "educação",
    "meio ambiente",
    "segurança alimentar",
    "população em situação de rua",
]
REGIOES = ["Goiás", "Goiânia", "Anápolis", "Aparecida de Goiânia", "Rio Verde", "Goiás", "todo o Brasil", "nacional"]
INTERNACIONAIS = [
    "Fundo Canadá para Iniciativas Locais",
    "Embaixada da Alemanha microprojetos",
    "Embaixada do Japão Assistência a Projetos Comunitários",
    "Embaixada da França fundo de apoio",
    "Embaixada dos Países Baixos",
    "União Europeia sociedade civil Brasil",
    "Fundação Interamericana IAF",
    "GEF Small Grants Programme Brasil",
    "Global Fund for Children",
    "Fundação Avina",
    "Open Society Foundations",
    "Ford Foundation Brasil",
    "W.K. Kellogg Foundation",
    "Porticus",
    "Laudes Foundation",
    "Oak Foundation",
    "ONU Mulheres fundo",
    "UNESCO Fundo Internacional para a Diversidade Cultural",
    "Ibercultura Viva",
]
OPERADORES = ['"regulamento" "inscrições"', 'filetype:pdf "edital"', "intitle:edital", '"inscrições abertas"', '"chamada de projetos"']
LINGUAS = {
    "internacional_ingles": [
        "call for proposals Brazil civil society {ano}",
        "grants for NGOs in Brazil {ano}",
        "small grants Brazil community organizations {ano}",
        "funding opportunity nonprofits Latin America {ano} Brazil eligible",
        "request for proposals Brazil social projects {ano}",
    ],
    "internacional_espanhol": [
        "convocatoria organizaciones de la sociedad civil Brasil {ano}",
        "fondos para ONG América Latina Brasil {ano}",
        "convocatoria proyectos comunitarios Brasil elegible {ano}",
    ],
    "internacional_frances": [
        "appel à projets ONG Brésil {ano}",
        "subventions associations Brésil {ano}",
        "fonds pour la société civile Amérique latine Brésil {ano}",
    ],
    "internacional_alemao": [
        "Förderung Zivilgesellschaft Brasilien {ano}",
        "Ausschreibung NGO Brasilien Projekte {ano}",
        "Kleinprojekte Botschaft Brasilien {ano}",
    ],
    "internacional_italiano": ["bando ONG Brasile {ano}", "finanziamenti società civile Brasile {ano}"],
}
OPORT = re.compile(
    r"(?i)edital|regulamento|inscri[çc][õo]es|chamada|call for proposals|apply now|grant|convocatoria|patroc[ií]nio|doa[çc][ãa]o|"
    r"sele[çc][ãa]o de projetos|programa de apoio|investimento social|fondos?|appel à projets|ausschreibung|bando"
)
OSC = re.compile(
    r"(?i)\bosc\b|\bongs?\b|organiza[çc][õo]es? (da sociedade civil|sociais|sem fins)|associa[çc][õo]es|sociedade civil|nonprofit|non-profit|"
    r"\bngos?\b|sin fines de lucro|terceiro setor|projetos sociais|entidades|associations|zivilgesellschaft"
)
GOVERNO = re.compile(r"(?i)(\.gov\.br|\.leg\.br|\.jus\.br|\.mp\.br|\.def\.br|\.mil\.br|\.gov)$")
FORA = re.compile(
    r"(?i)(^|\.)(duckduckgo\.com|bing\.com|google\.[a-z.]+|wikipedia\.org|youtube\.com|facebook\.com|instagram\.com|linkedin\.com|"
    r"twitter\.com|x\.com|tiktok\.com|prosas\.com\.br|editaiscult\w*\.com\.br|catarse\.me|vakinha\.com\.br|"
    r"[\w-]+\.blogspot\.com(\.br)?|[\w-]+\.wordpress\.com|medium\.com|[\w-]+\.substack\.com|jusbrasil\.com\.br)$"
)
# (o blog e a plataforma de publicação divulgam editais de terceiros: não são a fonte; teste real de 22/10/2026)
DDL = """
CREATE TABLE IF NOT EXISTS espiao_familia (nome TEXT PRIMARY KEY, a REAL NOT NULL DEFAULT 1, b REAL NOT NULL DEFAULT 1, usos INTEGER NOT NULL DEFAULT 0,
  achados INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS espiao_consulta (texto TEXT PRIMARY KEY, familia TEXT, usos INTEGER NOT NULL DEFAULT 0,
    achados INTEGER NOT NULL DEFAULT 0, ultima TEXT);
CREATE TABLE IF NOT EXISTS espiao_missao (id INTEGER PRIMARY KEY, em TEXT NOT NULL, familia TEXT, consulta TEXT, resultados INTEGER, candidatos INTEGER,
  achados INTEGER, motivos TEXT, rotas TEXT, bloqueada INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS espiao_rota (nome TEXT PRIMARY KEY, descansa_ate TEXT);
"""


def familias(empresas: list[str]) -> dict[str, Callable[[random.Random, int], str | None]]:
    regiao = lambda r: r.choice(REGIOES)  # noqa: E731
    f: dict[str, Callable[[random.Random, int], str | None]] = {
        "setor_apoio_regiao": lambda r, a: f"{r.choice(SETORES)} {r.choice(APOIOS)} {regiao(r)} {a}",
        "publico_apoio_empresa": lambda r, a: f"empresa {r.choice(APOIOS)} {r.choice(PUBLICOS)} {regiao(r)} {a}",
        "operador_avancado": lambda r, a: (
            f"{r.choice(OPERADORES)} {r.choice(['instituto', 'fundação empresarial', 'empresa'])} {r.choice(PUBLICOS)} {regiao(r)} {a}"
        ),
        "rastro_de_patrocinio": lambda r, a: f'"patrocínio" "{r.choice(PUBLICOS)}" projeto {regiao(r)} "apoio" {a}',
        "nao_financeiro": lambda r, a: (
            f"{r.choice(['doação de computadores', 'doação de alimentos', 'cessão de espaço', 'voluntariado de funcionários', 'doação de móveis'])} "
            f"para ONGs empresa {regiao(r)} {a}"
        ),
        "internacional_financiador": lambda r, a: (
            f'"{r.choice(INTERNACIONAIS)}" {r.choice(["edital", "chamada", "call for proposals", "inscrições"])} {a}'
        ),
        "associacoes_goias_eventos": lambda r, a: (
            f"{r.choice(['festival', 'corrida beneficente', 'evento beneficente', 'projeto social'])} "
            f"{r.choice(['Goiânia', 'Goiás', 'Anápolis'])} patrocinadores {a}"
        ),
    }
    for nome, consultas in LINGUAS.items():
        f[nome] = lambda r, a, c=consultas: r.choice(c).format(ano=a)
    if empresas:
        f["empresa_semente"] = lambda r, a: (
            f'"{r.choice(empresas)}" {r.choice(["instituto", "fundação", "patrocínio", "edital"])} projetos sociais {a}'
        )
    return f


from ...base.comandante.cartorio import peso_espiao  # noqa: E402


def _fator_real(con, familia: str) -> float:
    """06/11/2026: o fator real da família pelo último ciclo dos pilotos (1 sem ciclo)."""
    try:
        from ...base.cerebro.ciclo_pilotos import fator_familia
        return fator_familia(con, familia)
    except Exception:  # noqa: BLE001 — sem o Cérebro do ciclo, o sorteio segue como antes
        return 1.0


# 14/11/2026 (R55, C19): o título de uma listagem (o mesmo critério do portão de entrada)
LISTAGEM = re.compile(r"(?i)^\s*(?:convocat[óo]rias|editais|oportunidades|chamadas|programas|portal de (?:projetos|editais|oportunidades))\b")

class Espiao:
    def __init__(
        self,
        estado: str | Path,
        consultar: Callable[[str], tuple[list, list[str]]],
        ler: Callable[[str], tuple[str, str] | None],
        vigiados: set[str] | None = None,
        conhecidos: set[str] | None = None,
        empresas: list[str] | None = None,
        rnd: random.Random | None = None,
        descanso_h: float = 2.0,
        diario=None,
        abrir_listagem: Callable[[str], list[str]] | None = None,
    ):
        from ...banco.cerebro_db.esquema import abrir  # dentro do Cérebro (as tabelas espiao_* são da versão 2)
        self.con = abrir(estado)
        self.con.row_factory = None
        self.con.isolation_level = ""                         # as transações explícitas do Espião (commit) seguem valendo
        self.consultar, self.ler = consultar, ler
        self.vigiados, self.conhecidos = vigiados or set(), conhecidos or set()
        self.fams = familias(empresas or [])
        self.rnd = rnd or random.Random()
        self.descanso_h = descanso_h
        self.abrir_listagem = abrir_listagem   # R55 (C19): os editais de uma listagem (os links dos documentos e das plataformas)
        # o aprendizado do Espião vai ao Cérebro PELOS EVENTOS (24/10/2026: ele gravava direto no arquivo, e a sala, que lê o
        # repositório e os eventos, nunca via as missões: o alarme "Missões do Espião em 24 h" ficava aceso); sem diário
        # (os testes), grava direto
        self.diario = diario
        # 14/11/2026 (R55, C6): a memória das entregas — o achado do Espião tem identificador fixo por endereço («espiao-» +
        # o resumo do link); o endereço que a Pertinência barrou nos últimos 30 dias não volta (10.740 entregas de 660 páginas)
        try:
            desde = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            self.barrados = {r for (r,) in self.con.execute(
                "SELECT referencia FROM decisao_pertinencia WHERE referencia LIKE 'espiao-%' AND em >= ? "
                "AND lower(decisao) NOT IN ('aceito', 'aceita', 'aceitar', 'pertinente', 'manter')", (desde,))}
        except sqlite3.Error:
            self.barrados = set()
        existentes = {r[0] for r in self.con.execute("SELECT nome FROM espiao_familia")}
        for f in self.fams:
            if f not in existentes:
                self._gravar("espiao.familia", {"nome": f, "a": 1.0, "b": 1.0, "usos": 0, "achados": 0},
                             "INSERT OR IGNORE INTO espiao_familia(nome) VALUES (?)", (f,))
        self.con.commit()

    def _gravar(self, tipo: str, dados: dict, sql: str, args: tuple) -> None:
        if self.diario is not None:
            self.diario.emitir(tipo, "espiao", dados)
        else:
            self.con.execute(sql, args)

    # ------------------------------------------------------------------ a escolha (Thompson) e o bloqueio
    def bloqueado(self) -> bool:
        """Todas as rotas de busca GERAL descansando (R55, C5): não há missão de busca possível agora."""
        from ..descoberta.metabusca import ROTAS_GERAIS
        agora_ = datetime.now(timezone.utc).isoformat()
        rotas = dict(self.con.execute("SELECT nome, descansa_ate FROM espiao_rota"))
        return not any((rotas.get(r) or "") <= agora_ for r in ROTAS_GERAIS)

    def escolher(self) -> tuple[str, str]:
        if getattr(self, "preferida", None) in self.fams:                        # a família escolhida pelo Comandante (25/10/2026)
            ano, ruins = date.today().year, {q for (q,) in self.con.execute("SELECT texto FROM espiao_consulta WHERE usos >= 3 AND achados = 0")}
            for _ in range(6):
                q = self.fams[self.preferida](self.rnd, ano)
                if q and q not in ruins:
                    return self.preferida, re.sub(r"\s+", " ", q).strip()
        ruins = {q for (q,) in self.con.execute("SELECT texto FROM espiao_consulta WHERE usos >= 3 AND achados = 0")}
        sorteio = sorted(
            (
                (self.rnd.betavariate(max(0.1, a), max(0.1, b)) * peso_espiao(f) * _fator_real(self.con, f), f)   # 06/11: o fator real
                for f, a, b in self.con.execute("SELECT nome, a, b FROM espiao_familia")
                if f in self.fams
            ),
            reverse=True,
        )
        ano = date.today().year
        for _p, f in sorteio:
            for _ in range(6):
                q = self.fams[f](self.rnd, ano)
                if q and q not in ruins:
                    return f, re.sub(r"\s+", " ", q).strip()
        return "setor_apoio_regiao", self.fams["setor_apoio_regiao"](self.rnd, ano) or ""

    def fora_dos_motores(self, url: str) -> tuple[bool, str]:
        h = (urlsplit(url).hostname or "").lower().removeprefix("www.")
        if not h or not url.startswith("http"):
            return False, "sem endereço"
        if GOVERNO.search(h):
            return False, "domínio de governo (território dos motores)"
        if FORA.search(h):
            return False, "buscador, agregador ou rede social"
        if h in self.vigiados:
            return False, "já vigiado por um motor"
        if url.rstrip("/") in self.conhecidos:
            return False, "já está na Biblioteca"
        return True, ""

    # ------------------------------------------------------------------ uma missão
    def missao(self) -> dict[str, Any]:
        fam, q = self.escolher()
        pistas, relato = self.consultar(q)
        for linha in relato:  # o descanso das rotas vale entre as execuções
            # 14/11/2026 (R55, C1): só a linha «falhou» grava o descanso, com os minutos que a metabusca calculou (2 a 60; o
            # SearXNG, 1) — a linha «descansando» regravava 2 h a cada missão e a rota nunca voltava (79.054 eventos)
            m_falha = re.match(r"([^:]+): falhou .*?descansa (\d+) min", linha)
            if m_falha:
                ate = (datetime.now(timezone.utc) + timedelta(minutes=max(1, int(m_falha.group(2))))).isoformat()
                self._gravar("espiao.rota", {"nome": m_falha.group(1), "descansa_ate": ate}, "INSERT OR REPLACE INTO espiao_rota VALUES (?, ?)",
                             (m_falha.group(1), ate))
        motivos: dict[str, int] = {}
        achados: list[Achado] = []
        candidatos = 0
        for p in pistas[:8]:
            ok, porque = self.fora_dos_motores(p.link)
            if not ok:
                motivos[porque] = motivos.get(porque, 0) + 1
                continue
            if f"espiao-{__import__('hashlib').sha1(p.link.encode()).hexdigest()[:12]}" in self.barrados:   # C6
                motivos["barrada pela Pertinência nos últimos 30 dias"] = motivos.get("barrada pela Pertinência nos últimos 30 dias", 0) + 1
                continue
            lido = self.ler(p.link)
            if not lido:
                motivos["página não lida"] = motivos.get("página não lida", 0) + 1
                continue
            titulo, texto = lido
            # 14/11/2026 (R55, C19): a listagem é aberta — cada edital entra separado (a Pertinência barrava 7.958 listagens)
            if self.abrir_listagem and LISTAGEM.search(titulo or p.titulo or ""):
                try:
                    filhos = [u for u in self.abrir_listagem(p.link) if u.rstrip("/") != p.link.rstrip("/")][:5]
                except Exception:  # noqa: BLE001 — a listagem que não abre segue como página comum (registrado)
                    filhos = []
                motivos["listagem aberta"] = motivos.get("listagem aberta", 0) + 1
                for u in filhos:
                    ok2, porque2 = self.fora_dos_motores(u)
                    aid = f"espiao-{__import__('hashlib').sha1(u.encode()).hexdigest()[:12]}"
                    if not ok2 or aid in self.barrados:
                        chave = porque2 or "barrada pela Pertinência nos últimos 30 dias"
                        motivos[chave] = motivos.get(chave, 0) + 1
                        continue
                    lido2 = self.ler(u)
                    if not lido2 or not (OPORT.search(f"{lido2[0]} {lido2[1][:6000]}") and OSC.search(f"{lido2[0]} {lido2[1][:6000]}")):
                        continue
                    candidatos += 1
                    h2 = urlsplit(u).hostname or ""
                    achados.append(Achado(id=aid, motor="espiao", encontrado_em=date.today().isoformat(), link_divulgacao=p.link, link_oficial=u,
                                          titulo=(lido2[0] or h2)[:200], dados={"familia": fam, "consulta": q, "dominio": h2,
                                                                                "origem": "missão do piloto Espião (edital de uma listagem)"},
                                          documento={"url": u, "sha256": __import__("hashlib").sha256(lido2[1].encode()).hexdigest(), "tipo": "html",
                                                     "leitor": "espiao", "oficial": True, "paginas": [lido2[1]]}))
                    self.conhecidos.add(u.rstrip("/"))
                continue
            base = f"{p.titulo} {titulo} {texto[:6000]}"
            if not (OPORT.search(base) and OSC.search(base)):
                motivos["sem sinal de oportunidade para OSC"] = motivos.get("sem sinal de oportunidade para OSC", 0) + 1
                continue
            candidatos += 1
            h = urlsplit(p.link).hostname or ""
            achados.append(
                Achado(
                    id=f"espiao-{__import__('hashlib').sha1(p.link.encode()).hexdigest()[:12]}",
                    motor="espiao",
                    encontrado_em=date.today().isoformat(),
                    link_divulgacao=p.link,
                    link_oficial=p.link,
                    titulo=(titulo or p.titulo or h)[:200],
                    dados={"familia": fam, "consulta": q, "dominio": h, "origem": "missão do piloto Espião"},
                    documento={
                        "url": p.link,
                        "sha256": __import__("hashlib").sha256(texto.encode()).hexdigest(),
                        "tipo": "html",
                        "leitor": "espiao",
                        "oficial": True,
                        "paginas": [texto],
                    },
                )
            )
            self.conhecidos.add(p.link.rstrip("/"))
        bloqueada = not pistas and all(("descans" in r or "falhou" in r or "deslig" in r.lower()) for r in relato)
        em = datetime.now(timezone.utc).isoformat()
        linha_m = {"em": em, "familia": fam, "consulta": q, "resultados": len(pistas), "candidatos": candidatos, "achados": len(achados),
                   "motivos": json.dumps(motivos, ensure_ascii=False), "rotas": json.dumps(relato, ensure_ascii=False), "bloqueada": int(bloqueada)}
        self._gravar("espiao.missao", linha_m, "INSERT INTO espiao_missao(em, familia, consulta, resultados, candidatos, achados, motivos, rotas, "
                     "bloqueada) VALUES (?,?,?,?,?,?,?,?,?)", tuple(linha_m.values()))
        if not bloqueada:  # aprende: reforça a família que rendeu (os valores completos: nenhum incremento se perde)
            f0 = self.con.execute("SELECT a, b, usos, achados FROM espiao_familia WHERE nome = ?", (fam,)).fetchone() or (1.0, 1.0, 0, 0)
            # R48 (titular, 08/11/2026): a crença da família é simétrica (+1 no acerto, +1 no erro); com +0,3 no erro, a
            # família de muito volume e pouco valor subia sempre
            fam_nova = {"nome": fam, "a": f0[0] + (1.0 if achados else 0.0), "b": f0[1] + (0.0 if achados else 1.0), "usos": f0[2] + 1,
                        "achados": f0[3] + len(achados)}
            self._gravar("espiao.familia", fam_nova, "UPDATE espiao_familia SET a = ?, b = ?, usos = ?, achados = ? WHERE nome = ?",
                         (fam_nova["a"], fam_nova["b"], fam_nova["usos"], fam_nova["achados"], fam))
            c0 = self.con.execute("SELECT usos, achados FROM espiao_consulta WHERE texto = ?", (q,)).fetchone() or (0, 0)
            cons = {"texto": q, "familia": fam, "usos": c0[0] + 1, "achados": c0[1] + len(achados), "ultima": em}
            self._gravar("espiao.consulta", cons, "INSERT OR REPLACE INTO espiao_consulta(texto, familia, usos, achados, ultima) VALUES (?,?,?,?,?)",
                         tuple(cons.values()))
        self.con.commit()
        return {"familia": fam, "consulta": q, "resultados": len(pistas), "achados": achados, "motivos": motivos, "bloqueada": bloqueada}

    CAMINHOS_VARREDURA = ("", "/editais", "/edital", "/patrocinio", "/patrocinios", "/responsabilidade-social", "/investimento-social",
                          "/sustentabilidade", "/chamadas", "/instituto")

    def varredura(self, sites: list[str], n: int = 6) -> dict[str, Any]:
        """14/11/2026 (R55, C11 — a camada 1): a varredura direta das empresas e entidades do cadastro com site, sem buscador
        (o freio das 5 missões sem pista e a janela fechada trazem o Espião para cá). Lê a página inicial e os caminhos comuns de
        editais e de investimento social; vira achado a página com sinal de oportunidade para OSC, pelos mesmos filtros."""
        fam, motivos, achados, lidas = "camada1_cadastro", {}, [], 0
        escolhidos = self.rnd.sample(sites, min(n, len(sites))) if sites else []
        for site in escolhidos:
            base = site if site.startswith("http") else f"https://{site}"
            for cam in self.CAMINHOS_VARREDURA:
                url = base.rstrip("/") + cam
                ok, porque = self.fora_dos_motores(url)
                if not ok or f"espiao-{__import__('hashlib').sha1(url.encode()).hexdigest()[:12]}" in self.barrados:
                    motivos[porque or "barrada"] = motivos.get(porque or "barrada", 0) + 1
                    break
                lido = self.ler(url)
                lidas += 1
                if not lido:
                    continue
                titulo, texto = lido
                if not (OPORT.search(f"{titulo} {texto[:8000]}") and OSC.search(f"{titulo} {texto[:8000]}")):
                    continue
                h = urlsplit(url).hostname or ""
                achados.append(Achado(id=f"espiao-{__import__('hashlib').sha1(url.encode()).hexdigest()[:12]}", motor="espiao",
                                      encontrado_em=date.today().isoformat(), link_divulgacao=url, link_oficial=url, titulo=(titulo or h)[:200],
                                      dados={"familia": fam, "consulta": site, "dominio": h, "origem": "varredura do cadastro (camada 1)"},
                                      documento={"url": url, "sha256": __import__("hashlib").sha256(texto.encode()).hexdigest(), "tipo": "html",
                                                 "leitor": "espiao", "oficial": True, "paginas": [texto]}))
                self.conhecidos.add(url.rstrip("/"))
                break
        em = datetime.now(timezone.utc).isoformat()
        linha_m = {"em": em, "familia": fam, "consulta": ", ".join(escolhidos)[:500], "resultados": lidas, "candidatos": len(achados),
                   "achados": len(achados), "motivos": json.dumps(motivos, ensure_ascii=False), "rotas": json.dumps(["varredura direta"]), "bloqueada": 0}
        self._gravar("espiao.missao", linha_m, "INSERT INTO espiao_missao(em, familia, consulta, resultados, candidatos, achados, motivos, rotas, "
                     "bloqueada) VALUES (?,?,?,?,?,?,?,?,?)", tuple(linha_m.values()))
        self.con.commit()
        return {"familia": fam, "consulta": linha_m["consulta"], "resultados": lidas, "achados": achados, "motivos": motivos, "bloqueada": False}

    def recorrencia(self, horas: int = 72) -> dict[str, Any]:
        """O que o Cérebro mede: as missões recentes, quantas tiveram resultado, e o rendimento de cada família."""
        desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
        n, com, bloq = self.con.execute(
            "SELECT COUNT(*), COALESCE(SUM(achados > 0), 0), COALESCE(SUM(bloqueada), 0) FROM espiao_missao WHERE em >= ?", (desde,)
        ).fetchone()
        fams = [
            {"familia": f, "usos": u, "achados": a}
            for f, u, a in self.con.execute("SELECT nome, usos, achados FROM espiao_familia ORDER BY achados DESC, usos")
        ]
        return {"missoes": n, "com_resultado": com, "bloqueadas": bloq, "taxa": round(com / n, 3) if n else None, "familias": fams[:6]}


def vigiados_pelos_motores(pasta_config: str | Path = "eldorado/motores/canal/config") -> set[str]:
    hosts = set()
    for p in Path(pasta_config).glob("*.toml"):
        for f in tomllib.loads(p.read_text(encoding="utf-8")).get("fonte", []):
            h = urlsplit(f.get("url", "")).hostname
            if h:
                hosts.add(h.lower().removeprefix("www."))
    return hosts
