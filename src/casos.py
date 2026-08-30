from __future__ import annotations
import json
from pathlib import Path
from . import conselho
from .farol import evaluate
from .nucleo import ROOT, load_json, now_iso, write_json

def plan_text(profile,opp,decision):
    return f'''# Plano de Trabalho — {opp["titulo"]}

> Rascunho técnico condicionado à leitura integral do edital e à revisão jurídica, contábil e institucional.

## 1. Identificação

- Proponente: {profile["nome"]}
- Oportunidade: [{opp["titulo"]}]({opp["url"]})
- Enquadramento calculado: {decision["faixa"]} ({decision["pontuacao_preliminar"]}/100)
- Prazo localizado: {opp.get("prazo_texto") or "NÃO EXTRAÍDO — conferir no edital"}

## 2. Diagnóstico e justificativa

[PREENCHER somente com dados territoriais comprovados e aderentes ao objeto do edital.]

## 3. Objeto, público e território

[TRANSCREVER o objeto permitido; delimitar público, quantidade, critérios de seleção e território.]

## 4. Objetivos

- Objetivo geral: [PREENCHER]
- Objetivos específicos: [PREENCHER com verbos mensuráveis]

## 5. Metas, indicadores e evidências

| Meta | Indicador | Linha de base | Resultado | Evidência | Responsável |
|---|---|---:|---:|---|---|
| [M1] | [I1] | [ ] | [ ] | lista, registro e relatório | [ ] |

## 6. Metodologia e cronograma

| Etapa | Atividade | Início | Fim | Dependência |
|---|---|---|---|---|
| Preparação | [PREENCHER] | [ ] | [ ] | habilitação |

## 7. Equipe, governança e proteção

[Definir funções, seleção, voluntariado, proteção de crianças e adolescentes, LGPD, acessibilidade e conflitos de interesse.]

## 8. Orçamento e memória de cálculo

| Item | Unidade | Quantidade | Valor unitário | Total | Pesquisa de preço |
|---|---:|---:|---:|---:|---|
| [PREENCHER] | [ ] | [ ] | [ ] | [ ] | [fonte] |

## 9. Monitoramento, riscos e sustentabilidade

[Vincular cada risco a prevenção, responsável e evidência; explicar continuidade após o recurso.]

## 10. Conformidade e prestação de contas

[Inserir somente leis vigentes e regras expressas no edital. Cada despesa deve nascer ligada à meta, rubrica, autorização, documento fiscal, pagamento e prova de entrega.]
'''

def president_manual(profile,opp):
    return f'''# Manual do Presidente — {opp["titulo"]}

## Decisão imediata

- Confirmar a versão e todas as retificações em {opp["url"]}.
- Registrar o prazo: **{opp.get("prazo_texto") or "não extraído"}**.
- Nomear responsável técnico, financeiro e documental.
- Não assinar declaração sem prova arquivada.

## Antes da inscrição

1. Conferir objeto social, território, tempo de existência, experiência e impedimentos.
2. Validar estatuto, ata, representação, certidões, cadastro bancário e inscrições em conselhos.
3. Aprovar plano, orçamento e contrapartidas na instância competente.
4. Guardar edital, anexos, perguntas, respostas e retificações com hash e data.

## Durante a execução

1. Usar conta e centro de custo exclusivos quando exigidos.
2. Autorizar despesas antes da contratação e verificar rubrica, preço e conflito de interesse.
3. Guardar contrato, pesquisa de preço, nota fiscal, comprovante de pagamento e prova de entrega.
4. Registrar presença, consentimento de imagem, indicadores e ocorrências.
5. Solicitar autorização formal antes de alterar meta, cronograma, equipe ou orçamento.

## Prestação de contas

1. Conciliar extrato, razão contábil, orçamento e metas.
2. Entregar relatório de execução do objeto e relatório financeiro no formato do concedente.
3. Justificar desvios e devolver saldo quando exigido.
4. Preservar os documentos pelo prazo legal e pelo prazo específico do edital.

## Prazos internos preventivos

- T-30: diagnóstico documental e jurídico.
- T-15: plano e orçamento fechados.
- T-7: revisão independente.
- T-2: protocolo, recibo e cópia imutável.

Os marcos acima são preventivos; prevalecem os prazos expressos no edital e no instrumento assinado.
'''

def prepare(profile: dict, opportunity: dict, decision: dict) -> Path:
    assoc_root=ROOT/"dados/associacoes"/profile["id"]
    if assoc_root.resolve().parent!=(ROOT/"dados/associacoes").resolve(): raise ValueError("universo inválido")
    root=assoc_root/"farol/casos"/opportunity["id"]; root.mkdir(parents=True,exist_ok=True)
    write_json(root/"01_enquadramento.json",{"gerado_em":now_iso(),**decision,"fundamentos":decision.get("razoes",[]),"ressalvas":decision.get("riscos",[])})
    (root/"02_plano_trabalho.md").write_text(plan_text(profile,opportunity,decision),encoding="utf-8")
    (root/"03_manual_presidente.md").write_text(president_manual(profile,opportunity),encoding="utf-8")
    (root/"04_documentos_necessarios.md").write_text("# Documentos necessários\n\n- [ ] Edital e retificações\n- [ ] Estatuto registrado\n- [ ] Ata e representação vigente\n- [ ] Certidões exigidas\n- [ ] Comprovantes de experiência\n- [ ] Inscrições em conselhos/fundos, se exigidas\n- [ ] Plano e orçamento aprovados\n- [ ] Declarações do edital\n- [ ] Autorizações de imagem e tratamento de dados\n- [ ] Pasta contábil e bancária exclusiva\n",encoding="utf-8")
    (root/"05_prestacao_contas.md").write_text("# Matriz de prestação de contas\n\n| Meta | Entrega | Documento fiscal | Pagamento | Evidência do objeto | Status |\n|---|---|---|---|---|---|\n| [M1] | [ ] | [ ] | [ ] | [ ] | pendente |\n",encoding="utf-8")
    conselho.prepare(root,profile,opportunity,decision)
    return root

def run(triggers: list[dict]) -> int:
    db=ROOT/"dados/oportunidades/oportunidades.jsonl"; opportunities={x["id"]:x for x in (json.loads(line) for line in db.read_text(encoding="utf-8").splitlines() if line.strip())}
    criteria=load_json(ROOT/"config/criterios.json"); count=0
    for trigger in triggers:
        profile=load_json(ROOT/"dados/associacoes"/trigger["associacao_id"]/"perfil_publico.json"); opportunity=opportunities[trigger["oportunidade_id"]]
        full=evaluate(profile,opportunity,criteria)
        decision={**trigger,"triagem_preliminar":trigger,"avaliacao_requisitos":full,"pontuacao_preliminar":full["pontuacao"],"faixa":full["faixa"],"razoes":[full["explicacao"]],"riscos":[*trigger.get("riscos",[]),*full.get("bloqueios",[]),*full.get("faltantes",[])],"acoes_para_maximizar":full.get("acoes_para_maximizar",[])}
        prepare(profile,opportunity,decision); count+=1
    return count
