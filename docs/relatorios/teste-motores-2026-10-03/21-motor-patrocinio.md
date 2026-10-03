# Motor 21 — Patrocínio Privado: mídia e eventos de Goiás (`motor-patrocinio`)

**Veredito:** workflow FUNCIONANDO (semanal, aos domingos) · coleta PARCIAL (lê agendas de jornais) · resultado
**FALHA: as 3 "empresas" são falsos positivos** · histórico de 3 anos FALHA.

## Workflow

- **Agenda:** aos domingos, às 03:23, a cada 7 dias, na nuvem. Roda no mesmo passo do motor 20 (`src.patrocinios`).
  O teste `tests/test_prospeccao.py` passa.
- **Última leitura:** 29/09, às 00:20. A luz é cinza "fora da agenda", o que é correto.

## Onde coleta

- **Imprensa:** Jornal Opção (agenda), Diário de Goiás (cultura), O Popular e outros. O leitor procura termos como
  "apoio", "patrocínio", "realização" e "apresenta" perto de nomes próprios.
- **Sites de eventos culturais do Estado**, descobertos e verificados: Canto da Primavera, Mostra TeNpo, Semana Santa
  em Goiás.

## Resultado

**Os 3 achados são todos falsos positivos:**

| "Empresa" registrada | O que é de fato |
|---|---|
| "WhatsApp Agenda Grupo" | trecho de agenda ("inscrições… por WhatsApp", "Agenda Grupo Rooftime se apresenta") |
| "Diário de Goiás Comunicação LTDA" | o próprio jornal (rodapé), num trecho sobre a Semana da Pátria |
| "Prefeitura de Aparecida e Instituto" | ente público e concurso público, não patrocínio privado |

O painel mostrou "3 empresas mapeadas", e nenhuma é patrocinadora.

## Histórico de 3 anos

- **Nenhum registro válido.**
- **Recuperação possível:** os sites de eventos verificados (Canto da Primavera, TeNpo e outros) têm edições anuais com
  as marcas patrocinadoras. Ler as edições de 2023 a 2026 desses eventos dá patrocinadores reais, com ano e área.

## Correções, por prioridade

1. **Trocar a fonte principal:** sair do texto corrido de agenda de jornal e ir para as **páginas de patrocinadores e
   realização dos eventos** (rodapé com marcas e a lista "patrocínio/apoio"), começando pelos sites de eventos já
   verificados.
2. **Validar a empresa antes de gravar:** exigir CNPJ ou site oficial e vetar o próprio veículo, ente público,
   aplicativo ("WhatsApp") e trecho de agenda.
3. **Carga de 3 anos** das edições anuais dos eventos de Goiás, com patrocinadores por ano.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | 100% de falso positivo. Se alguém usar essa lista para pedir patrocínio, o resultado é constrangedor. |
| Pessimista | Ler agenda de jornal por palavra-chave não identifica empresa. |
| Levemente pessimista | Sem validação de CNPJ, qualquer nome próprio vira "empresa". |
| **Neutro** | **O objetivo é bom (quem patrocina eventos em Goiás), mas o método atual não serve. Prioridade: fonte nas páginas de patrocinadores dos eventos e validação por CNPJ ou site. Até lá, ocultar a lista do painel. Meta: 0 falso positivo.** |
| Levemente otimista | Os sites de eventos do Estado já foram descobertos e verificados: a fonte certa está à mão. |
| Otimista | Patrocínio privado com recurso próprio não depende de janela de edital. |
| Extremamente otimista | Com 3 anos de patrocinadores por evento, a associação pede patrocínio para eventos do bairro às marcas que já apoiam o tema. |
