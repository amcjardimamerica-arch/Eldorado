# Arranque no Claude Desktop — sessão única que navega, lê e grava

Objetivo: fechar as informações mínimas (objeto, prazo de inscrição e página oficial do edital) de
todas as oportunidades da fila, sem o titular tocar em GitHub ou terminal.

## Preparação (uma vez, 5 minutos)
1. Abra o Claude Desktop e entre com a sua conta.
2. Aba **Cowork** → **Nova tarefa** (ou nova conversa de Cowork).
3. Quando ele pedir, autorize: acesso a **arquivos** (escolha uma pasta, por exemplo Documentos) e
   ao **navegador** (Claude para Chrome). É isso que permite abrir sites e salvar arquivos.
4. Cole o PROMPT DE ARRANQUE abaixo. Se pedir login do GitHub, faça no navegador que abrir —
   a partir daí ele reaproveita a sessão.

## PROMPT DE ARRANQUE (cole no Cowork)

> Você é o agente do sistema Eldorado / Farol de Alexandria. Trabalhe sozinho e me dê um resumo no fim.
>
> **Preparar**: clone https://github.com/amcjardimamerica-arch/Eldorado numa pasta local (se já existir, `git pull`).
> Instale o necessário com `pip install -r requirements.txt`.
>
> **Descobrir o que falta**: rode `python -m src.enquadramento fila` e abra `estado/fila_verificacao.json`.
> Trabalhe primeiro os itens com `"modo": "completo"` (nacionais e Goiás) cujo `minimas.faltam` não esteja vazio.
>
> **Completar, um a um (faça 20 por vez)**: para cada item, abra no navegador a página do órgão ou do
> patrocinador — NUNCA PNCP, Querido Diário, Diário Oficial ou portais de notícia (Observatório do
> Terceiro Setor, Captadores/ABCR); se o `link_oficial` for de um desses, procure no Google o nome do
> financiador + "edital" e entre no site dele. Localize o edital, abra o PDF e extraia: OBJETO (frase do
> item "DO OBJETO"), PRAZO DE INSCRIÇÃO (início e fim) e a URL DA PÁGINA OFICIAL. Se não for edital
> (notícia, podcast, pesquisa), se o site não abrir ou se o prazo não constar, escreva isso — não invente datas.
>
> **Gravar**: salve tudo em `dados/editais/coleta_navegador/<data>.json` no formato
> `{"<id>": {"objeto": "...", "inicio": "AAAA-MM-DD ou null", "fim": "AAAA-MM-DD ou null", "pagina_oficial": "https://...", "observacao": "..."}}`
> e rode `python -m src.enquadramento ingerir_navegador`.
>
> **Fechar o ciclo**: `python -m src.enquadramento` ; `python -m src.enquadramento fila` ; `python -m src.dashboard_dados` ;
> `python -m unittest tests.test_system` (só siga com tudo verde) ; `python scripts/verificar_privacidade.py` ;
> `git add -A` ; `git commit -m "coleta pelo navegador <data>"` ; `git pull --rebase origin main` ; `git push`.
>
> **Extra, se sobrar tempo**: rode `python scripts/coleta_brasil.py` — ele lê, com o seu IP brasileiro, os portais
> goianos que o robô do GitHub não alcança (TJGO, Câmara e Prefeitura de Goiânia, goias.gov.br, MPGO).
>
> **Resumo final**: quantos itens completados, quantos não eram editais, quantos sites não abriram e o que ficou para mim decidir.

## Repetir toda semana sem digitar
No Cowork, **Tarefas agendadas** → nova tarefa → domingo, 05h → cole o mesmo prompt.
