# Verificação dos 210 editais — relatório final

**Executado em 08/09/2026**, do navegador da máquina do titular (IP residencial, renderização de JavaScript, leitura de PDF e de pacotes .zip).
Entrega: `2026-09-08-eldorado-completo.json` (210 ids) e 14 arquivos de lote em `lotes/`, no formato de `dados/editais/coleta_navegador/`.

## O número que importa

| | Itens |
|---|---|
| Total de ids na base | 210 |
| **Descartados por objeto** (não é fomento a OSC) | **82** |
| **Encerrados, com prazo confirmado em documento** | **80** |
| **ABERTOS nesta data** | **7** |
| Sem prazo verificável na fonte (`null` honesto) | 41 |
| Datas estimadas ou inventadas | **0** |
| Fontes proibidas usadas como `pagina_oficial` | **0** |

Prazo final confirmado em 93 dos 210; início confirmado em 73. A diferença é real e não é falha de leitura: muitos editais municipais só fixam a data-limite de entrega ("até o dia X"), sem abertura.

## Os 7 abertos

| Prazo | id | UF | O que é |
|---|---|---|---|
| **08/09/2026** | `4e5bcf84` | RJ | Chamamento Publico no 001/2026 do Municipio de Arraial do Cabo/RJ (Fundo Municipal de Educacao) - selecao de Organizacao da Sociedade Civil (OSC) para |
| **10/09/2026** | `c341e848` | RJ | Edital de Chamamento Publico da ESCOLA NAVAL (Marinha do Brasil) - Coleta Seletiva Cidada, Decreto 10.936/2022: selecionar associacoes e/ou cooperativ |
| **11/09/2026** | `b810b614` | SP | Chamamento Publico no 022/2026, Edital no 123/2026 do Municipio de Indaiatuba/SP (Secretaria Municipal de Mobilidade Urbana) - selecao de pessoas juri |
| **21/09/2026** | `8c6a2a0e` | RO | Chamamento Publico no 003/PMJ/2026 do Municipio de Jaru/RO (Secretaria Municipal de Agronegocio e Meio Ambiente - SEMEAGRO, processo 16098/PMJ/2025),  |
| **21/09/2026** | `ccf27961` | RO | Chamamento Publico no 003/PMJ/2026 do Municipio de Jaru/RO (Secretaria Municipal de Agronegocio e Meio Ambiente - SEMEAGRO, processo 16098/PMJ/2025),  |
| **30/09/2026** | `0b2e6b2e` | RS | Edital de Chamamento Publico no 13/2026 (Lei 13.019/14) - Termo de Colaboracao para realizacao do projeto 'Oficinas de Danca Tradicionalista', visando |
| **28/10/2026** | `20ec3e11` | RS | Concurso no 01/2026 - selecao de 6 (seis) projetos culturais ineditos na categoria de Arvores Natalinas, propostos por artesaos locais (pessoas fisica |

Dois desses sete são o mesmo edital de Jaru/RO registrado em dois ids (duplicata confirmada). Arraial do Cabo venceu hoje às 10h.

## Verificação independente das datas

Rodei uma checagem automática que procura cada data gravada, no formato do documento (com as variações de espaçamento que o PDF introduz), dentro do texto que foi efetivamente extraído da fonte. Resultado: **72 dos 74 pares de datas conferidos batem literalmente com o documento**.
As duas exceções são erros de digitação do próprio edital, já registrados na observação de cada item:

- `01efd9c4` (Alagoinhas/BA): o edital escreve `14p.11.2024` no item 2.4 — e a tabela de cronograma do mesmo documento diz 15/11. Adotei 14/11 (cláusula normativa + confirmação no metadado) e sinalizei a divergência.
- `376797a4` (Aracaju/SE): o edital escreve `04 de fevereitro de 2026`.

## Divergências encontradas entre o edital e o metadado do PNCP

Em 8 itens o metadado do PNCP contradiz o edital. Em todos, **prevaleceu o edital**, com a divergência anotada. Exemplos:

- `d21ce128` Palmeira dos Índios/AL: PNCP 05/05–29/05/2026; edital 06/05–05/06/2026.
- `11768ed9` Gov. Luiz Rocha/MA: PNCP 05/05–13/05/2026; edital 23/04–29/04/2026.
- `4ff67a8b` Itacaré/BA: PNCP marca 20/01/2025 nas duas pontas; edital 08/11–28/11/2024.
- `0ce9e2de` Dias d'Ávila/BA: PNCP abre e fecha em 04/05/2026; edital 04/05–30/07/2026.
- `248f7907` Horizonte/CE: PNCP 08/05/2024 nas duas pontas; edital 13/03–12/04/2024.

Isso confirma por que a regra de fonte existe: quem tivesse trabalhado só com o metadado do PNCP teria perdido ou errado esses prazos.

## Retificações que mudaram o prazo

Três itens só ficaram corretos porque fui atrás das retificações anexadas ao mesmo registro:

- `c4269137` Bento Gonçalves/RS (LPG Prêmio Trajetórias): cronograma dizia 16/09/2024; a Retificação 2 prorrogou para **19/09/2024 às 16h**.
- `48513973` Lagoa Vermelha/RS (CP 24/2025): recebimento até 03/12/2025; a retificação prorrogou para **19/12/2025**.
- `31b8a937` Nova Russas/CE: recebimento até 24/02/2025; o adendo prorrogou para **06/03/2025**.

## Por que 41 itens ficaram sem prazo

| Causa | Itens |
|---|---|
| PDF anexado é imagem digitalizada sem camada de texto | 9 |
| O próprio edital não traz cronograma (coluna de datas vazia ou ausente) | 11 |
| Documento anexado não corresponde ao objeto registrado | 3 |
| Só o anexo/aviso foi anexado, não o edital | 5 |
| Prazo relativo ("15 dias úteis após a publicação") sem data-base no documento | 2 |
| Formato de arquivo não extraível (.doc binário, .rar, RTF) | 3 |
| Instrumento sem fase de inscrição (termo já celebrado, credenciamento contínuo) | 5 |
| Portal do órgão fora do ar ou sem o edital | 3 |

Nenhum desses 41 recebeu data plausível. O campo vai `null` e a observação diz exatamente qual documento foi lido, quantas páginas, o que faltou e — quando existe — a pista para fechar (o número do processo, o e-mail da secretaria, o metadado do PNCP como referência a conferir).

## Achados de qualidade que valem para a base

- **Duplicatas reais:** 19 ids redundantes em 11 grupos, mais um par novo descoberto na leitura (`725f3091` = `196d0569`, Xanxerê/SC, mesmo concurso). A base tem ~155 unidades reais, não 210.
- **Não são duplicatas, apesar da ementa idêntica:** os pares de Manaus (`c0a95ca4` 001/2026 Audiovisual e `d13f7c2c` 002/2026 Música) e de São José do Rio Preto (`b1ae48b9` 05/2025 Fomento e `e8df77e3` 06/2025 Premiação). Confirmado documento por documento.
- **Janelas materialmente inviáveis**, que valem como argumento em eventual impugnação: Nossa Senhora do Socorro/SE abriu 5 dias de inscrição 3 dias após publicar; Wenceslau Braz/MG publicou no PNCP em 06/11/2024 um edital cujas inscrições fechavam em 07/11; Mirim Doce/SC exigia execução até 25/12/2024 com inscrição encerrando em 06/12.
- **Uma janela ainda aberta por desenho:** Araras/SP (`d745ecf4`) mantém credenciamento por 12 meses a contar da abertura, mesmo depois da data da sessão — vale confirmar com o município.

## Segurança

Nenhuma prompt injection em 210 itens e algumas centenas de PDFs. Nenhum arquivo pediu ação, alegou autorização ou tentou redirecionar a leitura.

## O que fica pendente

Os 41 itens sem prazo não se resolvem com mais navegação: dependem de OCR (9), de pedir o documento ao órgão (13) ou de abrir formato proprietário (3). Os outros 16 são casos em que o próprio edital não publicou cronograma — a resposta correta é `null` e permanecerá `null`.
