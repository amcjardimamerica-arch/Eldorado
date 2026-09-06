# Relatório — pontos do sistema que acionam IA e situação em 06/09/2026

Decisão do titular: o GitHub para na FASE 2 (coleta, fonte oficial, PDF→texto, extração determinística, regramentos); a FASE 3 (IA) roda por
rotina externa (agente Claude, conta do titular, domingo 03h) e devolve os resultados pelo repositório; da FASE 4 em diante o sistema segue.

| Ponto | Onde | Antes | Agora |
|---|---|---|---|
| Extração dos 12 itens (Haiku→Sonnet→Opus) | src/fonte_edital.investigar ← src/enquadramento.run | chamava a API; sem chave → "aguardando credencial" | não roda no GitHub; feito pela rotina externa (pacote → respostas_agente → ingerir) |
| Análise de enquadramento (Fable 5.1) | src/enquadramento.run | idem | idem — campo `enquadramento` das respostas do agente |
| Busca de prazo por IA (chamamentos sem faixa) | src/prazos_ia | passo do workflow | passo desativado no CI; coberto pelo pacote do agente |
| IA dos Motores Opressores (3º/6º/9º dia, conselho) | src/opressores.run | passo do bloco 04h | disjuntores continuam; chamadas de IA devolvem "fase 3 por rotina externa" |
| Farol parecer / conselho do edital (fase 3 antiga) | src/farol_parecer, src/conselho_edital | passo do workflow | passo desativado no CI; a rotina externa produz o parecer |
| Botão "subir informação faltante" (painel) | Enquadramento | abre complemento.md | mantido — o agente lê os complementos |
| Botões "inscrição realizada" / "dispensar" | perfil da associação | locais + export | mantidos; inconformidade do agente arquiva automaticamente |
| Quadro de luzes por modelo | cartão do edital | vermelho (sem chave) | verde/amarelo quando a rotina externa registra as tentativas (`agente-claude`) |
| Motor de empresas / patrocínio / SALIC | src/empresas, src/patrocinios | sem IA | sem mudança |

Nenhum ponto de IA depende mais de FAROL_AI_API_KEY no GitHub. Todos passam pelo mesmo canal: `python -m src.enquadramento pacote` → JSON por
edital em dados/editais/respostas_agente/ → `python -m src.enquadramento ingerir` (itens, regras, documentos, página do órgão, parecer,
enquadramento, selo de Conformidade/Inconformidade).
