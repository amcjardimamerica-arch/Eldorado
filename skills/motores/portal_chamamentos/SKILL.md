---
name: portal_chamamentos
description: Ler portais de chamamentos e contratações públicas (PNCP, SALIC, Mapa das OSC, portais de prefeituras).
---

# motores/portal_chamamentos

**Quando carrega:** a cada leitura de um canal desta família (config/skills_motores.json)  
**Falhas típicas:** falha_parcial (429: espaçar 1,5 s) / sem_rendimento — plano em config/linha_producao.json › planos_de_correcao

## Instrução
Use a API ou a busca do portal com o prazo OFICIAL de encerramento; guarde a chave do edital (no PNCP, CNPJ/ano/sequencial) e o PDF anexado pelo órgão. A modalidade de contratação (pregão, dispensa) só entra com instrumento MROSC explícito. Edital de OSC de qualquer UF vira livro (o PNCP é a porta de entrada nacional); o território é enquadramento, não descarte.

## Lições aprendidas
- 02/10 — PNCP nacional: 173 oportunidades em 24 estados; ~96% corretas; os erros viraram vetos nacionais.
