# Motor 11 — CNJ: destinação de prestações pecuniárias (`judiciario-cnj`)

**Veredito:** workflow PARCIAL (motor criado em 02/10 às 19:27; ainda não rodou) · coleta FUNCIONANDO pela busca do
Portal do CNJ · resultado FUNCIONANDO (o edital de Itaberaí também veio por aqui) · histórico de 3 anos PARCIAL
(artigos antigos vistos, mas não registrados).

## Workflow

- **Agenda:** todos os dias, às 07:53, na nuvem. O módulo é `src/judiciario_go.py` (`ler_parte("judiciario-cnj")`), e o
  teste passa.
- **Nunca rodou** com o id novo.
- **Antecessores:**
  - `cnj-destinacoes`: 40 leituras, **0 achados**, lendo a home e as licitações do CNJ. Era a fonte errada; hoje está
    inativo, o que está correto.
  - `judiciario-cnj-tjgo`: 2 leituras com a busca do CNJ.

## Onde coleta

| Fonte | Endereço | Situação |
|---|---|---|
| C — busca do Portal do CNJ (republica editais dos tribunais) | `cnj.jus.br/?s={termo}` com 4 termos ("prestação pecuniária edital", "penas pecuniárias projetos sociais"…) | Responde (a home deu HTTP 200 na nuvem, 364 KB); até 8 artigos por execução |
| Regra nacional | Res. CNJ 558/2024 | Referência |

## Resultado

- A busca viu 8 artigos.
- **1 é de Goiás e está aberto:** "Edital seleciona projetos de Itaberaí (GO) para receberem recursos de prestação
  pecuniária". É o mesmo edital do motor 07, sem duplicata na base.
- **Os outros 7 são de outros estados ou antigos:** AC, Niterói (covid), PE, RO, TRF e TJRJ (R$ 4,4 milhões para 51
  entidades). Servem de referência de valores e prática.
- Os 2 registros do CNJ na base (prêmios PopRuaJud e gestão de pessoas) vêm de outra fonte (`captacao-190`) e são
  ruído para captação.

## Histórico de 3 anos

- **Próprio:** 1 registro, de 2026.
- **Lacuna:** os artigos antigos vistos pela busca ficam só em "vistos", sem data nem valor na base.
- **Recuperação possível:** a busca do CNJ é paginada e alcança anos. Gravar cada edital de comarca de 2023 a 2026
  (tribunal, valor, áreas, mês) dá a referência nacional e, para Goiás, o calendário das comarcas.

## Correções, por prioridade

1. **Corrigir a quebra dos sensores** e confirmar a leitura diária das 07:53 com o id novo.
2. **Registrar o histórico** dos artigos de edital (2023 a 2026), com tribunal, comarca, valor e data. Hoje eles são
   vistos e descartados.
3. **Separar Goiás dos demais estados** no painel: só GO é oportunidade, o resto é referência.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | Nunca rodou com o nome novo, e o antecessor rendeu zero em 40 dias. |
| Pessimista | O CNJ só republica uma parte dos editais das comarcas: não substitui o TJGO. |
| Levemente pessimista | 7 de 8 artigos são de fora de Goiás. |
| **Neutro** | **Fonte certa (a busca do CNJ), já validada com o edital de Itaberaí. Funciona como rede de segurança do motor 07 na nuvem. Prioridade: rodar e gravar o histórico dos artigos. Qualidade: nenhum edital de comarca goiana republicado pelo CNJ fora do painel.** |
| Levemente otimista | Lê na nuvem, sem depender do computador do titular. |
| Otimista | Os valores de outros tribunais (R$ 4,4 milhões no RJ) mostram o tamanho da fonte. |
| Extremamente otimista | Com 3 anos de editais por comarca, a associação antecipa o edital de Goiânia. |
