"""As visões do painel: o que cada tela mostra, lido dos bancos (só leitura), num único arquivo de dados.

Cada tela lê uma visão; nenhuma tela lê os bancos diretamente. O painel é gerado ao fim de cada passagem.
"""
from __future__ import annotations

import json
import sqlite3
import tomllib
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ..missao import itens as I

TERRITORIO = {"municipal_go": "Município de Goiás", "estadual_go": "Governo de Goiás", "capital_outro_estado": "Capital de outro estado",
              "estadual_outro_estado": "Outro estado", "nacional": "Nacional", "internacional": "Internacional", "indeterminado": "A revisar"}


SQL_LEIS = "SELECT le.id, le.ementa, le.link_oficial FROM livro_lei ll JOIN lei le ON le.id = ll.lei_id WHERE ll.livro_id=?"
SQL_ALARMES = "SELECT gravidade, modulo, mensagem, aberto_em, repeticoes FROM alarme WHERE fechado_em IS NULL ORDER BY aberto_em DESC LIMIT 30"


def _ro(p: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def gerar(dados: str | Path, config: str | Path = "config", hoje: date | None = None) -> dict[str, Any]:
    dados, config, hoje = Path(dados), Path(config), hoje or date.today()
    b, c = _ro(dados / "biblioteca.db"), _ro(dados / "cerebro.db")
    try:
        livros = [dict(r) for r in b.execute(
            "SELECT l.id, l.titulo, l.orgao, l.uf, l.estrela, l.selo_livro, l.link_oficial, l.link_divulgacao, d.abrangencia, d.municipio, d.esfera,"
            " d.inscricao_inicio, d.inscricao_fim, d.resultado_em, d.valor_min, d.valor_max, d.modalidade, d.area, d.situacao_prazo, d.validacao"
            " FROM livro l JOIN livro_dados d ON d.livro_id = l.id WHERE l.situacao <> 'excluido' AND d.validacao <> 'expurgado'"
            " AND l.id NOT IN (SELECT livro_unido FROM uniao)")]                        # o livro unido a outro aparece só no que fica
        abertas = sorted((x for x in livros if x["situacao_prazo"] == "aberta"), key=lambda x: (x["inscricao_fim"] or "9999", x["titulo"] or ""))
        por_terr: dict[str, int] = {}
        for x in livros:
            por_terr[TERRITORIO.get(x["abrangencia"], "A revisar")] = por_terr.get(TERRITORIO.get(x["abrangencia"], "A revisar"), 0) + 1
        programas = []
        # o programa é o livro do próprio mecanismo (entregue pela seção "programa" do motor); as demais publicações
        # ligadas à mesma lei aparecem dentro dele
        sql_prog = ("SELECT DISTINCT l.id, l.titulo, l.estrela, l.link_oficial FROM livro l JOIN achado a ON a.livro_id = l.id "
                    "WHERE a.id LIKE '%-programa-%' AND l.situacao <> 'excluido'")
        for r in b.execute(sql_prog):
            certs = I.melhor([dict(x) for x in b.execute("SELECT * FROM certidao WHERE livro_id=? AND situacao IN ('comprovado','dispensado')", (r["id"],))])
            leis = [dict(x) for x in b.execute(SQL_LEIS, (r["id"],))]
            relacionados = [dict(x) for x in b.execute(
                "SELECT DISTINCT l.id, l.titulo, l.link_oficial FROM livro_lei ll JOIN livro l ON l.id = ll.livro_id WHERE ll.lei_id IN "
                "(SELECT lei_id FROM livro_lei WHERE livro_id=?) AND l.id <> ? AND l.situacao <> 'excluido' ORDER BY l.criado_em DESC LIMIT 20",
                (r["id"], r["id"]))]
            programas.append({**dict(r), "leis": leis, "relacionados": relacionados,
                              "certidoes": [{"item": k, "valor": v["valor"], "trecho": v.get("trecho"), "pagina": v.get("pagina"),
                                                                     "fase": v.get("fase")} for k, v in sorted(certs.items())]})
        agenda = tomllib.loads((config / "agenda.toml").read_text(encoding="utf-8")) if (config / "agenda.toml").exists() else {}
        horarios = {m["id"]: m.get("horarios", []) for m in agenda.get("modulo", [])}
        motores = []
        for mid in sorted(horarios):
            ult = c.execute("SELECT inicio, fim, achados, erro FROM execucao_motor WHERE motor=? ORDER BY id DESC LIMIT 1", (mid,)).fetchone()
            tot = c.execute("SELECT COUNT(*), COALESCE(SUM(achados), 0) FROM execucao_motor WHERE motor=?", (mid,)).fetchone()
            try:                                                  # o estado das fontes, dentro do Cérebro (motor_fonte)
                fontes = [dict(x) for x in c.execute("SELECT nome, leituras, achados, aceitos, barrados, falhas, ultimo_erro, ultima "
                                                     "FROM motor_fonte WHERE motor = ? ORDER BY nome", (mid,))]
            except sqlite3.Error:
                fontes = []
            aceitos = b.execute("SELECT COUNT(*) FROM achado WHERE motor=? AND decisao='aceito'", (mid,)).fetchone()[0]
            motores.append({"id": mid, "horarios": horarios[mid], "ultima": dict(ult) if ult else None, "execucoes": tot[0], "achados": tot[1],
                            "aceitos": aceitos, "fontes": fontes})
        passagens = [dict(x) for x in c.execute("SELECT inicio, fim, estado FROM execucao ORDER BY inicio DESC LIMIT 12")]
        alarmes = [dict(x) for x in c.execute(SQL_ALARMES)]
        estrelas: dict[str, int] = {}
        for x in livros:
            estrelas[x["estrela"] or "sem"] = estrelas.get(x["estrela"] or "sem", 0) + 1
        return {
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hoje": hoje.isoformat(),
            "resumo": {"livros": len(livros), "abertas": len(abertas), "territorio": por_terr, "estrelas": estrelas,
                       "revisar": sum(1 for x in livros if x["validacao"] == "revisar"), "ultima_passagem": passagens[0] if passagens else None,
                       "alarmes": len(alarmes)},
            "abertas": abertas, "programas": programas,
            # a Biblioteca em listas compactas (a tela só usa estes campos): id, título, órgão, UF, estrela, território, município,
            # fim das inscrições, situação do prazo, validação, link oficial
            "livros_campos": ["id", "titulo", "orgao", "uf", "estrela", "abrangencia", "municipio", "inscricao_fim", "situacao_prazo", "validacao",
                              "link_oficial"],
            "livros": [[x["id"], x["titulo"], x["orgao"], x["uf"], x["estrela"], x["abrangencia"], x["municipio"], x["inscricao_fim"],
                        x["situacao_prazo"], x["validacao"], x["link_oficial"]] for x in livros],
            "motores": motores, "passagens": passagens, "alarmes": alarmes,
            "territorios": TERRITORIO,
        }
    finally:
        b.close()
        c.close()


def publicar(dados: str | Path, saida: str | Path, config: str | Path = "config") -> dict[str, int]:
    """Gera a página e o arquivo de dados na pasta publicada (docs/, servida pelo GitHub Pages)."""
    saida = Path(saida)
    (saida / "dados").mkdir(parents=True, exist_ok=True)
    painel = gerar(dados, config)
    (saida / "dados" / "painel.json").write_text(json.dumps(painel, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (saida / "index.html").write_text((Path(__file__).parent / "paginas" / "painel.html").read_text(encoding="utf-8"), encoding="utf-8")
    (saida / ".nojekyll").write_text("")
    return {"livros": painel["resumo"]["livros"], "abertas": painel["resumo"]["abertas"], "bytes": (saida / "dados" / "painel.json").stat().st_size}
