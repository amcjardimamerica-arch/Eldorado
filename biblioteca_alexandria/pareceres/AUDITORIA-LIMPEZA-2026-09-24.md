# Auditoria de limpeza — sem dado de teste, sem benchmark, sem o que não tem uso · 24/09/2026

## 1. O que saiu

**Benchmark e banco de provas (dados e código)**
- `dados/conjunto-de-avaliacao-motor.json`
- `estado/piloto/avaliacao-qwen3-1.7b-2026-09-23.json`
- `estado/piloto/benchmark-1-2026-09-21.json`
- `estado/piloto/benchmark.json`
- `estado/piloto/trilha_do_cargo.json`
- `estado/piloto/voo_observado_2026-09-23.json`
- `scripts/trilha_do_cargo.py`
- `scripts/voo_observado.py`
- `tests/test_trilha_do_cargo.py`
- `tests/test_voo_observado.py`
- `scripts/aplicar_leituras_locais_23_09.py`
- `scripts/aplicar_parecer_23_09.py`
- `scripts/aprimorar_fontes_2026_09.py`
- `scripts/aprimorar_fontes_goias.py`
- `scripts/parecer_afiacao.py`
- `src/biblioteca_empresas.py`
- `src/parametros_oportunidades.py`

**Modos do workflow do Piloto:** `benchmark`, `avaliar` e `trilha do cargo` saíram; o download baixa só o ocupante.
As funções `gabarito`, `avaliar_modelo` e `benchmark` saíram de `src/piloto.py`, e `avaliar` de `src/cargo_piloto.py`.
Os testes que só existiam para eles saíram; os demais foram alinhados.

**Dados de teste que voltaram e por onde voltavam**
- **14.906 fichas de edição do Querido Diário** (234 MB), apagadas ontem, foram recriadas às 12h37 pela varredura: a
  Biblioteca é reconstruída a cada varredura a partir dos registros-fonte, e eu havia apagado só as fichas. Fechado na
  origem — o reconstrutor pula edição de diário (ela vive no índice `dados/editais/indice_diarios.json`). Biblioteca: 734 fichas.
- **141 avaliações e 2 lições de motores de ensaio** voltaram à base de aprendizados; removidas de novo. A barreira
  `_e_ensaio` impede registro novo.
- **27 empresas fictícias** voltaram ao radar por execução antiga; radar em 4 empresas reais. A barreira por domínio de ensaio
  (`config/dominios_de_ensaio.json`) impede que voltem por qualquer caminho — inclusive pelo meu próprio teste de hoje,
  que registrou "Instituto Ethos" num domínio de exemplo e foi desfeito; o domínio entrou na lista.

## 2. O que ficou de propósito, e por quê

| item | por quê fica |
|---|---|
| `estado/piloto/erro_do_voo.json` | diagnóstico real do último voo que quebrou; sem ele o log do Actions é ilegível de fora |
| `estado/piloto/sondagem_gguf.tsv` e o modo `sondar` | medição real dos endereços dos modelos (HTTP e tamanho); foi o que achou o 404 do Qwen3 |
| `config/dominios_de_ensaio.json`, `_e_ensaio`, `LAB_PROIBIDO` | barreiras: dado de ensaio nunca entra, por onde quer que venha |
| `tests/` | testes automatizados são do sistema; guardam as regras, não são dados de teste |
| `dados/verificacao/parecer_2026-09-23/` | gabarito do titular: acertos e erros reais contra os quais o PNCP é medido |

## 3. Regra nova do Piloto, em vigor

**Primeiro o resgate** de oportunidades publicadas nos **últimos 30 dias** (item sem data de publicação não conta como
resgate dos 30 dias). **Não havendo o que resgatar**, o voo vai aos **sites especializados do terceiro setor e de entidades**
(`config/sites_terceiro_setor.json`, 16 sementes: Observatório do 3º Setor, ABCR, GIFE, Prosas, Plataforma MROSC, IDIS,
Ethos, Pacto Global, Movimento Bem Maior, Rede Filantropia, Parceiros Voluntários, Itaú Social, Instituto Fonte, Captamos,
OVG, Instituto Cultural Vale) e cataloga, em `estado/piloto/catalogo_terceiro_setor.json`: as **páginas voltadas a entidades**
(editais, parcerias, apoio, inscrições), as **empresas que aparecem** como apoiadoras ou patrocinadoras — que seguem para
o radar e daí para a lista de empresas — e se o site **declara ESG**. Um site lido hoje só volta ao plano em 7 dias. Cada
site novo descoberto entra no rodízio. As missões de "descobrir fonte local" e "caçar por motor", que renderam zero em 52 de 52
hoje, saem do plano: as vagas são do resgate e do catálogo.
