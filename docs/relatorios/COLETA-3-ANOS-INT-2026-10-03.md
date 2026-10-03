# Coleta dos 3 anos — livros Internacional (03/10/2026)

Prompt executado: `PROMPT-COLETA-3-ANOS-LIVROS-INT.md`. A fila oficial (`fila_int.json`) não existia nesta cópia do repositório;
foi remontada a partir do catálogo (`biblioteca_alexandria/fontes/motores.json`: livros com geografia Internacional) — 41 livros.
Leitura feita no navegador do titular (IP do Brasil), só páginas oficiais; agregadores serviram para achar a edição.

## Resultado em uma linha
6 livros ganharam edições provadas em página oficial (8 edições); 1 deles (**ICA — Protocolo Luso-Brasileiro**) tem 3 anos seguidos
(2024, 2025, 2026) e passa a **ouro** — mas é um concurso de coprodução de cinema, **não é para OSC**. A maioria dos livros INT
não é chamada para a A.M.C.: é para artistas individuais, para quem tem sede em Portugal/Europa, ou é entidade financiadora sem programa.

## Edições provadas
| Livro | Anos | Datas (página oficial) | Elegível a OSC brasileira? |
|---|---|---|---|
| ICA — Protocolo Luso-Brasileiro de Coprodução | 2024, 2025, 2026 | 03/06–19/09/2024 · 06/05–12/09/2025 · 07/05–30/09/2026 (350.000 €) | Não: produtor minoritário português (lado brasileiro pela ANCINE) |
| Criança Esperança — Edital UNESCO | 2026 | 05/10–08/11/2026 (R$ 150/200/250 mil) | **Sim — público-alvo é OSC brasileira. Abre em 2 dias** |
| Gulbenkian — Apoio à Internacionalização | 2026 (2022 fora da janela) | 12/01–31/10/2026 | Não: sede/domicílio fiscal em Portugal |
| Perform Europe (3ª convocatória) | 2026 | até 22/10/2026 | Não: 41 países do Europa Criativa |
| Camargo Fellowship 2027-28 | 2026 | 01/10 (plataforma) – 05/10/2026 (prorrogado) | Individual (artistas/pesquisadores) |
| Ars Biologica ArtXScience | 2026 | 01/07–28/09/2026 (encerrada) | Individual |

## Achados importantes
1. **Criança Esperança/UNESCO — oportunidade quente:** inscrições abrem 05/10/2026 e fecham 08/11/2026 às 23h59; apoio em 2028;
   Termo de Referência lido por inteiro (19 páginas). A plataforma só mostra a campanha vigente: não há como provar edições 2023-2025 por lá.
2. **3 livros classificados errado como INT:** credenciamentos de Serro (MG), Colombo (PR) e do Estado do RJ (PNCP). Corrigir a geografia.
3. **Livro com endereço inválido:** Institut français × Cité internationale — o domínio registrado não resolve (DNS) em duas tentativas.
4. **Duplicados:** Ars Biologica (2 livros) e Camargo (2 livros) — juntar.
5. **21 livros "captacao-2xx" são entidades** (Gates, Ford, Google.org, BID…), não programas: nenhuma "mesma oportunidade" para medir em 3 anos.
   Abrir livro por programa concreto (ex.: UNESCO IFCD, Erasmus+ por ação). IFCD: página oficial diz que o período 2026 foi encerrado; datas estão na brochura em PDF.
6. **ACNUDH (ONU):** Fundo contra a escravidão contemporânea declara chamada **anual de 15/01 a 01/03** (US$ 15–35 mil) — regime anual provado, sem páginas por ano.

## Limites desta coleta (nada inventado)
- Sem busca na web nesta sessão; achei edições pelo próprio site oficial. Onde o site não guarda arquivo, **não registrei edição**.
- Edições 2023–2025 de Criança Esperança, IFCD, Camargo, Perform Europe, Gulbenkian continuam por provar (onde procurar está em `observacao`).
- `src/selo_livros.py` e a fila oficial não estão nesta cópia: o recálculo dos selos **não foi executado**; o arquivo está pronto para a incorporação.

## Próximas janelas previstas de Internacional (só com base provada)
1. Criança Esperança/UNESCO — 05/10 a 08/11/2026 (aberta em breve)
2. Camargo 2027-28 — encerra 05/10/2026
3. Delfina (PT/PALOP) — 04/10/2026 · IETM Global Connect — 15/10 · Perform Europe — 22/10 · Gulbenkian — 31/10 · EMMA — 02/11 · Schneider — 22/11 · Al-Tiba9 — 30/11
4. ICA Protocolo Luso-Brasileiro — mês típico: maio a setembro (3 anos seguidos) → próxima janela esperada **mai–set/2027**
5. ACNUDH escravidão — 15/01 a 01/03/2027 (regime anual declarado)

## Conselho de 7 lentes
- **Extremamente pessimista:** só 6 de 41 livros têm edição; nenhum livro elegível a OSC chegou a ouro. O "ouro" do ICA é de um programa irrelevante para a A.M.C. e pode enganar o painel.
- **Pessimista:** a fila foi remontada sem o arquivo oficial; pode divergir dos 64 livros do levantamento do selo (aqui são 41).
- **Levemente pessimista:** a extensão do navegador falhou várias vezes e dois domínios não abriram; a cobertura é desigual.
- **Neutro (decide):** incorporar as 8 edições (prova oficial + trecho), marcar elegibilidade em `observacao`, corrigir os 3 livros mal classificados e juntar os duplicados. Parâmetros: ouro só conta para o painel se o livro for elegível a OSC brasileira; meta de 100% dos livros INT com "elegibilidade" registrada. Mitigação: reabrir os 5 programas de edições anteriores por arquivo oficial.
- **Levemente otimista:** o ICA fornece mês típico (mai–set) e confiança média/alta para a próxima janela.
- **Otimista:** o edital Criança Esperança/UNESCO foi lido por inteiro 2 dias antes da abertura, com prazos e valores.
- **Extremamente otimista:** separar "programa" de "entidade" limpa a base INT e abre espaço para livros nominais de programas realmente acessíveis ao Brasil.
