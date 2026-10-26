"""O Comandante apresenta à titular (a etapa C10; a fase 6 do desenho, titular, 25/10/2026): o que foi encontrado,
organizado para a decisão humana — as oportunidades que fecham antes, as novidades do dia, o que falta e o estado do
sistema — e, redigido pela IA do cargo Comandante (com o contexto da memória do Cérebro), o que decidir primeiro e por quê.
Sem a IA, as prioridades saem pela regra (o que fecha antes; o ouro primeiro). O relatório fica em verificacao/relatorios/
(o texto e os dados) e o painel mostra o mais recente no topo da página inicial."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PASTA = Path("verificacao/relatorios")
A_CADA_H = 6
PESO = {"ouro": 3, "prata": 2, "bronze": 1}

# a contagem única dos livros no site inteiro (25/10/2026): só os vivos
VIVOS = "FROM passaporte p JOIN livro l ON l.id = p.livro_id WHERE l.situacao NOT IN ('excluido', 'unido')"


def _selo(estrela: str | None, selo: str | None) -> str:
    return max((estrela or "sem", selo or "sem"), key=lambda s: PESO.get(s, 0))


def reunir(dados: Path, agora: datetime) -> dict[str, Any]:
    bib = sqlite3.connect(f"file:{dados / 'biblioteca.db'}?mode=ro", uri=True)
    cer = sqlite3.connect(f"file:{dados / 'cerebro.db'}?mode=ro", uri=True)
    hoje, h24 = agora.date(), (agora - timedelta(hours=24)).isoformat()
    try:
        abertas = bib.execute(
            "SELECT l.id, l.titulo, l.orgao, l.uf, l.link_oficial, l.estrela, l.selo_livro, d.inscricao_fim, p.fase FROM livro l "
            "JOIN livro_dados d ON d.livro_id = l.id JOIN passaporte p ON p.livro_id = l.id "
            "WHERE d.situacao_prazo = 'aberta' AND l.situacao NOT IN ('excluido', 'unido') ORDER BY d.inscricao_fim"
        ).fetchall()
        fecham = []
        for lid, tit, org, uf, link, est, selo, fim, fase in abertas:
            try:
                dias = (datetime.fromisoformat(str(fim)[:10]).date() - hoje).days
            except ValueError:
                continue
            if 0 <= dias <= 7:
                fecham.append(
                    {
                        "livro": lid,
                        "titulo": tit,
                        "orgao": org,
                        "uf": uf,
                        "link": link,
                        "selo": _selo(est, selo),
                        "fecha_em": str(fim)[:10],
                        "dias": dias,
                        "fase": fase,
                    }
                )
        fecham.sort(key=lambda x: (x["dias"], -PESO.get(x["selo"], 0)))
        novidades = {
            "achados_aceitos": bib.execute(
                "SELECT COUNT(*) FROM achado WHERE decisao = 'aceito' AND encontrado_em >= ?", (hoje.isoformat(),)
            ).fetchone()[0],
            "livros_novos": bib.execute("SELECT COUNT(*) FROM livro WHERE criado_em >= ?", (h24,)).fetchone()[0],
            "dos_pilotos": bib.execute(
                "SELECT COUNT(*) FROM achado WHERE motor IN ('espiao', 'interceptador') AND encontrado_em >= ?", (hoje.isoformat(),)
            ).fetchone()[0],
        }
        falta = {
            "aguardam_o_chrome": bib.execute(
                "SELECT COUNT(*) " + VIVOS + " AND p.fase = 'analise externa'"
            ).fetchone()[0]
        }

        def um(sql: str, args: tuple = ()) -> Any:
            try:
                return cer.execute(sql, args).fetchone()[0]
            except sqlite3.Error:
                return None

        sistema = {
            "decisoes_do_comandante_24h": um("SELECT COUNT(*) FROM comandante_decisao WHERE em >= ?", (h24,)),
            "missoes_do_espiao_24h": um("SELECT COUNT(*) FROM espiao_missao WHERE em >= ?", (h24,)),
            "alarmes_graves_abertos": um("SELECT COUNT(*) FROM alarme WHERE fechado_em IS NULL AND gravidade IN ('alta', 'critica')"),
        }
    finally:
        bib.close()
        cer.close()
    return {
        "em": agora.isoformat(timespec="seconds"),
        "abertas": len(abertas),
        "ouro_abertas": sum(1 for a in abertas if _selo(a[5], a[6]) == "ouro"),
        "fecham_em_7_dias": fecham[:15],
        "novidades": novidades,
        "falta": falta,
        "sistema": sistema,
    }


def prioridades_pela_regra(r: dict[str, Any]) -> list[dict[str, str]]:
    p = [
        {
            "o_que": f"Decidir a inscrição em «{x['titulo'][:90]}» ({x['orgao'] or x['uf'] or ''})",
            "por_que": f"fecha em {x['dias']} dia(s) ({x['fecha_em']}); selo {x['selo']}",
        }
        for x in r["fecham_em_7_dias"][:5]
    ]
    if r["falta"]["aguardam_o_chrome"]:
        p.append(
            {
                "o_que": f"Rodar o lote do Claude no Chrome ({r['falta']['aguardam_o_chrome']} livro(s))",
                "por_que": "a validação final desses livros depende do Chrome",
            }
        )
    if r["sistema"].get("alarmes_graves_abertos"):
        p.append({"o_que": f"Ver os {r['sistema']['alarmes_graves_abertos']} alarme(s) grave(s) abertos", "por_que": "podem estar parando uma etapa"})
    return p


def redigir(r: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """A IA do cargo Comandante (com a memória do Cérebro) redige o que decidir primeiro e por quê; sem a IA, a regra."""
    from ..nucleo.ia import IA, SemIA

    ia = IA(cargo_nome="comandante")
    if ia.disponivel():
        pedido = (
            "Com estes dados do Eldorado, diga à titular o que ela deve decidir primeiro e por quê (no máximo 5 prioridades, "
            'só com o que está nos dados). Responda em JSON: {"resumo": "...", "prioridades": [{"o_que": "...", "por_que": "..."}]}\n'
            + json.dumps(r, ensure_ascii=False)[:6000]
        )
        try:
            resposta, _uso = ia.pedir("apresentar à titular", pedido, 900)
            if isinstance(resposta, dict) and resposta.get("prioridades"):
                return resposta, "a IA do Comandante (Qwen3-8B, com a memória do Cérebro)"
        except SemIA:
            pass
    return {
        "resumo": f"{r['abertas']} oportunidades abertas ({r['ouro_abertas']} com ouro); {len(r['fecham_em_7_dias'])} fecham em 7 dias.",
        "prioridades": prioridades_pela_regra(r),
    }, "a regra (o que fecha antes; o ouro primeiro)"


def texto(r: dict[str, Any], red: dict[str, Any], autor: str) -> str:
    linhas = [f"# Para a sua decisão — {r['em'][:16].replace('T', ' ')} UTC", "", red.get("resumo", ""), "", "## O que decidir primeiro"]
    linhas += [f"{i}. **{p.get('o_que', '')}** — {p.get('por_que', '')}" for i, p in enumerate(red.get("prioridades", []), 1)]
    linhas += ["", "## Fecham em até 7 dias"]
    linhas += [f"- {x['fecha_em']} · {x['selo']} · {x['titulo']} — {x['link'] or ''}" for x in r["fecham_em_7_dias"]] or ["- nenhuma"]
    n, s = r["novidades"], r["sistema"]
    linhas += [
        "",
        "## O dia",
        f"- {n['achados_aceitos']} achados aceitos hoje ({n['dos_pilotos']} dos pilotos); {n['livros_novos']} livros novos em 24 h",
        f"- {r['falta']['aguardam_o_chrome']} livro(s) à espera do Claude no Chrome",
        f"- o Comandante tomou {s.get('decisoes_do_comandante_24h')} decisões e o Espião voou {s.get('missoes_do_espiao_24h')} missões em 24 h",
        f"- {s.get('alarmes_graves_abertos')} alarme(s) grave(s) abertos",
        "",
        f"_Redigido por: {autor}._",
    ]
    return "\n".join(linhas) + "\n"


def apresentar(dados: Path, pasta: Path = PASTA, agora: datetime | None = None, forcar: bool = False) -> dict[str, Any] | None:
    agora = agora or datetime.now(timezone.utc)
    pasta.mkdir(parents=True, exist_ok=True)
    ultimos = sorted(pasta.glob("*.json"))
    if ultimos and not forcar:
        try:
            ult = datetime.fromisoformat(json.loads(ultimos[-1].read_text(encoding="utf-8"))["em"])
            if agora - ult < timedelta(hours=A_CADA_H):
                return None
        except (ValueError, KeyError):
            pass
    r = reunir(dados, agora)
    red, autor = redigir(r)
    nome = agora.strftime("%Y-%m-%d-%H%M")
    saida = {**r, "redacao": red, "redigido_por": autor}
    (pasta / f"{nome}.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / f"{nome}.md").write_text(texto(r, red, autor), encoding="utf-8")
    return saida


def no_apresentar(itens: list[dict[str, Any]], parametros: dict[str, Any], contexto) -> list[dict[str, Any]]:
    """Nó da passagem (o Comandante, C10): o relatório para a titular, no máximo a cada 6 horas."""
    dados = Path(parametros.get("dados", "dados"))
    if not ((dados / "cerebro.db").exists() and (dados / "biblioteca.db").exists()):
        return []
    pasta = Path(parametros.get("pasta", str(PASTA)))
    if not pasta.is_absolute():  # relativa à raiz dos dados (na produção, a do repositório)
        pasta = dados.resolve().parent / pasta
    r = apresentar(dados, pasta)
    return [{"apresentado": bool(r), "por": (r or {}).get("redigido_por")}]
