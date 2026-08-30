# Eldorado + Farol de Alexandria

Sistema nacional, auditável e econômico para localizar recursos destinados a organizações da sociedade civil e transformar oportunidades verificadas em decisões, planos de trabalho e trilhas de prestação de contas.

## As duas partes

| Módulo | Função | Resultado |
|---|---|---|
| **Eldorado** | Monitora fontes públicas, privadas e plataformas de editais; deduplica; registra evidências; acompanha cinco anos de histórico por financiador | oportunidades verificadas e dossiês individualizados |
| **Farol de Alexandria** | Aplica requisitos eliminatórios, pontua aderência de cada associação, consulta leis/procedimentos e prepara pacotes de trabalho | ranking explicável, checklist, plano de trabalho e prestação de contas |

As partes usam um identificador imutável de oportunidade, mas não misturam associações. Cada perfil fica em diretório próprio. Somente o perfil institucional saneado pode ser versionado; originais, documentos pessoais e dados privados são ignorados pelo Git porque este repositório é público.

## Operação automática

- Diariamente, às **5h30 de Brasília**, uma sentinela leve detecta fontes alteradas e atualiza a fila sem executar o Farol.
- Às **segundas e quartas, às 6h**, o Eldorado faz a varredura aprofundada desde o último checkpoint, prioriza a fila, percorre páginas catalogadas e registra histórico individual por edital.
- O levantamento de cinco anos é um bootstrap único. Depois do marcador `estado/bootstrap_cinco_anos.json`, ele não volta a executar.
- Mensalmente, hashes das fontes jurídicas oficiais são comparados e uma revisão humana é aberta para vigência, revogação e impacto procedimental.
- Nenhum token de IA é necessário para a coleta, deduplicação, filtros, pontuação ou geração do HTML.
- A IA entra apenas por exportação controlada de um pacote JSON mínimo, pelo botão **Preparar pacote para IA** do painel.

## Segurança e prova

- URLs são restritas a HTTPS e a uma lista de domínios autorizados; endereços locais e privados são bloqueados.
- Cada evidência recebe SHA-256, URL, horário UTC, origem e nível de confiança.
- Conteúdo externo é sempre dado não confiável. Tentativas de prompt injection são colocadas em quarentena e nunca viram instruções.
- Requisitos sem fonte e oportunidades sem URL primária não são tratados como confirmados.
- O sistema não cria valores, prazos, beneficiários ou exigências ausentes na fonte.

## Começar

1. Abra **Actions → 00 · Verificar prontidão → Run workflow**.
2. Em **Settings → Actions → General**, permita leitura e gravação ao workflow.
3. Em **Settings → Pages**, publique a pasta `docs` da branch `main` se desejar o painel público.
4. Crie cada associação com `python scripts/criar_associacao.py SLUG "Nome"`. Cada entidade recebe diretórios exclusivos de conhecimento, documentos, editais, planos, prestações e casos do Farol.
5. Ajuste `config/escopo.json` para escolher UFs, municípios, níveis e áreas. O padrão monitora Goiás/Goiânia, além de fontes federais, privadas nacionais e internacionais compatíveis.
6. Execute o Eldorado localmente: `python -m src.executar_diario`.
7. O Farol é acionado automaticamente apenas após verificação primária/dupla e triagem com possibilidade moderada ou alta. A execução manual continua disponível em `python -m src.executar_farol`.

Para importar DOCX, imagens ou planilhas localmente, instale os componentes opcionais com `pip install -r requirements-importacao.txt`. O monitoramento normal continua usando apenas a biblioteca-padrão do Python.

## Estrutura

```text
config/                       fontes e regras de pontuação
catalogo_captacao/            260 pistas do anexo por nível e tipo
src/                          coleta, normalização, dossiês, matching e painel
dados/oportunidades/          banco JSONL deduplicado
dados/financiadores/          um dossiê por organização financiadora
dados/associacoes/            isolamento estrito por associação
dados/doadores/               empresas e fundações doadoras separadas
biblioteca/leis/              catálogo jurídico e vigência
biblioteca/procedimentos/     procedimentos e checklists reutilizáveis
biblioteca/modelos/           modelos versionados
acervo_importado/             índice verificável do anexo fornecido
docs/                         painel estático e dados filtráveis
estado/                       hashes, cache HTTP e auditoria
```

## Trilha de busca cirúrgica

1. O acervo fornece pistas de programas e formas de captação, sem convertê-las automaticamente em fatos atuais.
2. `config/fontes.json` funciona como lista de permissão: o coletor não segue links para domínios não catalogados. A busca histórica usa `site:dominio_oficial` e também descarta o resultado se o host não coincidir.
3. `config/escopo.json` elimina UFs, municípios e áreas antes de qualquer requisição, economizando banda e tokens.
4. Portais públicos são coletados automaticamente; Goodstack e UN Partner Portal ficam como portais autenticados e não são raspados.
5. A etapa social consulta somente canais previamente identificados em `config/verificacao_social.json` e gera pista secundária.
6. Uma oportunidade só segue ao Farol quando revisada como `verificada_primaria` ou `verificada_dupla`.

O dashboard permite filtrar por UF, nível e área, baixar um novo `escopo.json` e exportar um pacote JSON mínimo para ChatGPT ou Claude.

## Conselho independente do Farol

Cada caso elegível recebe sete pacotes separados, dos pontos de vista extremamente pessimista ao extremamente otimista. As personalidades brasileiras são sorteadas entre lentes relevantes à área e não repetem a mesma posição na rodada seguinte. Elas são simulações metodológicas, não opiniões reais.

O parecer final permanece bloqueado até existirem sete respostas JSON válidas. O modelo usado é definido externamente por `FAROL_FINAL_MODEL`; nenhuma versão comercial é presumida no código. Sem credencial autorizada, o sistema prepara os pacotes, plano integral em rascunho, manual do presidente, documentos faltantes e matriz de prestação de contas, mas não simula que uma IA externa foi executada.

## Associação inicial

`dados/associacoes/amc-jardim-america/` contém o perfil público sanitizado da A.M.C., capacidades, indicadores, projetos/eventos e o índice compacto do DOCX anexado. O arquivo original tem dados pessoais e 17 imagens; por segurança, foram publicados apenas texto e tabelas compactados com PII removida e manifestos de hash das imagens.

Consulte também [ARQUITETURA.md](ARQUITETURA.md), [SEGURANCA.md](SEGURANCA.md) e [OPERACAO.md](OPERACAO.md).
