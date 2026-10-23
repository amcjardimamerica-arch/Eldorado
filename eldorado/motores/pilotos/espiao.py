"""O PILOTO ESPIÃO (do Eldorado0, titular, 09 e 16/10/2026): caça só o que nenhum motor alcança.

Avaliação que motivou o foco (Eldorado0, 08 e 09/10): 792 missões, 2 com resultado; as buscas eram de editais
públicos, território dos motores. Por isso o Espião busca só:
  editais e chamadas de institutos, fundações e empresas privadas; patrocínio, doação, investimento social,
  voluntariado, matching e cessão (mesmo sem edital); e o internacional (fundos, embaixadas, cooperação), em várias línguas.
Descarta: domínio de governo (é dos motores), buscadores, agregadores, redes sociais, o que um motor já vigia e o que
já está na Biblioteca. Fica só a página com sinal de oportunidade E sinal de OSC.

A família de busca é escolhida por amostragem de Thompson (aprende sozinha qual rende); consulta usada 3 vezes sem
resultado é aposentada. O achado vai à Pertinência e entra no Cartório pela recepção (etapa 1). Estado próprio em
dados/motores/espiao.db (só o Espião escreve); o descanso das rotas de busca vale entre as execuções.
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

SETORES = ["mineradora", "agronegócio", "cooperativa agroindustrial", "energia elétrica", "saneamento", "rede de supermercados", "atacarejo", "banco",
           "cooperativa de crédito", "operadora de telefonia", "indústria farmacêutica", "frigorífico", "construtora", "empresa de tecnologia", "seguradora",
           "montadora", "indústria de alimentos", "indústria de bebidas", "shopping center", "rede de farmácias", "transportadora", "usina de etanol",
           "indústria de fertilizantes", "hospital privado"]
APOIOS = ["edital de patrocínio", "chamada de projetos sociais", "programa de investimento social", "seleção de projetos", "fundo de doação para ONGs",
          "doação de equipamentos para entidades", "voluntariado corporativo", "doação casada (matching)", "prêmio de iniciativas sociais",
          "patrocínio a projetos culturais", "patrocínio a projetos esportivos", "apoio a projetos comunitários", "doação de alimentos para instituições",
          "edital do instituto", "chamada pública de parceiros sociais"]
PUBLICOS = ["crianças e adolescentes", "pessoa idosa", "mulheres", "juventude", "pessoas com deficiência", "comunidades periféricas",
            "catadores de recicláveis", "agricultura familiar", "cultura popular", "esporte de base", "educação", "meio ambiente", "segurança alimentar",
            "população em situação de rua"]
REGIOES = ["Goiás", "Goiânia", "Anápolis", "Aparecida de Goiânia", "Rio Verde", "Goiás", "todo o Brasil", "nacional"]
INTERNACIONAIS = ["Fundo Canadá para Iniciativas Locais", "Embaixada da Alemanha microprojetos", "Embaixada do Japão Assistência a Projetos Comunitários",
                  "Embaixada da França fundo de apoio", "Embaixada dos Países Baixos", "União Europeia sociedade civil Brasil", "Fundação Interamericana IAF",
                  "GEF Small Grants Programme Brasil", "Global Fund for Children", "Fundação Avina", "Open Society Foundations", "Ford Foundation Brasil",
                  "W.K. Kellogg Foundation", "Porticus", "Laudes Foundation", "Oak Foundation", "ONU Mulheres fundo",
                  "UNESCO Fundo Internacional para a Diversidade Cultural", "Ibercultura Viva"]
OPERADORES = ['"regulamento" "inscrições"', 'filetype:pdf "edital"', "intitle:edital", '"inscrições abertas"', '"chamada de projetos"']
LINGUAS = {
    "internacional_ingles": ["call for proposals Brazil civil society {ano}", "grants for NGOs in Brazil {ano}",
    "small grants Brazil community organizations {ano}",
                             "funding opportunity nonprofits Latin America {ano} Brazil eligible", "request for proposals Brazil social projects {ano}"],
    "internacional_espanhol": ["convocatoria organizaciones de la sociedad civil Brasil {ano}", "fondos para ONG América Latina Brasil {ano}",
                               "convocatoria proyectos comunitarios Brasil elegible {ano}"],
    "internacional_frances": ["appel à projets ONG Brésil {ano}", "subventions associations Brésil {ano}",
    "fonds pour la société civile Amérique latine Brésil {ano}"],
    "internacional_alemao": ["Förderung Zivilgesellschaft Brasilien {ano}", "Ausschreibung NGO Brasilien Projekte {ano}",
    "Kleinprojekte Botschaft Brasilien {ano}"],
    "internacional_italiano": ["bando ONG Brasile {ano}", "finanziamenti società civile Brasile {ano}"],
}
OPORT = re.compile(r"(?i)edital|regulamento|inscri[çc][õo]es|chamada|call for proposals|apply now|grant|convocatoria|patroc[ií]nio|doa[çc][ãa]o|"
                   r"sele[çc][ãa]o de projetos|programa de apoio|investimento social|fondos?|appel à projets|ausschreibung|bando")
OSC = re.compile(r"(?i)\bosc\b|\bongs?\b|organiza[çc][õo]es? (da sociedade civil|sociais|sem fins)|associa[çc][õo]es|sociedade civil|nonprofit|non-profit|"
                 r"\bngos?\b|sin fines de lucro|terceiro setor|projetos sociais|entidades|associations|zivilgesellschaft")
GOVERNO = re.compile(r"(?i)(\.gov\.br|\.leg\.br|\.jus\.br|\.mp\.br|\.def\.br|\.mil\.br|\.gov)$")
FORA = re.compile(r"(?i)(^|\.)(duckduckgo\.com|bing\.com|google\.[a-z.]+|wikipedia\.org|youtube\.com|facebook\.com|instagram\.com|linkedin\.com|"
                  r"twitter\.com|x\.com|tiktok\.com|prosas\.com\.br|editaiscult\w*\.com\.br|catarse\.me|vakinha\.com\.br|"
                  r"[\w-]+\.blogspot\.com(\.br)?|[\w-]+\.wordpress\.com|medium\.com|[\w-]+\.substack\.com|jusbrasil\.com\.br)$")
# (o blog e a plataforma de publicação divulgam editais de terceiros: não são a fonte; teste real de 22/10/2026)
DDL = """
CREATE TABLE IF NOT EXISTS familia (nome TEXT PRIMARY KEY, a REAL NOT NULL DEFAULT 1, b REAL NOT NULL DEFAULT 1, usos INTEGER NOT NULL DEFAULT 0,
  achados INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS consulta (texto TEXT PRIMARY KEY, familia TEXT, usos INTEGER NOT NULL DEFAULT 0, achados INTEGER NOT NULL DEFAULT 0, ultima TEXT);
CREATE TABLE IF NOT EXISTS missao (id INTEGER PRIMARY KEY, em TEXT NOT NULL, familia TEXT, consulta TEXT, resultados INTEGER, candidatos INTEGER,
  achados INTEGER, motivos TEXT, rotas TEXT, bloqueada INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS rota (nome TEXT PRIMARY KEY, descansa_ate TEXT);
"""


def familias(empresas: list[str]) -> dict[str, Callable[[random.Random, int], str | None]]:
    regiao = lambda r: r.choice(REGIOES)  # noqa: E731
    f: dict[str, Callable[[random.Random, int], str | None]] = {
        "setor_apoio_regiao": lambda r, a: f"{r.choice(SETORES)} {r.choice(APOIOS)} {regiao(r)} {a}",
        "publico_apoio_empresa": lambda r, a: f"empresa {r.choice(APOIOS)} {r.choice(PUBLICOS)} {regiao(r)} {a}",
        "operador_avancado": lambda r,
        a: f"{r.choice(OPERADORES)} {r.choice(['instituto', 'fundação empresarial', 'empresa'])} {r.choice(PUBLICOS)} {regiao(r)} {a}",
        "rastro_de_patrocinio": lambda r, a: f'"patrocínio" "{r.choice(PUBLICOS)}" projeto {regiao(r)} "apoio" {a}',
        "nao_financeiro": lambda r,
        a: f"{r.choice(['doação de computadores', 'doação de alimentos', 'cessão de espaço', 'voluntariado de funcionários', 'doação de móveis'])} "
                                       f"para ONGs empresa {regiao(r)} {a}",
        "internacional_financiador": lambda r, a: f'"{r.choice(INTERNACIONAIS)}" {r.choice(["edital", "chamada", "call for proposals", "inscrições"])} {a}',
        "associacoes_goias_eventos": lambda r, a: f"{r.choice(['festival', 'corrida beneficente', 'evento beneficente', 'projeto social'])} "
                                                  f"{r.choice(['Goiânia', 'Goiás', 'Anápolis'])} patrocinadores {a}",
    }
    for nome, consultas in LINGUAS.items():
        f[nome] = lambda r, a, c=consultas: r.choice(c).format(ano=a)
    if empresas:
        f["empresa_semente"] = lambda r, a: f'"{r.choice(empresas)}" {r.choice(["instituto", "fundação", "patrocínio", "edital"])} projetos sociais {a}'
    return f


class Espiao:
    def __init__(self, estado: str | Path, consultar: Callable[[str], tuple[list, list[str]]], ler: Callable[[str], tuple[str, str] | None],
                 vigiados: set[str] | None = None, conhecidos: set[str] | None = None, empresas: list[str] | None = None,
                 rnd: random.Random | None = None, descanso_h: float = 2.0):
        Path(estado).parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(estado)
        self.con.executescript(DDL)
        self.consultar, self.ler = consultar, ler
        self.vigiados, self.conhecidos = vigiados or set(), conhecidos or set()
        self.fams = familias(empresas or [])
        self.rnd = rnd or random.Random()
        self.descanso_h = descanso_h
        for f in self.fams:
            self.con.execute("INSERT OR IGNORE INTO familia(nome) VALUES (?)", (f,))
        self.con.commit()

    # ------------------------------------------------------------------ a escolha (Thompson) e o bloqueio
    def bloqueado(self) -> bool:
        """Todas as rotas de busca descansando: não há missão possível agora (o Cérebro não envia)."""
        agora_ = datetime.now(timezone.utc).isoformat()
        rotas = dict(self.con.execute("SELECT nome, descansa_ate FROM rota"))
        return bool(rotas) and all((v or "") > agora_ for v in rotas.values()) and len(rotas) >= 3

    def escolher(self) -> tuple[str, str]:
        ruins = {q for (q,) in self.con.execute("SELECT texto FROM consulta WHERE usos >= 3 AND achados = 0")}
        sorteio = sorted(((self.rnd.betavariate(max(0.1, a), max(0.1, b)), f) for f, a, b in self.con.execute("SELECT nome, a, b FROM familia")
                          if f in self.fams), reverse=True)
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
        for linha in relato:                                            # o descanso das rotas vale entre as execuções
            if "descansa" in linha or "falhou" in linha:
                ate = (datetime.now(timezone.utc) + timedelta(hours=self.descanso_h)).isoformat()
                self.con.execute("INSERT OR REPLACE INTO rota VALUES (?, ?)", (linha.split(":")[0], ate))
        motivos: dict[str, int] = {}
        achados: list[Achado] = []
        candidatos = 0
        for p in pistas[:8]:
            ok, porque = self.fora_dos_motores(p.link)
            if not ok:
                motivos[porque] = motivos.get(porque, 0) + 1
                continue
            lido = self.ler(p.link)
            if not lido:
                motivos["página não lida"] = motivos.get("página não lida", 0) + 1
                continue
            titulo, texto = lido
            base = f"{p.titulo} {titulo} {texto[:6000]}"
            if not (OPORT.search(base) and OSC.search(base)):
                motivos["sem sinal de oportunidade para OSC"] = motivos.get("sem sinal de oportunidade para OSC", 0) + 1
                continue
            candidatos += 1
            h = urlsplit(p.link).hostname or ""
            achados.append(Achado(id=f"espiao-{__import__('hashlib').sha1(p.link.encode()).hexdigest()[:12]}", motor="espiao",
                encontrado_em=date.today().isoformat(),
                                  link_divulgacao=p.link, link_oficial=p.link, titulo=(titulo or p.titulo or h)[:200],
                                  dados={"familia": fam, "consulta": q, "dominio": h, "origem": "missão do piloto Espião"},
                                  documento={"url": p.link, "sha256": __import__("hashlib").sha256(texto.encode()).hexdigest(), "tipo": "html",
                                             "leitor": "espiao", "oficial": True, "paginas": [texto]}))
            self.conhecidos.add(p.link.rstrip("/"))
        bloqueada = not pistas and all(("descans" in r or "falhou" in r or "deslig" in r.lower()) for r in relato)
        self.con.execute("INSERT INTO missao(em, familia, consulta, resultados, candidatos, achados, motivos, rotas, bloqueada) VALUES (?,?,?,?,?,?,?,?,?)",
                         (datetime.now(timezone.utc).isoformat(), fam, q, len(pistas), candidatos, len(achados), json.dumps(motivos, ensure_ascii=False),
                          json.dumps(relato, ensure_ascii=False), int(bloqueada)))
        if not bloqueada:                                               # aprende: reforça a família que rendeu
            self.con.execute("UPDATE familia SET usos = usos + 1, achados = achados + ?, a = a + ?, b = b + ? WHERE nome = ?",
                             (len(achados), 1.0 if achados else 0.0, 0.0 if achados else 0.3, fam))
            self.con.execute("INSERT INTO consulta(texto, familia, usos, achados, ultima) VALUES (?, ?, 1, ?, ?) ON CONFLICT(texto) DO UPDATE SET "
                             "usos = usos + 1, achados = achados + excluded.achados, ultima = excluded.ultima",
                             (q, fam, len(achados), datetime.now(timezone.utc).isoformat()))
        self.con.commit()
        return {"familia": fam, "consulta": q, "resultados": len(pistas), "achados": achados, "motivos": motivos, "bloqueada": bloqueada}

    def recorrencia(self, horas: int = 72) -> dict[str, Any]:
        """O que o Cérebro mede: as missões recentes, quantas tiveram resultado, e o rendimento de cada família."""
        desde = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat()
        n, com, bloq = self.con.execute("SELECT COUNT(*), COALESCE(SUM(achados > 0), 0), COALESCE(SUM(bloqueada), 0) FROM missao WHERE em >= ?",
                                        (desde,)).fetchone()
        fams = [{"familia": f, "usos": u, "achados": a} for f, u, a in self.con.execute("SELECT nome, usos, achados FROM familia ORDER BY achados DESC, usos")]
        return {"missoes": n, "com_resultado": com, "bloqueadas": bloq, "taxa": round(com / n, 3) if n else None, "familias": fams[:6]}


def vigiados_pelos_motores(pasta_config: str | Path = "eldorado/motores/canal/config") -> set[str]:
    hosts = set()
    for p in Path(pasta_config).glob("*.toml"):
        for f in tomllib.loads(p.read_text(encoding="utf-8")).get("fonte", []):
            h = urlsplit(f.get("url", "")).hostname
            if h:
                hosts.add(h.lower().removeprefix("www."))
    return hosts
