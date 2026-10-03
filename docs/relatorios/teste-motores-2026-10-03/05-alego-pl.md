# Motor 05 — Assembleia Legislativa de Goiás (`alego-pl`)

**Veredito:** workflow FUNCIONANDO · coleta PARCIAL (lê notícias, não proposições) · resultado FALHA (os 3 registros
são notícias, sem data e com título sujo) · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** às quintas, às 10:53 e 20:53, a cada 7 dias, na nuvem. O disparo é `agenda-motores` →
  `monitoramento-diario` → `src.sensores`.
- **Módulo:** **não tem módulo próprio**; usa o leitor genérico de `src/sensores.py`. Também não tem teste próprio.
- **Leituras:** 42; a última foi em 01/10, às 21:57 (manual). Luz **verde**, mas sem dados novos.
- **Alerta ativo:** "trocar URL: 3 leituras sem achados com página respondendo", com 12 leituras vazias seguidas.

## Onde coleta

| Endereço | Nuvem |
|---|---|
| `portal.al.go.leg.br/` (home) | HTTP 200, 134 KB |
| `portal.al.go.leg.br/noticias` | HTTP 200, 115 KB |
| `transparencia.al.go.leg.br/` | configurado |

- **O problema:** o motor lê a home e as notícias. O objetivo da agenda é outro: **proposições e emendas impositivas
  estaduais**, com janela de outubro a novembro.
- Nenhum endereço configurado aponta para o processo legislativo nem para as emendas.

## Resultado

- 17 achados acumulados, que dão 3 únicos na base, os três notícias de 2026:
  - "Votações conjuntas validam requerimentos e declarações de utilidade pública";
  - "Requerimentos, títulos de cidadania e utilidades públicas são aprovados em bloco";
  - "Nova legislação altera política de fomento à IA…".
- Os títulos foram gravados com a hora e espaços ("15:19 ⏎ …") e **sem data de publicação**.
- Nenhum é oportunidade. São, no máximo, pistas de utilidade pública.

## Histórico de 3 anos

- **Próprio:** nenhum registro datado. **Correlato:** 1 registro, de outra fonte.
- **Recuperação possível:** o processo legislativo e as emendas da ALEGO têm número e ano. A carga de 3 anos é
  viável quando a rota for de proposições, não de notícias.

## Correções, por prioridade

1. **Trocar a rota:** dar ao motor um leitor próprio do processo legislativo e das emendas impositivas da ALEGO, como
   foi feito na Câmara de Goiânia (motor 04 v2). Classificar em OPORTUNIDADE, ACOMPANHAR (utilidade pública, lei de
   fomento, emenda) ou RUÍDO.
2. **Limpar os 3 registros** e corrigir a extração de título e data das notícias (tirar a hora e os espaços, gravar a
   data).
3. **Janela de emendas:** de outubro a novembro, rodar diariamente, e não só às quintas.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | A janela de emendas estaduais está aberta agora (outubro e novembro), e o motor só lê notícias. |
| Pessimista | Tudo o que ele gravou é ruído com título quebrado. |
| Levemente pessimista | Leitor genérico, sem teste próprio: qualquer mudança no site quebra sem aviso. |
| **Neutro** | **O motor roda, mas lê a fonte errada para o objetivo. Prioridade alta: leitor do processo legislativo e das emendas (como o v2 da Câmara), diário na janela de outubro e novembro. Meta: cada emenda impositiva para entidade de Goiânia registrada com deputado e valor.** |
| Levemente otimista | O alerta de troca de URL funcionou: o sistema percebeu o vazio. |
| Otimista | As notícias de utilidade pública mostram que a Assembleia aprova em bloco: dá para seguir a habilitação das entidades. |
| Extremamente otimista | Com 3 anos de emendas, o sistema indica qual deputado tem histórico de destinar ao bairro. |
