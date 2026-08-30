# Operação

## Comandos

```bash
python -m src.executar_diario            # varredura completa (o que roda seg/qua)
python -m src.sentinela                  # checagem diária leve
python -m src.executar_farol             # reprocessar triagem/casos/ranking + Farol IA
python -m src.retrospectivo              # carga histórica (janelas mensais pendentes)
python -m src.resumo_execucao            # resumo humano + decisão de alerta
python -m unittest discover -s tests -v
python scripts/promover.py listar capturada
python scripts/promover.py ID verificada_primaria --por "Nome" --nota "conferido na fonte"
python scripts/confirmar_pista.py PISTA_ID https://dominio-oficial/edital --por "Nome"
python scripts/cobertura_catalogo.py     # abrangência das camadas sobre os 260 pontos
python scripts/importar_acervo.py entrada_acervo
python scripts/importar_catalogo_captacao.py planilha.xlsx
python scripts/criar_associacao.py SLUG "Nome da associação"
python scripts/ingestao_associacao.py SLUG documento.docx
```

## Estados de uma oportunidade

`pista_do_acervo_pendente_url_primaria` / `pista_imprensa` → `capturada` → `verificada_primaria` ou `verificada_dupla` → `elegivel` ou `inelegivel` → `em_preparacao` → `submetida` → `selecionada` ou `nao_selecionada` → `em_execucao` → `prestacao_de_contas` → `encerrada`.

**Quem verifica:** a verificação assistida (sem IA) promove `capturada → verificada_primaria` quando abre a URL primária em fonte catalogada, encontra termos de edital e não há padrão de injeção — com evidência hasheada e auditoria. O humano continua soberano via `scripts/promover.py` (promove, rebaixa ou descarta; status definidos por humano nunca são rebaixados pela máquina).

## O caso no Farol (por associação, universo isolado)

```text
farol/casos/<oportunidade>/
  01_enquadramento.json                triagem inicial
  01b_enquadramento_com_requisitos.json portão com requisitos reais do edital
  02_plano_trabalho.md                 rascunho editável (nunca sobrescrito)
  03_manual_presidente.md              manual geral (nunca sobrescrito)
  04_documentos_necessarios.md         checklist
  05_prestacao_contas.md               matriz
  conselho/01..07_*/entrada.json       pacotes isolados das 7 lentes
  conselho/01..07_*/resposta.json      respostas (IA ou fila externa)
  06_parecer_conselho.md               ponto de vista + personalidade + vantagens/desvantagens
  07_pacote_presidente.md              decisão, prazos, pendências e orientações OBJETIVAS
  submissao/                           documentos finais limpos (sem IA, sem placeholders)
  rascunhos/                           o que ainda tem pendência, com os motivos
```

Sem credencial de IA (`FAROL_AI_API_KEY` em Actions Secrets), o sistema prepara os pacotes e para aí, dizendo isso com clareza — nunca finge parecer. Com credencial, o fluxo segue automático dentro dos limites de `config/ia.json` (casos por execução, tamanhos, modelos por tarefa).

## Dossiê e aprendizado do financiador

O diretório individual reúne eventos comprovados, valor quando publicado, objeto, forma de acesso, requisitos recorrentes e links. “Padrão” só é promovido após **duas ocorrências validadas**; antes disso aparece como hipótese. `aprendizado.json` traz também a **previsão de janela** (mesmo mês em 2+ anos) para preparar a entidade ANTES da abertura; o consolidado fica em `estado/previsoes.json`.

## Plano de trabalho e prestação de contas

O Farol gera checklist a partir do edital e do procedimento aplicável. A redação final preserva a estrutura exigida pela fonte, com indicadores mensuráveis, cronograma, memória de cálculo, riscos e plano de evidências. A prestação de contas nasce junto com o plano: cada meta define desde o início qual documento provará sua entrega. Documentos em `submissao/` saem em nome da entidade, prontos para conferência e assinatura da diretoria; tudo que é orientação vai ao pacote do presidente.
