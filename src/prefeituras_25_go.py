"""MOTOR 08 v2 — OPORTUNIDADES DAS 25 MAIORES PREFEITURAS DE GOIÁS (titular, 02/10/2026).

ARQUIVO ÚNICO DE IMPLANTAÇÃO. Substitui a leitura antiga do sensor `plat-prefeituras-50-go` (19 leituras, 0 achados,
painel "azul" falso: só lia a home de Goiânia, a home do Querido Diário e a home do PNCP). O PNCP continua no motor
próprio (04). Aqui a consulta é DIRETA aos locais onde cada cidade publica:

  ROTA A · DIÁRIO AGM (diariomunicipal.com.br/agm, SIGPub)  — 6 cidades num leitor só (Águas Lindas, Cristalina, Formosa,
           Inhumas, Senador Canedo, Trindade). É onde aparecem os termos de fomento e convênios de subvenção que o site
           não mostra (Inhumas: 34 fomentos em 2025-26; Formosa: 15 subvenções).
  ROTA B · SITE OFICIAL (API do WordPress /wp-json/wp/v2)     — 21 cidades, posts e páginas, 14 termos, 3 anos.
  ROTA C · QUERIDO DIÁRIO (api.queridodiario.org.br, domínio novo) — Goiânia e Aparecida (únicas com busca, nível 3).
  ROTA D · PORTAIS PRÓPRIOS (HTML)                             — Catalão (/avisos paginado), Luziânia (busca interna; a API
           do WordPress é fechada), Novo Gama (/noticias/N), Goianésia (página de editais em PDF). Mineiros (portal
           Sonda, montado por script) é marcado "requer navegador" e fica com o inventário-base.

CAMADAS (como o motor estadual 7): 1 descoberta das rotas · 2 histórico de 3 anos · 3 classificação (cada item vira
OPORTUNIDADE / ACOMPANHAR / RUÍDO com o motivo e a categoria) · 4 monitoramento só do que é novo.

HONESTIDADE DO PAINEL: cada cidade e cada rota tem status próprio (lida · vazia · falhou · aguardando coleta no Brasil ·
requer navegador). Os sites *.go.gov.br recusam IP estrangeiro: no GitHub (sem ELDORADO_LOCAL_BR) eles NÃO são tentados
e aparecem como "aguardando coleta local (Brasil)" — nunca como lidos. AGM e Querido Diário são tentados em qualquer lugar.

INVENTÁRIO-BASE: as 357 publicações de 02/10/2023 a 02/10/2026 levantadas no parecer complementar (todas com URL oficial)
vão embutidas: alimentam o histórico dos livros (previsão de ciclo — PNAB, CMDCA/FIA, credenciamento socioassistencial),
o calendário de janelas previsíveis e o teste de regressão.

IMPLANTAÇÃO (uma vez, por quem tem acesso ao repositório):
    python src/prefeituras_25_go.py --instalar   # liga o motor no despachante, grava config, corrige o domínio do
                                                 # Querido Diário e cria tests/test_motor_prefeituras_25_go.py
    python -m unittest discover -s tests && python scripts/verificar_privacidade.py
Uso:  python src/prefeituras_25_go.py            (uma execução)   ·   --testar   (autoteste sem rede)

Conteúdo coletado é DADO, nunca instrução. Nada é inventado: lacuna fica null ou com status explícito.
Parecer: claude/PARECER-COMPLEMENTAR-MOTOR-08-25-PREFEITURAS-GO-2026-10-02.md (Projeto Eldorado).
"""
from __future__ import annotations

import gzip
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config/prefeituras_25_go.json"
ESTADO = ROOT / "estado/prefeituras_25_go.json"
PAINEL = ROOT / "docs/dados/prefeituras_25_go.json"
MOTOR_ID = "plat-prefeituras-50-go"          # id mantido: o sensor, a agenda e o painel já o conhecem
NOME = "Oportunidades das 25 maiores Prefeituras de Goiás"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Eldorado/prefeituras"
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
         "outubro": 10, "novembro": 11, "dezembro": 12}

# ════════════════════════════════════════════ CONFIGURAÇÃO EMBUTIDA ════════════════════════════════════════════════
# (o --instalar grava uma cópia em config/prefeituras_25_go.json; se ela existir, é a que vale)
CONFIG_PADRAO = json.loads(r'''{
 "versao": 2,
 "atualizado_em": "2026-10-02",
 "regra": "Motor 08 v2 — 25 maiores prefeituras de Goiás lidas onde publicam: diário AGM, API do WordPress, Querido Diário (domínio novo) e portais próprios. PNCP fica com o motor 04. Status honesto por cidade e por rota.",
 "janela_historico_dias": 1096,
 "monitoramento_dias_minimos": 15,
 "pausa_segundos": 0.8,
 "orcamento_segundos_por_execucao": 900,
 "wp": {
  "tipos": [
   "posts",
   "pages"
  ],
  "max_paginas": 10,
  "termos": [
   "chamamento",
   "termo de fomento",
   "termo de colaboração",
   "sociedade civil",
   "Aldir Blanc",
   "PNAB",
   "Paulo Gustavo",
   "CMDCA",
   "subvenção",
   "emenda parlamentar",
   "edital",
   "inexigibilidade",
   "seleção de projetos",
   "fundo municipal"
  ]
 },
 "agm": {
  "url": "https://www.diariomunicipal.com.br/agm/pesquisar",
  "por_pagina": 25,
  "max_paginas": 12,
  "termos": [
   "chamamento público",
   "termo de fomento",
   "termo de colaboração",
   "organização da sociedade civil",
   "seleção de projetos",
   "Aldir Blanc",
   "Paulo Gustavo",
   "CMDCA",
   "subvenção",
   "inexigibilidade de chamamento",
   "emenda parlamentar"
  ]
 },
 "querido_diario": {
  "api": "https://api.queridodiario.org.br",
  "max_por_termo": 1000,
  "termos": [
   "\"chamamento público\"",
   "\"termo de fomento\"",
   "\"termo de colaboração\"",
   "\"organização da sociedade civil\"",
   "\"Aldir Blanc\"",
   "CMDCA"
  ],
  "nota": "domínio antigo api.queridodiario.ok.org.br falha (TLS); em 02/10/2026 a API oscilou (tempo esgotado) — o motor marca 'falhou' e tenta de novo na próxima"
 },
 "lexico": {
  "osc_forte": "organizac\\w* da sociedade civil|\\boscs?\\b|termos? de (fomento|colaboracao)|contrato de fomento|mrosc|13\\.019|sem fins lucrativos|entidades? (socioassistencia|filantropic|sem fins|nao governamenta|assistencia)|terceiro setor|organizac\\w* socia",
  "osc": "entidade|associac|instituic\\w* (privad|sem|de longa)|aldir blanc|\\bpnab\\b|paulo gustavo|lei (municipal )?de incentivo|fundo municipal|projetos? (culturais|sociais|esportivos|socioambientais|literarios)|agentes? culturais|ponto(s|es)? de cultura|cultura viva|cmdca|\\bfia\\b|fmdca|crianca|adolescente|idosos|longa permanencia|casa.lar|credenciamento social|socioassistencia|premi\\w* (para|de|por)|chamamento publico|chamada publica|fomento|cultura|cultural",
  "abertura": "chamament|chamada publica|\\bchamada\\b|edital|editais|selecao|seleciona|credenciamento|inscric|premio|premiacao|abre |lanca",
  "resultado": "^resultado|resultado (final|preliminar|definitivo|da|do|dos|pos)|homolog|habilitad|habilitac|classificad|classificac|selecionad|contemplad|lista (de|final|preliminar|dos)|aprovad|inscritos|deferid|julgamento|^ata\\b|ata (da|de)|pagamento(s)? aos|recursos .*(ja estao|chegam)|analise de merito|propostas recebidas|indeferimento",
  "ato_do_edital": "retifica|errata|prorroga|adiad|adiamento|revoga|suspens|cronograma|esclareciment|aditivo ao edital|termo aditivo ao edital|convocac\\w* de suplentes|suplentes",
  "parceria": "^extrato|extrato d|inexigibilidade|dispensa de chamamento|termos? de (fomento|colaboracao|execucao cultural|convenio|subvencao|parceria)\\b|contrato de fomento|^convenio|subvenc|apostilamento|aditamento|aditivo ao termo|repass|celebra|firma|entrega de (van|veiculo)|incentivo financeiro|apoio financeiro|^c o n v",
  "conselho": "conselh\\w* municipa|representantes da sociedade civil|eleicao|composicao d|conselheir|forum municipal|conferencia|recomposicao",
  "cultura": "aldir blanc|\\bpnab\\b|paulo gustavo|cultur|audiovisual|artist|ponto(s|es)? de cultura|lei (municipal )?de incentivo|patrimonio|literari|\\blpg\\b",
  "crianca": "cmdca|\\bfia\\b|fmdca|crianca|adolescente",
  "agricultura": "agricultura familiar|\\bpaa\\b|\\bpnae\\b|aquisicao de (generos )?aliment",
  "acompanhar": "resoluc|fundo municipal|emenda|plano (anual )?de aplicacao|consulta publica|audiencia publica|regulament|\\blei n|programa|adesao",
  "dias_aberta_sem_prazo": 45,
  "vetos": [
   [
    "seleção ou convocação de pessoal",
    "concurso|processo seletivo|\\bpss\\b|convocac\\w* (de|dos|para) (candidat|aprovad|apresentac|concursad)|nomeac|analistas|pedagog|professor|educador social voluntario|estagi|aptidao fisica|guarda civil|concursados|assistente social escolar|pareceristas|bancas? tecnicas?",
    false
   ],
   [
    "matrícula e vagas escolares",
    "chamada publica (escolar|infantil|da educacao)|matricula|educacao infantil|novos alunos|ingresso na rede|escola (municipal )?de (linguas|musica)|\\beja\\b|periodo integral",
    false
   ],
   [
    "saúde pública geral",
    "vacin|febre amarela|dengue",
    false
   ],
   [
    "conselho tutelar",
    "conselh\\w* tutelar",
    false
   ],
   [
    "leilão, notificação ou tributo",
    "leilao|notificac|intimac|iptu|tribut|lancamento fiscal|divida ativa|refis",
    false
   ],
   [
    "compra ou contratação comum",
    "pregao|registro de precos|combustivel|aquisicao de (?!generos aliment)|contratacao de empresa|ordem de fornecimento|locacao|manutencao predial",
    true
   ],
   [
    "ocupação comercial de evento",
    "festival gastronomic|praca de alimentacao|ocupacao de espacos|ambulante|feira (livre|de artesanato)|atividades comerciais|expotrin|som automotivo|milholandia|festival de sabores",
    false
   ],
   [
    "prêmio recebido pela prefeitura ou servidores",
    "(recebe|conquista|ganha|vence|destaque|finalista|premiad|homenage|reconhecid)\\w*.{0,60}premi|premio (da qualidade|leia|selo|funcionario|goias sustentavel|espirito publico)|selo (ouro|de referencia)|premiacoes de destaque|licenca premio|cerimonia de premiacao|premio buritis|premio brb",
    false
   ],
   [
    "habitação e regularização fundiária",
    "habitac|sorteio|regularizacao fundiaria|custo zero|unidades habitaciona|pro moradia|moradia|loteamento",
    true
   ],
   [
    "transporte e mobilidade",
    "transporte (coletivo|publico)|bicicletas compartilhad|mototaxi|\\btaxi\\b",
    false
   ],
   [
    "chamamento de empresas, patrocínio ou publicidade",
    "construtor|empresas|loteric|patrocini|influenciador|publicidade|subcomissao tecnica|capital social|restos a pagar|juro zero|manifestacao de interesse|\\bpmi\\b|cemiterio|telemedicina|clinicas de psicologia|profissionais (psicologos|habilitados)",
    true
   ],
   [
    "doação de bens ou uso de espaço público",
    "doacao de bens|permissao de uso|bens moveis|inserviv|patrulhas agricolas|lago bonsucesso|parque natural",
    false
   ],
   [
    "corrida e esporte de rendimento sem entidade",
    "corrida|campeonato|torneio|atletas",
    true
   ]
  ]
 },
 "municipios": [
  {"municipio": "Goiânia", "ibge": "5208707", "site": "https://www.goiania.go.gov.br", "wp_api": true, "diario": "Diário Oficial do Município – www.goiania.go.gov.br/casa-civil/ (também no Querido Diário, nível 3, desde 2020-11-24)", "transparencia": "www.goiania.go.gov.br/sing_transparencia/licitacoes", "agm": null, "qd": "5208707"},
  {"municipio": "Aparecida de Goiânia", "ibge": "5201405", "site": "https://aparecida.go.gov.br", "wp_api": true, "diario": "doe.aparecida.go.gov.br (Querido Diário nível 3 desde 2022-10-04)", "transparencia": "acessoainformacao.aparecida.go.gov.br ; transparencia.aparecida.go.gov.br/licitacoes", "agm": null, "qd": "5201405"},
  {"municipio": "Anápolis", "ibge": "5201108", "site": "https://www.anapolis.go.gov.br", "wp_api": true, "diario": "dom.anapolis.go.gov.br", "paginas_editais": ["/publicacao-de-editais/", "/espacocultural/"], "agm": null, "portal": {"modo": "pagina_editais", "paginas": ["publicacao-de-editais/"]}, "qd": null},
  {"municipio": "Rio Verde", "ibge": "5218805", "site": "https://www.rioverde.go.gov.br", "wp_api": true, "diario": null, "paginas_editais": ["/editais-e-downloads/"], "transparencia": "acessoainformacao.rioverde.go.gov.br/informacao/licitacoes", "agm": null, "portal": {"modo": "pagina_editais", "paginas": ["editais-e-downloads/"]}, "qd": null},
  {"municipio": "Águas Lindas de Goiás", "ibge": "5200258", "site": "https://aguaslindasdegoias.go.gov.br", "wp_api": true, "diario": "AGM + acessoainformacao.aguaslindasdegoias.go.gov.br/cidadao/atos_adm/mp/id=26", "paginas_editais": ["acessoainformacao…/cidadao/atos_adm/mp/id=23"], "agm": "44796", "qd": null},
  {"municipio": "Luziânia", "ibge": "5212501", "site": "https://www.luziania.go.gov.br", "wp_api": false, "nota": "API WordPress fechada (401): usar busca interna /?s= e tabelas", "paginas_editais": ["/tabela-editais/", "/tabela-termos/", "/editaismunicipais", "/editaismunicipais2/"], "agm": null, "portal": {"modo": "busca_wp_html", "termos": ["chamamento", "termo de fomento", "termo de colaboração", "sociedade civil", "aldir blanc", "paulo gustavo", "cmdca", "subvenção"], "max_paginas": 6}, "qd": null},
  {"municipio": "Valparaíso de Goiás", "ibge": "5221858", "site": "https://www.valparaisodegoias.go.gov.br", "wp_api": true, "diario": "diariooficial.valparaisodegoias.go.gov.br", "paginas_editais": ["acessoainformacao.valparaisodegoias.go.gov.br/cidadao/atos_adm/mp/id=3"], "agm": null, "qd": null},
  {"municipio": "Trindade", "ibge": "5221403", "site": "https://www.trindade.go.gov.br", "wp_api": true, "diario": "AGM", "transparencia": "acessoainformacao.trindade.go.gov.br", "agm": "51721", "qd": null},
  {"municipio": "Formosa", "ibge": "5208004", "site": "https://www.formosa.go.gov.br", "wp_api": true, "diario": "AGM", "transparencia": "acessoainformacao.formosa.go.gov.br", "agm": "14263", "qd": null},
  {"municipio": "Novo Gama", "ibge": "5215231", "site": "https://www.novogama.go.gov.br", "wp_api": false, "nota": "portal próprio (/noticia/NNNN-…), sem WordPress; responder só do Brasil", "transparencia": "acessoainformacao.novogama.go.gov.br", "agm": null, "portal": {"modo": "noticias_paginado", "max_paginas": 260}, "qd": null},
  {"municipio": "Senador Canedo", "ibge": "5220454", "site": "https://www.senadorcanedo.go.gov.br", "wp_api": true, "diario": "diario.senadorcanedo.go.gov.br + AGM", "transparencia": "acessoainformacao.senadorcanedo.go.gov.br/cidadao/informacao/licitacoes", "agm": "4445", "qd": null},
  {"municipio": "Itumbiara", "ibge": "5211503", "site": "https://www.itumbiara.go.gov.br", "wp_api": true, "diario": "acessoainformacao.itumbiara.go.gov.br/cidadao/outras_informacoes/mp/id=5", "agm": null, "qd": null},
  {"municipio": "Catalão", "ibge": "5205109", "site": "https://www.catalao.go.gov.br", "wp_api": false, "nota": "portal próprio; listas paginadas ?page=N", "paginas_editais": ["/avisos/edital-de-chamamento-publico", "/avisos/termo-fomento", "/avisos/termo-de-convenio", "/avisos/comunicados"], "transparencia": "/transparencia/documentos/licitacao", "agm": null, "portal": {"modo": "avisos_paginado", "secoes": ["avisos/edital-de-chamamento-publico", "avisos/termo-fomento", "avisos/termo-de-convenio"], "max_paginas": 15}, "qd": null},
  {"municipio": "Jataí", "ibge": "5211909", "site": "https://www.jatai.go.gov.br", "wp_api": true, "diario": "intranet.jatai.go.gov.br/intranet/sistemas/diario-oficial/diario-site.php", "transparencia": "jatai.sigep.com.br", "agm": null, "qd": null},
  {"municipio": "Planaltina", "ibge": null, "site": "https://www.planaltina.go.gov.br", "wp_api": true, "transparencia": "acessoainformacao.planaltina.go.gov.br/cidadao/informacao/licitacoes", "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null},
  {"municipio": "Caldas Novas", "ibge": "5204508", "site": "https://www.caldasnovas.go.gov.br", "wp_api": true, "diario": "caldasnovas.integrame.app.br/app/", "transparencia": "www.caldasnovas.go.gov.br/licitacao/ ; acessoainformacao.caldasnovas.go.gov.br/informacao/mp/id=27", "agm": null, "qd": null},
  {"municipio": "Santo Antônio do Descoberto", "ibge": null, "site": "https://www.santoantoniododescoberto.go.gov.br", "wp_api": true, "diario": "/diario-oficial/", "transparencia": "acessoainformacao.santoantoniododescoberto.go.gov.br/cidadao/informacao/licitacoes", "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null},
  {"municipio": "Goianésia", "ibge": null, "site": "https://www.goianesia.go.gov.br", "wp_api": true, "paginas_editais": ["/editais-e-publicacoes/"], "transparencia": "acessoainformacao.goianesia.go.gov.br/cidadao/informacao/licitacoes", "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "portal": {"modo": "pagina_editais", "paginas": ["editais-e-publicacoes/"]}, "qd": null},
  {"municipio": "Cidade Ocidental", "ibge": "5205497", "site": "https://cidadeocidental.go.gov.br", "wp_api": true, "transparencia": "acessoainformacao.cidadeocidental.go.gov.br/cidadao/informacao/licitacoes", "agm": null, "qd": null},
  {"municipio": "Mineiros", "ibge": null, "site": "https://www.mineiros.go.gov.br", "wp_api": false, "nota": "portal próprio, sem WordPress", "paginas_editais": ["/acesso-a-informacao/bids", "/acesso-a-informacao/atos-de-inexigibilidade", "/acesso-a-informacao/atos-de-dispensa"], "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "portal": {"modo": "requer_navegador", "paginas": ["acesso-a-informacao/apoio-financeiro", "acesso-a-informacao/convenios", "acesso-a-informacao/credenciamentos"], "nota": "portal Sonda montado por script: PROCACES (apoio financeiro a projetos culturais, esportivos e sociais, fluxo contínuo) e convênios"}, "qd": null},
  {"municipio": "Cristalina", "ibge": null, "site": "https://cristalina.go.gov.br", "wp_api": true, "diario": "AGM", "transparencia": "acessoainformacao.cristalina.go.gov.br/cidadao/informacao/licitacoes", "agm": "46421", "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null},
  {"municipio": "Inhumas", "ibge": null, "site": "https://www.inhumas.go.gov.br", "wp_api": true, "diario": "AGM", "transparencia": "acessoainformacao.inhumas.go.gov.br/cidadao/informacao/licitacoes_cnt", "agm": "28352", "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null},
  {"municipio": "Itaberaí", "ibge": null, "site": "https://www.itaberai.go.gov.br", "wp_api": true, "paginas_editais": ["/aviso/"], "transparencia": "acessoainformacao.itaberai.go.gov.br/cidadao/informacao/licitacoes", "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null},
  {"municipio": "Jaraguá", "ibge": null, "site": "https://www.jaragua.go.gov.br", "wp_api": true, "transparencia": "acessoainformacao.jaragua.go.gov.br/cidadao/informacao/licitacoes", "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null},
  {"municipio": "Quirinópolis", "ibge": null, "site": "https://www.quirinopolis.go.gov.br", "wp_api": true, "transparencia": "acessoainformacao.quirinopolis.go.gov.br/cidadao/informacao/licitacoes_cnt", "agm": null, "ibge_pendente": "confirmar no IBGE antes de usar", "qd": null}
 ]
}''')

# ═══════════════════════════════ INVENTÁRIO-BASE (02/10/2023 → 02/10/2026, 357 itens) ═══════════════════════════════
# colunas: municipio, data (AAAA-MM-DD; "AAAA" quando o portal não data o ato; "s/d" sem data), fonte, categoria, titulo, url
INVENTARIO_BASE = json.loads(r'''[
["Anápolis", "2026-09-14", "Site municipal (WordPress)", "ACOMPANHAR", "Anápolis regulamenta fomento à cultura e amplia incentivo aos artistas locais", "https://www.anapolis.go.gov.br/anapolis-regulamenta-fomento-a-cultura-e-amplia-incentivo-aos-artistas-locais/"],
["Anápolis", "2026-07-20", "Site municipal (WordPress)", "ATO_DO_EDITAL", "Prorrogação das inscrições dos editais da PNAB até 26/07", "https://www.anapolis.go.gov.br/prefeitura-de-anapolis-prorroga-inscricoes-dos-editais-da-politica-nacional-aldir-blanc-ate-26-de-julho/"],
["Anápolis", "2026-06-16", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Prefeitura lança editais da Lei Aldir Blanc para o setor cultural", "https://www.anapolis.go.gov.br/prefeitura-de-anapolis-lanca-editais-da-lei-aldir-blanc-para-o-setor-cultural/"],
["Anápolis", "2025-09-02", "Site municipal (WordPress)", "ACOMPANHAR", "Anápolis garante mais de R$ 2,5 milhões para a Cultura com adesão à PNAB", "https://www.anapolis.go.gov.br/anapolis-garante-mais-de-r-25-milhoes-para-a-cultura-com-adesao-a-politica-nacional-aldir-blanc/"],
["Anápolis", "2025-08-15", "Site municipal (WordPress)", "ACOMPANHAR", "Criação do Fundo Municipal de Esportes", "https://www.anapolis.go.gov.br/prefeitura-de-anapolis-cria-fundo-municipal-de-esportes-para-organizar-e-ampliar-investimentos-no-setor/"],
["Anápolis", "2024-05-15", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Fundo Municipal de Cultura recebe inscrições até domingo (19)", "https://www.anapolis.go.gov.br/fundo-municipal-de-cultura-recebe-inscricoes-ate-domingo-19/"],
["Anápolis", "2024-03-18", "Site municipal (WordPress)", "ACOMPANHAR", "Destinação do IR ao Fundo Municipal para a Infância e Adolescência", "https://www.anapolis.go.gov.br/parte-do-imposto-de-renda-pode-ser-destinada-ao-fundo-municipal-para-a-infancia-e-adolescencia/"],
["Anápolis", "2024-03-13", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Fundo Municipal de Cultura 2023/2024 vai investir mais de R$ 2 milhões em projetos culturais", "https://www.anapolis.go.gov.br/fundo-municipal-de-cultura-2023-2024-vai-investir-mais-de-r-2-milhoes-em-projetos-culturais/"],
["Anápolis", "2023-12-15", "Site municipal (WordPress)", "RESULTADO", "Lei Paulo Gustavo – resultado final com projetos contemplados", "https://www.anapolis.go.gov.br/lei-paulo-gustavo-divulga-resultado-final-com-projetos-contemplados/"],
["Anápolis", "2023-10-27", "Site municipal (WordPress)", "RESULTADO", "Projetos habilitados no edital da Lei Paulo Gustavo", "https://www.anapolis.go.gov.br/divulgados-os-projetos-habilitados-no-edital-da-lei-paulo-gustavo/"],
["Aparecida de Goiânia", "2025-11-12", "Site municipal (WordPress)", "ACOMPANHAR", "Secretaria de Cultura aprova projeto de R$ 13,2 milhões da Aldir Blanc para projetos culturais", "https://aparecida.go.gov.br/secretaria-de-cultura-de-aparecida-aprova-projeto-de-r-132-milhoes-da-aldir-blanc-para-projetos-culturais/"],
["Aparecida de Goiânia", "2024-11-18", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Aparecida lança editais do Programa Aldir Blanc com investimento de R$ 3,3 milhões", "https://aparecida.go.gov.br/aparecida-lanca-editais-do-programa-aldir-blanc-com-investimento-de-r-33-milhoes/"],
["Aparecida de Goiânia", "2024-06-12", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Assistência Social repassa emenda de R$ 200 mil ao Centro Bezerra de Menezes para projetos sociais", "https://aparecida.go.gov.br/assistencia-social-repassa-emenda-de-r-200-mil-ao-centro-bezerra-de-menezes-para-projetos-sociais/"],
["Aparecida de Goiânia", "2024-01-22", "Site municipal (WordPress)", "ATO_DO_EDITAL", "Prorrogação das inscrições para editais da Lei Paulo Gustavo", "https://aparecida.go.gov.br/prefeitura-de-aparecida-prorroga-inscricoes-para-editais-da-lei-paulo-gustavo/"],
["Aparecida de Goiânia", "2023-12-22", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Inscrições abertas para editais da Lei Paulo Gustavo", "https://aparecida.go.gov.br/aparecida-esta-com-inscricoes-abertas-para-editais-lei-paulo-gustavo/"],
["Caldas Novas", "2024-06-27", "Site municipal (WordPress)", "ACOMPANHAR", "Página da Política Nacional Aldir Blanc", "https://www.caldasnovas.go.gov.br/lei-aldir-blanc/"],
["Caldas Novas", "2024-06-27", "Site municipal (WordPress)", "ACOMPANHAR", "Página da Lei Paulo Gustavo", "https://www.caldasnovas.go.gov.br/lei-paulo-gustavo/"],
["Catalão", "2026-07-10", "Portal próprio (/avisos)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público 2º ciclo da Política Nacional Aldir Blanc - PNAB", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/2o-ciclo-da-politica-nacional-aldir-blanc-pnab"],
["Catalão", "2026-06-01", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público - Termo de Fomento nº 001/2026", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/edital-de-chamamento-publico-termo-de-fomento-no-0012026-010626175239"],
["Catalão", "2026-05-14", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "Edital de chamamento público - Termo de fomento nº 001/2026 (seção termo-fomento)", "https://www.catalao.go.gov.br/avisos/termo-fomento/edital-de-chamamento-publico-termo-de-fomento-no-0012026"],
["Catalão", "2026-01-16", "Portal próprio (/avisos)", "ACOMPANHAR", "Plano de Aplicação de Recursos", "https://www.catalao.go.gov.br/avisos/comunicados/plano-de-aplicacao-de-recursos"],
["Catalão", "2026-01-15", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "Edital de chamamento público nº 002/2025", "https://www.catalao.go.gov.br/avisos/termo-fomento/edital-de-chamamento-publico-no-0022025"],
["Catalão", "2025-12-24", "Portal próprio (/avisos)", "OUTRO_EDITAL", "Edital de credenciamento de manifestação de interesse nº 003/2025", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/edital-de-credenciamento-de-manifestacao-de-interesse-no-0032025"],
["Catalão", "2025-09-22", "Portal próprio (/avisos)", "OUTRO_EDITAL", "Edital de credenciamento de manifestação de interesse nº 002/2025", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/edital-de-credenciamento-de-manifestacao-de-interesse-no-0022025"],
["Catalão", "2025-02-12", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público – Termo de Fomento nº 001/2025", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/edital-de-chamamento-publico-termo-de-fomento-no-0012025"],
["Catalão", "2024-11-13", "Portal próprio (/avisos)", "RESULTADO", "Resultado preliminar dos editais de chamamento público nº 001/2024 e 002/2024", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/resultado-preliminar-dos-editais-de-chamamento-publico-no-0012024-e-0022024"],
["Catalão", "2024-10-15", "Portal próprio (/avisos)", "OPORTUNIDADE_CULTURA", "Chamamento Público - Fomento a projetos continuados de Pontos de Cultura", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/chamamento-publico-fomento-a-projetos-continuados-de-pontos-de-cultura-do-municipio-de-catalao-go"],
["Catalão", "2024-10-15", "Portal próprio (/avisos)", "OPORTUNIDADE_CULTURA", "Chamamento Público - Política Nacional Aldir Blanc de Fomento à Cultura (PNAB)", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/chamamento-publico-politica-nacional-aldir-blanc-de-fomento-a-cultura-pnab"],
["Catalão", "2024-05-24", "Portal próprio (/avisos)", "ACOMPANHAR", "Plano Anual de Aplicação dos Recursos (PAAR) para PNAB", "https://www.catalao.go.gov.br/avisos/termo-fomento/plano-anual-de-aplicacao-dos-recursos-paar-para-pnab-politica-nacional-aldir-blanc"],
["Catalão", "2024-04-05", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público – Termo de Fomento nº 005/2023", "https://www.catalao.go.gov.br/avisos/termo-fomento/edital-de-chamamento-publico-termo-de-fomento-no-0052023-de-20-de-setembro-de-2023"],
["Catalão", "2024-03-22", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "COMIC - Edital de Chamamento Público nº 001/2024", "https://www.catalao.go.gov.br/avisos/termo-fomento/comic-edital-de-chamamento-publico-no-0012024"],
["Catalão", "2024-01-18", "Portal próprio (/avisos)", "OUTRO_EDITAL", "Chamada Pública nº 002/2023", "https://www.catalao.go.gov.br/avisos/termo-fomento/chamada-publica-no-0022023"],
["Catalão", "2023-12-05", "Portal próprio (/avisos)", "OUTRO_EDITAL", "Chamada Pública 001/2023", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/chamada-publica-0012023"],
["Catalão", "2023-11-20", "Portal próprio (/avisos)", "OUTRO_EDITAL", "Chamada Pública nº 001/2023", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/chamada-publica-no-0012023"],
["Catalão", "2023-11-06", "Portal próprio (/avisos)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 006/2023 - Lei Paulo Gustavo - Audiovisual", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/edital-de-chamamento-publico-no-0062023-lei-paulo-gustavo-audiovisual-061123173753"],
["Catalão", "2023-11-06", "Portal próprio (/avisos)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 005/2023 - Lei Paulo Gustavo - Demais áreas", "https://www.catalao.go.gov.br/avisos/edital-de-chamamento-publico/edital-de-chamamento-publico-no-0052023-lei-paulo-gustavo-demais-areas-061123173935"],
["Catalão", "2023-11-01", "Portal próprio (/avisos)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público – Termo de Fomento nº 006/2023 - COMIC", "https://www.catalao.go.gov.br/avisos/termo-fomento/edital-de-chamamento-publico-termo-de-fomento-no-0062023-comic"],
["Cidade Ocidental", "2026-07-24", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Editais da PNAB publicados", "https://cidadeocidental.go.gov.br/editais-da-pnab-publicados/"],
["Cidade Ocidental", "2025-06-10", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Chamada pública – Lei 14.399/2022 – PNAB", "https://cidadeocidental.go.gov.br/chamada-publica-para-a-lei-14-399-2022-politica-nacional-aldir-blanc-pnab/"],
["Cidade Ocidental", "2024-12-07", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 006/2023 – promoção das expressões culturais", "https://cidadeocidental.go.gov.br/edital-de-chamamento-publico-no-006-2023-promocao-das-expressoes-culturais-em-cidade-ocidental-go/"],
["Cidade Ocidental", "2024-11-28", "Site municipal (WordPress)", "RESULTADO", "Resultado Mérito Cultural – Lei Paulo Gustavo", "https://cidadeocidental.go.gov.br/resultado-merito-cultural-lei-paulo-gustavo/"],
["Cidade Ocidental", "2024-11-14", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Lei Paulo Gustavo – Edital de Chamamento Público nº 002/2024", "https://cidadeocidental.go.gov.br/lei-paulo-gustavo-edital-de-chamamento-publico-no-002-2024/"],
["Cidade Ocidental", "2023-12-14", "Site municipal (WordPress)", "RESULTADO", "Resultado final das propostas aprovadas – Lei Paulo Gustavo", "https://cidadeocidental.go.gov.br/saiu-o-resultado-final-das-propostas-aprovadas-para-a-lei-paulo-gustavo/"],
["Cidade Ocidental", "2023-11-09", "Site municipal (WordPress)", "ACOMPANHAR", "Cidade Ocidental recebe R$ 2,5 milhões em emendas parlamentares", "https://cidadeocidental.go.gov.br/cidade-ocidental-recebe-r-25-milhoes-em-emendas-parlamentares/"],
["Cidade Ocidental", "2023-11-08", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Abertura das inscrições para o edital da Lei Paulo Gustavo", "https://cidadeocidental.go.gov.br/cidade-ocidental-abre-as-inscricoes-para-o-edital-da-lei-paulo-gustavo/"],
["Cristalina", "2026-01-14", "Site municipal (WordPress)", "ACOMPANHAR", "PNAB ciclo 2 (página)", "https://cristalina.go.gov.br/pnab-ciclo-2/"],
["Cristalina", "2025-11-10", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de fomento", "https://www.diariomunicipal.com.br/agm/materia/D70ED45F"],
["Cristalina", "2025-06-03", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Entrega de van para a APAE por meio de emenda parlamentar", "https://cristalina.go.gov.br/prefeitura-de-cristalina-realiza-entrega-de-van-para-a-apae-por-meio-de-emenda-do-senador-vanderlan-cardoso/"],
["Cristalina", "2024-10-29", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamamento Público 006/2024 – Cultura Viva", "https://www.diariomunicipal.com.br/agm/materia/9E46D5D5"],
["Cristalina", "2024-10-29", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 005/2024", "https://www.diariomunicipal.com.br/agm/materia/8071DD8E"],
["Cristalina", "2024-07-31", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_OSC", "Chamamento 003/2024", "https://www.diariomunicipal.com.br/agm/materia/0DCC31CA"],
["Cristalina", "2023-11-17", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público 004/2023", "https://cristalina.go.gov.br/edital-de-chamamento-publico-004-2023/"],
["Cristalina", "2023-11-17", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público 003/2023", "https://cristalina.go.gov.br/edital-de-chamamento-publico-003-2023/"],
["Cristalina", "2023-11-16", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público 002/2023", "https://cristalina.go.gov.br/edital-de-chamamento-publico-002-2023/"],
["Cristalina", "2023-10-06", "Diário AGM (diariomunicipal.com.br/agm)", "CMDCA_FIA", "Extrato da Resolução 007/2023 do CMDCA", "https://www.diariomunicipal.com.br/agm/materia/2524703A"],
["Formosa", "2026-08-07", "Site municipal (WordPress)", "RESULTADO", "Resultado definitivo – Chamamento Público 01/2026", "https://www.formosa.go.gov.br/edital-de-resultado-definitivo-chamamento-publico-01-2026/"],
["Formosa", "2026-07-31", "Site municipal (WordPress)", "RESULTADO", "Resultado preliminar – Chamamento Público 01/2026", "https://www.formosa.go.gov.br/resultado-preliminar-chamamento-publico-01-2026/"],
["Formosa", "2026-07-15", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato do termo de convênio", "https://www.diariomunicipal.com.br/agm/materia/D6E99EBC"],
["Formosa", "2026-07-02", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_OSC", "Chamada pública – seleção de OSC para Termo de Colaboração", "https://www.diariomunicipal.com.br/agm/materia/D8B273E6"],
["Formosa", "2026-06-11", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (associação)", "https://www.diariomunicipal.com.br/agm/materia/F9AC01F0"],
["Formosa", "2026-05-08", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento nº 02/2026 com entidade sem fins lucrativos", "https://www.diariomunicipal.com.br/agm/materia/7463867A"],
["Formosa", "2026-04-09", "Site municipal (WordPress)", "AGRICULTURA_FAMILIAR", "Chamada Pública nº 01/2026 – Programa de Aquisição de Alimentos (PAA)", "https://www.formosa.go.gov.br/chamada-publica-no-01-2026-do-programa-de-aquisicao-de-alimentos-paa/"],
["Formosa", "2026-03-12", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de chamamento público 01/2026", "https://www.formosa.go.gov.br/edital-chamamento-publico-01-2026/"],
["Formosa", "2026-03-12", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamada pública – seleção de projetos literários", "https://www.diariomunicipal.com.br/agm/materia/FBBBF871"],
["Formosa", "2026-03-12", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamada pública – seleção de Pontos de Cultura", "https://www.diariomunicipal.com.br/agm/materia/CC60A0E7"],
["Formosa", "2026-03-12", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamada pública (Secretaria de Cultura)", "https://www.diariomunicipal.com.br/agm/materia/9F86D4C8"],
["Formosa", "2026-03-12", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamada pública (Secretaria de Cultura)", "https://www.diariomunicipal.com.br/agm/materia/9AB05DBD"],
["Formosa", "2026-03-12", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamada pública (Secretaria de Cultura)", "https://www.diariomunicipal.com.br/agm/materia/D59EB203"],
["Formosa", "2026-02-25", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social – repasse de emenda impositiva", "https://www.diariomunicipal.com.br/agm/materia/BADF4E61"],
["Formosa", "2026-01-20", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (sociedade)", "https://www.diariomunicipal.com.br/agm/materia/9767862B"],
["Formosa", "2026-01-12", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio com a APPAF (Associação de Pais e Pessoas com Autismo)", "https://www.diariomunicipal.com.br/agm/materia/A3D0F66E"],
["Formosa", "2025-12-17", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio com o Lar São Vicente de Paulo", "https://www.diariomunicipal.com.br/agm/materia/12F8F7A8"],
["Formosa", "2025-12-05", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (associação)", "https://www.diariomunicipal.com.br/agm/materia/4FBDF07C"],
["Formosa", "2025-12-05", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (associação)", "https://www.diariomunicipal.com.br/agm/materia/8E7D2411"],
["Formosa", "2025-12-05", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (associação)", "https://www.diariomunicipal.com.br/agm/materia/6FB8AA7C"],
["Formosa", "2025-11-21", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (sociedade)", "https://www.diariomunicipal.com.br/agm/materia/4EECD418"],
["Formosa", "2025-11-07", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato do termo de convênio", "https://www.diariomunicipal.com.br/agm/materia/BB80E6D5"],
["Formosa", "2025-10-31", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de convênio", "https://www.diariomunicipal.com.br/agm/materia/9C81F212"],
["Formosa", "2025-09-04", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Convênio de subvenção social com entidade filantrópica (sociedade)", "https://www.diariomunicipal.com.br/agm/materia/6BDD63CB"],
["Formosa", "2025-07-15", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de termo de convênio (Processo 4332/2025)", "https://www.diariomunicipal.com.br/agm/materia/F0078CA0"],
["Formosa", "2025-03-28", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital 06/2025 – Chamada Pública", "https://www.formosa.go.gov.br/edital-06-2025-chamada-publica-assinado/"],
["Formosa", "2025-01-28", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de chamamento público para seleção de projetos", "https://www.formosa.go.gov.br/edital-de-chamamento-publico-para-selecao-de-projetos/"],
["Goianésia", "2026", "Página de editais (PDF)", "OPORTUNIDADE_OSC", "Edital 006/2026 – Chamamento Público Credenciamento Social", "https://www.goianesia.go.gov.br/wp-content/uploads/2023/02/Edital-de-Chamamento-Publico-Credenciamento-Social-CORRIGIDO-FINAL-1.pdf"],
["Goianésia", "2026", "Página de editais (PDF)", "OPORTUNIDADE_CULTURA", "Edital 002/2026 – Cultura – Lei Aldir Blanc (execução cultural de projetos)", "https://www.goianesia.go.gov.br/wp-content/uploads/2023/02/EDITAL-CULTURA-LEI-ALDIR-BLANC-.pdf"],
["Goianésia", "2026", "Página de editais (PDF)", "OPORTUNIDADE_OSC", "Edital 002/2026 – Minuta de Edital de Chamamento Público", "https://www.goianesia.go.gov.br/wp-content/uploads/2023/11/6-Minuta-de-Edital-de-Chamamento-Publico.pdf"],
["Goianésia", "2025", "Página de editais (PDF)", "OPORTUNIDADE_CULTURA", "Edital 001/2025 – Prêmio Pontos e Pontões de Cultura (PNCV/PNAB)", "https://www.goianesia.go.gov.br/wp-content/uploads/2023/11/EDITAL.pdf"],
["Goianésia", "2025", "Página de editais (PDF)", "OUTRO_EDITAL", "Edital de Chamamento Público – Credenciamento nº 001/2025", "https://www.goianesia.go.gov.br/wp-content/uploads/2025/04/EDITAL-DE-CREDENCIAMENTO-001-2025.pdf"],
["Goianésia", "2025", "Página de editais (PDF)", "OUTRO_EDITAL", "Edital de Chamamento Público – Credenciamento nº 002/2025", "https://www.goianesia.go.gov.br/wp-content/uploads/2023/11/Edital-002-2025.pdf"],
["Goiânia", "2026-09-23", "Site municipal (WordPress)", "ACOMPANHAR", "Prefeitura regulamenta repasse de emendas parlamentares para escolas da rede municipal", "https://www.goiania.go.gov.br/agora/prefeitura-regulamenta-repasse-de-emendas-parlamentares-para-escolas-da-rede-municipal-de-goiania"],
["Goiânia", "2026-05-10", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento público para seleção de instituições de longa permanência e casa-lar para idosos", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-abre-chamamento-publico-para-selecao-de-instituicoes-de-longa-permanencia-e-casa-lar-para-idosos"],
["Goiânia", "2026-03-05", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Prazo de inscrições para editais da PNAB e da Lei Municipal de Incentivo à Cultura", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-anuncia-prazo-de-inscricoes-para-editais-da-pnab-e-da-lei-municipal-de-incentivo-a-cultura"],
["Goiânia", "2026-02-20", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital seleciona artistas para programação cultural durante MotoGP", "https://www.goiania.go.gov.br/agora/edital-seleciona-artistas-para-programacao-cultural-durante-motogp-em-goiania"],
["Goiânia", "2025-11-10", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "3º Prêmio Goiânia Sustentável – valoriza projetos socioambientais", "https://www.goiania.go.gov.br/agora/prefeitura-promove-3o-premio-goiania-sustentavel-para-valorizar-projetos-socioambientais"],
["Goiânia", "2025-06-18", "Site municipal (WordPress)", "CONSELHO", "Resultado preliminar das entidades habilitadas ao Colégio Eleitoral do COMPED", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-divulga-resultado-preliminar-das-entidades-habilitadas-ao-colegio-eleitoral-do-comped-goiania"],
["Goiânia", "2025-06-03", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Prefeitura publica chamamento de organizações sociais", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-publica-chamamento-de-organizacoes-sociais"],
["Goiânia", "2025-04-25", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Credenciamento para entidades socioassistenciais (parceria com o terceiro setor)", "https://www.goiania.go.gov.br/agora/prefeito-mabel-lanca-credenciamento-para-entidades-socioassistenciais-e-destaca-parceria-com-o-terceiro-setor"],
["Goiânia", "2024-06-14", "Site municipal (WordPress)", "ATO_DO_EDITAL", "Inscrição em edital da Lei Municipal de Incentivo à Cultura termina em 14/6", "https://www.goiania.go.gov.br/agora/inscricao-em-edital-para-lei-municipal-de-incentivo-a-cultura-termina-nesta-sexta-14-6"],
["Goiânia", "2024-04-05", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital da Lei Municipal de Incentivo à Cultura 2024", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-publica-edital-da-lei-municipal-de-incentivo-a-cultura-2024"],
["Goiânia", "2024-01-25", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Entrega de sete veículos para entidades assistenciais", "https://www.goiania.go.gov.br/agora/prefeito-rogerio-entrega-sete-novos-veiculos-para-entidades-assistenciais-de-goiania"],
["Goiânia", "2024-01-21", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Repasse para fomentar o futebol goianiense (parceria com a Câmara)", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-em-parceria-com-a-camara-anuncia-repasse-para-fomentar-futebol-goianiense"],
["Goiânia", "2023-12-06", "Site municipal (WordPress)", "RESULTADO", "Primeiro resultado preliminar dos editais da Lei Paulo Gustavo", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-publica-primeiro-resultado-preliminar-referente-aos-editais-da-lei-paulo-gustavo"],
["Goiânia", "2023-11-22", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Inscrições para a 2ª edição do Prêmio Goiânia Sustentável", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-abre-inscricoes-para-a-2a-edicao-do-premio-goiania-sustentavel"],
["Goiânia", "2023-11-03", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Repasses a entidades filantrópicas somam cerca de R$ 5 milhões", "https://www.goiania.go.gov.br/agora/repasses-a-entidades-filantropicas-somam-cerca-de-r-5-milhoes-e-reafirmam-compromisso-do-prefeito-rogerio-com-area-social"],
["Goiânia", "2023-10-17", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Editais da Lei Paulo Gustavo com inscrições de 18/10 a 2/11", "https://www.goiania.go.gov.br/agora/prefeitura-de-goiania-publica-editais-da-lei-paulo-gustavo-com-inscricoes-abertas-de-18-de-outubro-a-partir-das-12h-ate-2-de-novembro"],
["Inhumas", "2026-08-20", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – extrato de contrato nº 08/2026", "https://www.diariomunicipal.com.br/agm/materia/15EADC2C"],
["Inhumas", "2026-08-04", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Plano de trabalho com emenda parlamentar nº 87 (R$ 100 mil) – FMDS", "https://www.diariomunicipal.com.br/agm/materia/1AD9A88A"],
["Inhumas", "2026-07-22", "Site municipal (WordPress)", "RESULTADO", "Resultado da PNAB – Ciclo 2", "https://www.inhumas.go.gov.br/%f0%9f%93%a2-atencao-fazedores-de-cultura/"],
["Inhumas", "2026-07-17", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento nº 007/2026", "https://www.diariomunicipal.com.br/agm/materia/824F71A0"],
["Inhumas", "2026-07-14", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Contrato de Fomento nº 06/2026", "https://www.diariomunicipal.com.br/agm/materia/01C4F6FB"],
["Inhumas", "2026-07-14", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Contrato de Fomento nº 05/2026", "https://www.diariomunicipal.com.br/agm/materia/B8083DA9"],
["Inhumas", "2026-07-06", "Site municipal (WordPress)", "RESULTADO", "Lista de inscrições – Edital de Chamamento Público 006/2026 PNAB (premiação de pontos e pontões de cultura)", "https://www.inhumas.go.gov.br/lista-de-inscricoes-inhumas-go-edital-de-chamamento-publico-006-2026-premiacao-de-pontos-e-pontoes-de-cultura/"],
["Inhumas", "2026-06-01", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 004/2026 – seleção de projetos (termo de execução cultural)", "https://www.diariomunicipal.com.br/agm/materia/AF9CCBD4"],
["Inhumas", "2026-06-01", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 005/2026 – premiação de agentes culturais", "https://www.diariomunicipal.com.br/agm/materia/A53DC3F9"],
["Inhumas", "2026-05-07", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Projeto de Lei 014 – autoriza subvenções a entidades para programas assistenciais", "https://www.inhumas.go.gov.br/projeto-de-lei-014-autoriza-conceder-subvencaoes-as-entidades-que-especifica-para-manutencao-de-programas-assistenciais/"],
["Inhumas", "2026-05-07", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Projeto de Lei 005 – subvenção via FMAS à Fundação de Assistência ao Menor Inhumense", "https://www.inhumas.go.gov.br/projeto-de-lei-005-autoriza-o-poder-executivo-por-meio-do-fundo-municipal-de-assistencia-social-fmas-a-conceder-no-exercicio-de-2026-subvencao-a-fundacao-de-assistencia-ao-menor-inhumense/"],
["Inhumas", "2026-02-23", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de Fomento 03/2026 – FMDS", "https://www.diariomunicipal.com.br/agm/materia/2A86C553"],
["Inhumas", "2026-02-20", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de Fomento nº 002/2026 – FMDS", "https://www.diariomunicipal.com.br/agm/materia/27373937"],
["Inhumas", "2026-01-30", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de Fomento nº 001/2026 – FMDS", "https://www.diariomunicipal.com.br/agm/materia/0F28068F"],
["Inhumas", "2026-01-23", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento 001/2026", "https://www.inhumas.go.gov.br/edital-de-chamamento-001-2026/"],
["Inhumas", "2025-10-31", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 033/2025 (Saúde)", "https://www.diariomunicipal.com.br/agm/materia/502C4040"],
["Inhumas", "2025-10-02", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 032/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/0DCEB285"],
["Inhumas", "2025-09-09", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 029/2025 (Educação)", "https://www.diariomunicipal.com.br/agm/materia/0517FB47"],
["Inhumas", "2025-09-04", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 023/2025 (Saúde)", "https://www.diariomunicipal.com.br/agm/materia/C0DEF6B5"],
["Inhumas", "2025-09-03", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 030/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/C7540A9A"],
["Inhumas", "2025-08-27", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 028/2025", "https://www.diariomunicipal.com.br/agm/materia/FB64E5DD"],
["Inhumas", "2025-08-21", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 021/2025 (Saúde)", "https://www.diariomunicipal.com.br/agm/materia/7CEE05DC"],
["Inhumas", "2025-08-21", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 025/2025", "https://www.diariomunicipal.com.br/agm/materia/C535DDD4"],
["Inhumas", "2025-08-21", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 026/2025", "https://www.diariomunicipal.com.br/agm/materia/C9083AA0"],
["Inhumas", "2025-08-19", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 022/2025 (Saúde)", "https://www.diariomunicipal.com.br/agm/materia/91F44EE3"],
["Inhumas", "2025-08-19", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 020/2025 (Saúde)", "https://www.diariomunicipal.com.br/agm/materia/AF99A238"],
["Inhumas", "2025-07-17", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 017/2025", "https://www.diariomunicipal.com.br/agm/materia/CD4C6095"],
["Inhumas", "2025-07-07", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 013/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/6556226D"],
["Inhumas", "2025-07-07", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 012/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/BF6A1D53"],
["Inhumas", "2025-07-07", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 015/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/CE41F04D"],
["Inhumas", "2025-07-07", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 014/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/2B1A3D7D"],
["Inhumas", "2025-07-07", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 016/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/7F9380A8"],
["Inhumas", "2025-07-04", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 011/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/0007B826"],
["Inhumas", "2025-07-03", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento nº 003/2025", "https://www.inhumas.go.gov.br/edital-de-chamamento-n-003-2025/"],
["Inhumas", "2025-07-02", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 009/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/9611FE0D"],
["Inhumas", "2025-07-01", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 008/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/194D7F45"],
["Inhumas", "2025-07-01", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 010/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/D7D23729"],
["Inhumas", "2025-06-26", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 005/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/AE9F0886"],
["Inhumas", "2025-06-24", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de Fomento – contrato nº 006/2025 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/071273F7"],
["Inhumas", "2025-06-13", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento nº 002/2025", "https://www.inhumas.go.gov.br/edital-de-chamamento-n-002-2025/"],
["Inhumas", "2025-04-15", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Primeiro aditivo ao Termo de Fomento nº 016/2024 (FMDS)", "https://www.diariomunicipal.com.br/agm/materia/93692132"],
["Inhumas", "2024-11-19", "Site municipal (WordPress)", "RESULTADO", "Homologação do resultado definitivo – edital da Lei Complementar Aldir Blanc", "https://www.inhumas.go.gov.br/15-homologacao-e-divulgacao-do-resultado-definitivo-do-edital-da-lei-complementar-aldir-blanc-lei-no-14-399-2022/"],
["Inhumas", "2024-10-21", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 001/2024 – Lei Aldir Blanc", "https://www.inhumas.go.gov.br/11-edital-de-chamamento-publico-no-001-2024-lei-aldir-blanc/"],
["Inhumas", "2024-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 003/2024 – Cultura Viva", "https://www.inhumas.go.gov.br/10-edital-de-chamamento-publico-n-003-2024-cultura-viva/"],
["Inhumas", "2024-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 002/2024 – Premiação", "https://www.inhumas.go.gov.br/09-edital-de-chamamento-publico-n-002-2024-premiacao/"],
["Inhumas", "2024-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 001/2024 – Seleção de Projetos", "https://www.inhumas.go.gov.br/08-edital-de-chamamento-publico-n001-2024-selecao-de-projetos/"],
["Inhumas", "2023-10-06", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Lei Paulo Gustavo – lançamento de editais", "https://www.inhumas.go.gov.br/lei-paulo-gustavo-lancamento-de-editais/"],
["Itaberaí", "2026-09-25", "Site municipal (WordPress)", "CMDCA_FIA", "Edital de Chamamento Público nº 001-CMDCA-2026", "https://www.itaberai.go.gov.br/edital-de-chamamento-publico-n-001-cmdca-2026/"],
["Itaberaí", "2025-07-01", "Site municipal (WordPress)", "RESULTADO", "Resolução 003/2025 CMDCA – homologação do resultado final dos projetos financiados pelo FMDCA", "https://www.itaberai.go.gov.br/resolucao-no-003-2025-cmdca-homologacao-de-resultado-final-projetos-financiados-fmdca/"],
["Itaberaí", "2025-06-10", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 002/2025", "https://www.itaberai.go.gov.br/dital-de-chamamento-publico-no-002-2025/"],
["Itaberaí", "2025-04-08", "Site municipal (WordPress)", "CMDCA_FIA", "Edital de Chamamento Público nº 001-CMDCA-2025", "https://www.itaberai.go.gov.br/edital-de-chamamento-publico-no-001-cmdca-2025/"],
["Itaberaí", "2024-11-29", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 005/2024", "https://www.itaberai.go.gov.br/edital-de-chamamento-publico-no-005-2024/"],
["Itaberaí", "2024-03-22", "Site municipal (WordPress)", "RESULTADO", "Resultado definitivo – edital de chamamento Lei Paulo Gustavo", "https://www.itaberai.go.gov.br/resultado-definitivo-edital-de-chamamento-publico-lei-paulo-gustavo/"],
["Itaberaí", "2024-01-31", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital complementar 005/2024 – Lei Paulo Gustavo", "https://www.itaberai.go.gov.br/edital-complementar-005-2024-lei-paulo-gustavo/"],
["Itumbiara", "2026-09-15", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Inscrições abertas para editais de premiação e fomento de projetos culturais", "https://www.itumbiara.go.gov.br/inscricoes-abertas-para-editais-de-premiacao-e-fomento-de-projetos-culturais/"],
["Itumbiara", "2024-10-31", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Chamada pública de agentes culturais (até 8/11)", "https://www.itumbiara.go.gov.br/inscricoes-em-chamada-publica-de-agentes-culturais-de-itumbiara-irao-ate-o-dia-8-de-novembro/"],
["Itumbiara", "2023-11-27", "Site municipal (WordPress)", "RESULTADO", "Projetos culturais selecionados pela Lei Paulo Gustavo", "https://www.itumbiara.go.gov.br/divulgados-os-projetos-culturais-selecionados-nas-areas-de-audiovisual-outras-linguagens-culturais-e-multilinguagem-pela-lei-paulo-gustavo-em-itumbiara/"],
["Itumbiara", "2023-11-06", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital Chamada Pública – Lei Paulo Gustavo", "https://www.itumbiara.go.gov.br/edital-chamada-publica-lei-paulo-gustavo/"],
["Jaraguá", "2026-08-24", "Site municipal (WordPress)", "RESULTADO", "PNAB: início dos pagamentos aos artistas contemplados", "https://www.jaragua.go.gov.br/pnab-prefeitura-de-jaragua-inicia-pagamentos-aos-artistas-contemplados/"],
["Jaraguá", "2026-04-27", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital Aldir Blanc 2026 disponível", "https://www.jaragua.go.gov.br/edital-aldir-blanc-2026-ja-disponivel-artistas-de-jaragua-preparem-se-para-as-inscricoes/"],
["Jaraguá", "2024-03-08", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital cultural para Semana Santa", "https://www.jaragua.go.gov.br/edital-cultural-para-semana-santa/"],
["Jaraguá", "2023-10-05", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Inscrições abertas – Lei Paulo Gustavo (até 22/10)", "https://www.jaragua.go.gov.br/chegou-a-hora-de-voce-dar-mais-um-passo-conosco-na-lei-paulo-gustavo-de-incentivo-cultural-as-inscricoes-estao-abertas-a-partir-de-hoje-ate-o-proximo-dia-22-de-outubro-entao-voce-que-e-artista-jarag/"],
["Jataí", "2026-09-08", "Site municipal (WordPress)", "AGRICULTURA_FAMILIAR", "Chamada pública para compra de alimentos da agricultura familiar (PAA)", "https://www.jatai.go.gov.br/prefeitura-de-jatai-abre-chamada-publica-para-compra-de-alimentos-da-agricultura-familiar-pelo-paa/"],
["Jataí", "2026-07-30", "Site municipal (WordPress)", "RESULTADO", "Resultado final do Edital de Chamamento Público nº 002/2026 (Cultura)", "https://www.jatai.go.gov.br/secretaria-de-cultura-de-divulga-resultado-do-recurso-e-resultado-final-do-edital-de-chamamento-publico-no-002-2026/"],
["Jataí", "2026-03-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital da Lei de Incentivo à Cultura 2026 – apoio de até R$ 40 mil", "https://www.jatai.go.gov.br/cultura-em-acao-prefeitura-lanca-edital-da-lei-de-incentivo-2026-com-apoio-de-ate-r-40-mil/"],
["Jataí", "2025-11-27", "Site municipal (WordPress)", "RESULTADO", "Homologação do resultado do Edital PNAB 02/2025", "https://www.jatai.go.gov.br/cultura-homologa-resultado-do-edital-pnab-02-2025/"],
["Jataí", "2025-09-03", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "PNAB – editais para Pontos de Cultura (fomento continuado e premiação)", "https://www.jatai.go.gov.br/pnab-jatai-lanca-editais-para-pontos-de-cultura-a-secretaria-de-cultura-publica-mais-dois-editais-voltados-a-rede-municipal-de-pontos-de-cultura-com-foco-em-fomento-continuado-e-premiacao-de-trajet/"],
["Jataí", "2025-08-14", "Site municipal (WordPress)", "AGRICULTURA_FAMILIAR", "Chamada pública para agricultura familiar no PNAE 2025", "https://www.jatai.go.gov.br/chamada-publica-para-agricultura-familiar-no-pnae-2025/"],
["Jataí", "2025-06-10", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "PNAB – edital de fomento a ações culturais e premiação por trajetória", "https://www.jatai.go.gov.br/pnab-jatai-publica-edital-de-fomento-a-acoes-culturais-e-premiacao-por-trajetoria-secretaria-de-cultura-de-jatai-lanca-edital-para-impulsionar-projetos-culturais-e-valorizar-trajetorias-artisticas-n/"],
["Jataí", "2025-03-19", "Site municipal (WordPress)", "OUTRO_EDITAL", "Credenciamento de pareceristas técnicos culturais", "https://www.jatai.go.gov.br/lancamento-de-edital-para-credenciamento-de-pareceristas-tecnicos-culturais-especializados/"],
["Jataí", "2024-11-04", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital nº 003/2024 – Lei de Incentivo à Cultura", "https://www.jatai.go.gov.br/lancamento-edital-no-003-2024-da-lei-de-incentivo-a-cultura-de-jatai/"],
["Jataí", "2024-10-10", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de fomento ao audiovisual – Lei Paulo Gustavo", "https://www.jatai.go.gov.br/inscricoes-abertas-para-o-edital-de-fomento-ao-audiovisual-da-lei-paulo-gustavo-em-jatai/"],
["Jataí", "2024-04-16", "Site municipal (WordPress)", "ACOMPANHAR", "Temporada de captação de recursos para fomento ao setor cultural", "https://www.jatai.go.gov.br/temporada-de-captacao-de-recursos-para-fomento-ao-setor-cultural-esta-aberta/"],
["Jataí", "2024-01-29", "Site municipal (WordPress)", "RESULTADO", "Homologação do resultado final do edital da Lei Paulo Gustavo", "https://www.jatai.go.gov.br/homologacao-do-resultado-final-do-edital-da-lei-paulo-gustavo-em-jatai/"],
["Jataí", "2023-12-12", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Prefeito autoriza publicação de edital para incentivo à cultura", "https://www.jatai.go.gov.br/prefeito-autoriza-publicacao-de-edital-para-incentivo-a-cultura/"],
["Jataí", "2023-11-17", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Lançamento do edital da Lei Paulo Gustavo", "https://www.jatai.go.gov.br/edital-da-lei-paulo-gustavo-e-lancado/"],
["Luziânia", "s/d", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Extrato de Termo de Fomento", "https://www.luziania.go.gov.br/extrato-de-termo-de-fomento/"],
["Luziânia", "s/d", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Extrato de Termo de Fomento (2)", "https://www.luziania.go.gov.br/extrato-de-termo-de-fomento-2/"],
["Luziânia", "s/d", "Site municipal (tabela)", "ACOMPANHAR", "Tabela de Termos de Colaboração", "https://www.luziania.go.gov.br/tabela-termos/"],
["Luziânia", "2026", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 001/2026 (termo de fomento, sociedade civil)", "https://www.luziania.go.gov.br/edital-de-chamamento-publico-no-001-2026/"],
["Luziânia", "2026", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 001/2026/SMS-FMS (termo de colaboração com OSC)", "https://www.luziania.go.gov.br/edital-de-chamamento-publico-n-001-2026-sms-fms/"],
["Luziânia", "2026", "Site municipal (busca interna)", "RESULTADO", "Termo de homologação – Edital de Chamamento Público nº 001/2026-FMS", "https://www.luziania.go.gov.br/termo-de-homologacao-edital-de-chamamento-publico-no-001-2026-fms/"],
["Luziânia", "2026", "Site municipal (busca interna)", "ATO_DO_EDITAL", "Parecer técnico – comissão especial de seleção – Chamamento Público 001/2026", "https://www.luziania.go.gov.br/parecer-tecnico-comissao-especial-de-selecao-chamamento-publico-n001-2026/"],
["Luziânia", "2026", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Termo de Colaboração nº 01/2026 – OSC Instituto Patris (Chamamento 001/2026/SMS-FMS)", "https://www.luziania.go.gov.br/termo-de-colaboracao-organizacao-da-sociedade-civil-instituto-patris-no-ambito-do-chamamento-publico-no-001-2026-sms-fms-processo-administrativo-no-2025036752/"],
["Luziânia", "2026", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público para Credenciamento nº 001/2026", "https://www.luziania.go.gov.br/edital-de-chamamento-publico-para-credenciamento-n-001-2026/"],
["Luziânia", "2026", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Modalidade Chamamento Público nº 002/2026 – SMS (Processo 2026013004)", "https://www.luziania.go.gov.br/modalidade-chamamento-publico-no-002-2026-sms-processo-administrativo-no-2026013004/"],
["Luziânia", "2026", "Site municipal (busca interna)", "CMDCA_FIA", "Resolução nº 01/2026 – CMDCA/Luziânia", "https://www.luziania.go.gov.br/resolucao-%e2%84%96-01-2026-cmdca-luziania/"],
["Luziânia", "2025", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Termo de Colaboração Emergencial nº 01/2025 – OSC Instituto Patris", "https://www.luziania.go.gov.br/termo-de-colaboracao-emergencial-n-01-2025-organizacao-da-sociedade-civil-instituto-patris/"],
["Luziânia", "2025", "Site municipal (busca interna)", "OPORTUNIDADE_CULTURA", "Chamada Pública nº 005/2025 – fomento cultural (Aldir Blanc)", "https://www.luziania.go.gov.br/chamada-publica-no-005-2025-processo-administrativo-no-2025030815/"],
["Luziânia", "2025", "Site municipal (busca interna)", "RESULTADO", "Resultado da curadoria de mérito cultural – Edital 005/2025 de fomento cultural", "https://www.luziania.go.gov.br/divulgacao-do-resultado-da-curadoria-de-analise-de-merito-cultural-edital-de-chamamento-publico-no-005-2025-de-fomento-cultural/"],
["Luziânia", "2025", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Chamamento Público nº 004/2025 (Processo 2025027602)", "https://www.luziania.go.gov.br/chamamento-publico-no-004-2025-processo-administrativo-no-2025027602/"],
["Luziânia", "2025", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Chamamento Público nº 002/2025 (Processo 2025003239)", "https://www.luziania.go.gov.br/chamamento-publico-no-002-2025-processo-administrativo-no-2025003239/"],
["Luziânia", "2025", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Chamamento Público nº 001/2025 (Processo 2025000307)", "https://www.luziania.go.gov.br/chamamento-publico-no-001-2025-processo-administrativo-no-2025000307/"],
["Luziânia", "2025", "Site municipal (busca interna)", "CMDCA_FIA", "Resoluções nº 05 e 06/2025 – CMDCA", "https://www.luziania.go.gov.br/resolucao-no06-2025-cmdca/"],
["Luziânia", "2024", "Site municipal (busca interna)", "CMDCA_FIA", "Edital de Chamamento Público CMDCA nº 001/2024", "https://www.luziania.go.gov.br/edital-de-chamamento-publico-cmdca-n001-2024/"],
["Luziânia", "2024", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Chamamento Público nº 003/2024 (termo de colaboração com OSC)", "https://www.luziania.go.gov.br/chamamento-publico-no-003-2024-processo-administrativo-no-2024010221/"],
["Luziânia", "2024", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Chamamento Público nº 005/2024 (Processo 2024024325)", "https://www.luziania.go.gov.br/chamamento-publico-no-005-2024-processo-administrativo-no-2024024325/"],
["Luziânia", "2024", "Site municipal (busca interna)", "OPORTUNIDADE_OSC", "Chamamento Público nº 004/2024 (Processo 2024025077)", "https://www.luziania.go.gov.br/chamamento-publico-no-004-2024-processo-administrativo-no-2024025077/"],
["Luziânia", "2024", "Site municipal (busca interna)", "OPORTUNIDADE_CULTURA", "Aviso de Chamamento Público nº 002/2024 – Lei Aldir Blanc", "https://www.luziania.go.gov.br/aviso-de-chamamento-publico-n-002-2024-lei-aldir-blanc/"],
["Luziânia", "2024", "Site municipal (busca interna)", "OPORTUNIDADE_CULTURA", "Aviso de Chamamento Público nº 001/2024 – Lei Aldir Blanc", "https://www.luziania.go.gov.br/aviso-de-chamamento-publico-n001-2024-lei-aldir-blanc/"],
["Luziânia", "2024", "Site municipal (busca interna)", "OPORTUNIDADE_CULTURA", "Aldir Blanc 2024 – Edital de Fomento Cultural \"Luziânia 279 Anos de História\"", "https://www.luziania.go.gov.br/aldir-blanc-2024-edital-de-fomento-cultural-luziania-279-de-historia/"],
["Luziânia", "2024", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Extrato de Convênio nº 002/2024 (subvenção)", "https://www.luziania.go.gov.br/extrato-de-convenio-n002-2024/"],
["Luziânia", "2024", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Extrato de Convênio nº 001/2024 (subvenção)", "https://www.luziania.go.gov.br/extrato-de-convenio-11/"],
["Luziânia", "2023", "Site municipal (busca interna)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 06/2023 – Lei Paulo Gustavo", "https://www.luziania.go.gov.br/edital-de-chamamento-publico-no-06-2023/"],
["Luziânia", "2023", "Site municipal (busca interna)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 05/2023 – Lei Paulo Gustavo", "https://www.luziania.go.gov.br/edital-de-chamamento-publico-no-05-2023/"],
["Luziânia", "2023", "Site municipal (busca interna)", "PARCERIA_DIRETA", "Termos de Colaboração – Processo 2023031278 (Partis e Bone)", "https://www.luziania.go.gov.br/termo-de-colaboracao-processo-administrativo-n-2023031278-partis/"],
["Mineiros", "2026-09-23", "Portal próprio (Convênios)", "PARCERIA_DIRETA", "Termo de Fomento nº 001/2026 – APAE de Mineiros, projeto \"Assistência Legal: Aconselhamento Jurídico Inclusivo\"", "https://www.mineiros.go.gov.br/acesso-a-informacao/convenios"],
["Mineiros", "2026-09-21", "Portal próprio (PROCACES)", "PARCERIA_DIRETA", "Incentivo financeiro – Projeto Elos de Convivência com Idosos e Crianças (CRAS)", "https://www.mineiros.go.gov.br/acesso-a-informacao/apoio-financeiro"],
["Mineiros", "2026-08-25", "Portal próprio (PROCACES)", "PARCERIA_DIRETA", "PROCACES – incentivo ao projeto \"Open Belas – 2ª edição – Torneio de Beach Tennis\"", "https://www.mineiros.go.gov.br/acesso-a-informacao/apoio-financeiro"],
["Mineiros", "2026-07-07", "Portal próprio (Convênios)", "PARCERIA_DIRETA", "Convênio – repasse ao Sindicato Rural de Mineiros (XLV Exposição Agropecuária)", "https://www.mineiros.go.gov.br/acesso-a-informacao/convenios"],
["Mineiros", "2026-05-06", "Portal próprio (PROCACES)", "PARCERIA_DIRETA", "Termos de Execução Cultural – apoio a 15+ projetos culturais (edital cultural 2025)", "https://www.mineiros.go.gov.br/acesso-a-informacao/apoio-financeiro"],
["Mineiros", "2026", "Portal próprio (PROCACES)", "OPORTUNIDADE_OSC", "PROCACES – Programa de Incentivo a Projetos Culturais, Artísticos, Científicos, Esportivos e Sociais: fluxo contínuo (89 decisões em 2026)", "https://www.mineiros.go.gov.br/acesso-a-informacao/apoio-financeiro"],
["Novo Gama", "2026-07-10", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "PNAB – segundo ciclo, inscrições abertas", "https://www.novogama.go.gov.br/noticia/2168-poltica-nacional-aldir-blanc-de-fomento--cultura-pnab---segundo-ciclo-inscries-abertas"],
["Novo Gama", "2026-02-13", "Portal próprio (notícias)", "OPORTUNIDADE_OSC", "Edital nº 001/2026 – Chamamento Público (Promoção Social e Cidadania)", "https://www.novogama.go.gov.br/noticia/1982-edital-n-0012026-chamamento-pblico"],
["Novo Gama", "2026-01-06", "Portal próprio (notícias)", "CMDCA_FIA", "Resolução CMDCA nº 001/2026", "https://www.novogama.go.gov.br/noticia/1949-resoluo-cmdca-n-0012026"],
["Novo Gama", "2025-09-09", "Portal próprio (notícias)", "ATO_DO_EDITAL", "Retificação do Edital nº 01/2025 (Defesa da Mulher)", "https://www.novogama.go.gov.br/noticia/1834-retificao-da-publicao-do-edital-n-012025-"],
["Novo Gama", "2025-08-22", "Portal próprio (notícias)", "OPORTUNIDADE_OSC", "Chamamento Público: Edital nº 001/2025 (Defesa da Mulher e da Diversidade Social)", "https://www.novogama.go.gov.br/noticia/1810-chamamento-pblico-edital-n-0012025"],
["Novo Gama", "2025-08-21", "Portal próprio (notícias)", "CMDCA_FIA", "Resolução 009/2025 – CMDCA", "https://www.novogama.go.gov.br/noticia/1806-resoluo-0092025---cmdca"],
["Novo Gama", "2025-05-07", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "Edital 07 de premiação da PNAB", "https://www.novogama.go.gov.br/noticia/1685-edital-07-de-premiao-da-pnab"],
["Novo Gama", "2025-05-06", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "Editais 05 e 06 – PNAB", "https://www.novogama.go.gov.br/noticia/1679-edital-05-e-06---pnab"],
["Novo Gama", "2025-04-07", "Portal próprio (notícias)", "RESULTADO", "Resultado preliminar da análise de mérito cultural da PNAB", "https://www.novogama.go.gov.br/noticia/1654-resultado-preliminar-da-analise-de-merito-cultural-da-pnab---novo-gama"],
["Novo Gama", "2025-02-11", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "PNAB – Edital de Chamamento Público nº 01/2025", "https://www.novogama.go.gov.br/noticia/1604-pnab---edital-de-chamamento-pblico-n-012025"],
["Novo Gama", "2025-02-03", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "Editais PNAB – Política Nacional Aldir Blanc", "https://www.novogama.go.gov.br/noticia/1595-editais-pnab---poltica-nacional-aldir-blanc-"],
["Novo Gama", "2024-12-03", "Portal próprio (notícias)", "RESULTADO", "Resultado final do edital de premiação LPG 002/2024", "https://www.novogama.go.gov.br/noticia/1557-publicao-e-homologao-do-resultado-final-do-edital-de-premiao-lpg-0022024"],
["Novo Gama", "2024-10-30", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 002/2024 – Lei Paulo Gustavo", "https://www.novogama.go.gov.br/noticia/1530-edital-de-chamamento-pblico-n-0022024---lei-paulo-gustavo-"],
["Novo Gama", "2024-01-05", "Portal próprio (notícias)", "RESULTADO", "Resultado final do edital – Lei Paulo Gustavo", "https://www.novogama.go.gov.br/noticia/1267-publicao-do-resultado-final-do-edital---lei-paulo-gustavo"],
["Novo Gama", "2023-11-06", "Portal próprio (notícias)", "OPORTUNIDADE_CULTURA", "Edital e orientação para inscrição – Lei Paulo Gustavo", "https://www.novogama.go.gov.br/noticia/1197-edital-e-orientao-para-inscrio---lei-paulo-gustavo"],
["Planaltina", "2026-09-08", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público nº 06/2026 – Processo 23713/2026", "https://www.planaltina.go.gov.br/chamamento-publico-no-06-2026-processo-no-23713-2026/"],
["Planaltina", "2026-05-12", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público 05/2026 – Processo 14067/2026", "https://www.planaltina.go.gov.br/chamamento-publico-05-2026-processo-no-14067-2026/"],
["Planaltina", "2026-04-06", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital Chamamento Público 04/2026", "https://www.planaltina.go.gov.br/edital-chamamento-publico-04-2026/"],
["Planaltina", "2026-03-04", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público 03/2026", "https://www.planaltina.go.gov.br/chamamento-publico-03-2026/"],
["Planaltina", "2026-03-02", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público 02/2026", "https://www.planaltina.go.gov.br/chamamento-publico-02-2026/"],
["Planaltina", "2026-02-09", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público 01/2026", "https://www.planaltina.go.gov.br/chamamento-publico-01-2026/"],
["Planaltina", "2025-12-01", "Site municipal (WordPress)", "CMDCA_FIA", "CMDCA publica edital de chamamento para custeio de projetos voltados a crianças e adolescentes", "https://www.planaltina.go.gov.br/cmdca-de-planaltina-go-publica-edital-de-chamamento-publico-para-custeio-de-projetos-voltados-a-criancas-e-adolescentes/"],
["Planaltina", "2025-04-01", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital Chamamento Público 04/2025", "https://www.planaltina.go.gov.br/edital-chamamento-publico-04-2025/"],
["Planaltina", "2025-03-31", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 03/2025", "https://www.planaltina.go.gov.br/edital-de-chamamento-publico-no-03-2025/"],
["Planaltina", "2025-03-11", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital Chamamento Público 02/2025", "https://www.planaltina.go.gov.br/edital-chamamento-publico-02-2025/"],
["Planaltina", "2024-04-08", "Site municipal (WordPress)", "CMDCA_FIA", "Edital de Chamamento Público FIA nº 001/2024", "https://www.planaltina.go.gov.br/edital-de-chamamento-publico-fia-n-001-2024/"],
["Planaltina", "2024-03-13", "Site municipal (WordPress)", "RESULTADO", "Resultado final – seleção de projetos (Lei Paulo Gustavo, LC 195/2022)", "https://www.planaltina.go.gov.br/comunicado-resultado-final-da-lei-complementar-no-195-2023-lei-paulo-gustavo/"],
["Quirinópolis", "2024-12-04", "Site municipal (WordPress)", "RESULTADO", "Resultado pós-recurso da análise de mérito – Lei Complementar Aldir Blanc", "https://www.quirinopolis.go.gov.br/confira-o-resultado-pos-recurso-da-analise-de-merito-da-lei-complementar-aldir-blanc/"],
["Quirinópolis", "2023-10-23", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Editais da Lei Paulo Gustavo abertos até 3/11", "https://www.quirinopolis.go.gov.br/editais-da-lei-paulo-gustavo-estao-abertos-para-inscricoes-ate-o-dia-3-de-novembro/"],
["Rio Verde", "2026-08-18", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Extrato – justificativa de inexigibilidade de chamamento público", "https://www.rioverde.go.gov.br/extrato-justificativa-de-inexigibilidade-de-chamamento-publico-4/"],
["Rio Verde", "2026-07-24", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Extrato – justificativa de inexigibilidade de chamamento público", "https://www.rioverde.go.gov.br/extrato-justificativa-de-inexigibilidade-de-chamamento-publico-3/"],
["Rio Verde", "2026-03-23", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Extrato – justificativa de inexigibilidade de chamamento público", "https://www.rioverde.go.gov.br/extrato-justificativa-de-inexigibilidade-de-chamamento-publico-2/"],
["Rio Verde", "2025-09-03", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público 004/2025", "https://www.rioverde.go.gov.br/edital-de-chamamento-publico-004-2025/"],
["Rio Verde", "2025-07-31", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Extrato – justificativa de inexigibilidade de chamamento público", "https://www.rioverde.go.gov.br/extrato-justificativa-de-inexigibilidade-de-chamamento-publico/"],
["Rio Verde", "2025-03-17", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Extrato – justificativa de inexigibilidade de chamamento público (P.A. 29.765/2025)", "https://www.rioverde.go.gov.br/extrato-justificativa-de-inexigibilidade-de-chamamento-publico-p-a-29-765-2025/"],
["Rio Verde", "2025-02-20", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Chamamento público para execução de ações culturais – PNAB", "https://www.rioverde.go.gov.br/chamamento-publico-para-execucao-de-acoes-culturais-com-recursos-da-politica-nacional-aldir-blanc-de-fomento-a-cultura-pnab/"],
["Rio Verde", "2024-10-21", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público", "https://www.rioverde.go.gov.br/chamamento-publico-2/"],
["Rio Verde", "2024-06-18", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Extrato e justificativa de inexigibilidade de chamamento público", "https://www.rioverde.go.gov.br/extrato-e-justificativa-de-inexigibilidade-de-chamamento-publico/"],
["Rio Verde", "2023-10-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Inscrições para artistas – Lei Paulo Gustavo (recursos acima de R$ 1,6 milhão)", "https://www.rioverde.go.gov.br/inscricoes-para-artistas-interessados-na-lei-paulo-gustavo-comecam-nesta-quarta-em-rio-verde-recursos-passam-de-r-16-milhao/"],
["Santo Antônio do Descoberto", "2026-04-30", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 002/2026", "https://www.santoantoniododescoberto.go.gov.br/edital-de-chamamento-publico-n-002-2026/"],
["Santo Antônio do Descoberto", "2026-04-30", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 001/2026", "https://www.santoantoniododescoberto.go.gov.br/edital-de-chamamento-publico-n-001-2026/"],
["Santo Antônio do Descoberto", "2025-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de chamamento público 01/2025 – Cultura", "https://www.santoantoniododescoberto.go.gov.br/edital-de-chamamento-publico-01-2025-cultura/"],
["Santo Antônio do Descoberto", "2025-07-03", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 01/2025 do CMDM", "https://www.santoantoniododescoberto.go.gov.br/edital-de-chamamento-publico-n-01-2025-do-cmdm/"],
["Santo Antônio do Descoberto", "2024-08-08", "Site municipal (WordPress)", "PARCERIA_DIRETA", "Apostilamento ao Termo de Colaboração nº 001/2023/SMS-FMS", "https://www.santoantoniododescoberto.go.gov.br/apostilamento-ao-termo-de-colaboracao-n-001-2023-sms-fms/"],
["Santo Antônio do Descoberto", "2024-03-08", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 02/2024 – Culturas", "https://www.santoantoniododescoberto.go.gov.br/edital-de-chamamento-publico-no-02-2024-culturas/"],
["Santo Antônio do Descoberto", "2023-11-20", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Chamamento Público nº 09/2023 (Lei Paulo Gustavo) – Cultura", "https://www.santoantoniododescoberto.go.gov.br/chamamento-publico-n-09-2023-lei-paulo-gustavo-cultura/"],
["Santo Antônio do Descoberto", "2023-10-18", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 005/2023/SMS-FMS", "https://www.santoantoniododescoberto.go.gov.br/edital-de-chamamento-publico-no-005-2023-sms-fms/"],
["Senador Canedo", "2026-09-08", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital Aldir Blanc 2026 – R$ 380 mil para projetos culturais", "https://www.senadorcanedo.go.gov.br/prefeitura-de-senador-canedo-lanca-edital-aldir-blanc-2026/"],
["Senador Canedo", "2026-06-25", "Site municipal (WordPress)", "CMDCA_FIA", "SEMASC abre chamamento para seleção de projetos de proteção de crianças e adolescentes", "https://www.senadorcanedo.go.gov.br/semasc-abre-chamamento-publico-para-selecao-de-projetos-voltados-a-protecao-de-criancas-e-adolescentes/"],
["Senador Canedo", "2025-06-30", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital \"Memória, Patrimônio e Cultura\"", "https://www.senadorcanedo.go.gov.br/ultimo-dia-de-inscricoes-para-o-edital-memoria-patrimonio-e-cultura/"],
["Senador Canedo", "2025-04-30", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "2ª Chamada da Lei Aldir Blanc", "https://www.senadorcanedo.go.gov.br/inscricoes-da-2a-chamada-da-lei-aldir-blanc-comecam-nesta-quinta-feira-em-senador-canedo/"],
["Senador Canedo", "2025-04-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 003/2024 – 2ª convocação / Fomento", "https://www.senadorcanedo.go.gov.br/edital-de-chamamento-publico-no-003-2024-2a-convocacao-fomento/"],
["Senador Canedo", "2025-04-09", "Site municipal (WordPress)", "RESULTADO", "Resultados do Edital de Chamamento Público nº 009/2024 – Iamesc", "https://www.senadorcanedo.go.gov.br/resultado-iamesc/"],
["Senador Canedo", "2024-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital nº 03/2024 – Fomento (PNAB)", "https://www.senadorcanedo.go.gov.br/edital-no03-2024-fomento/"],
["Senador Canedo", "2024-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "PNAB – Edital nº 05/2024 – Cultura Viva", "https://www.senadorcanedo.go.gov.br/politica-nacional-aldir-blanc-edital-no05-2024-cultura-viva/"],
["Senador Canedo", "2024-10-02", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "PNAB – Edital nº 04/2024", "https://www.senadorcanedo.go.gov.br/politica-nacional-aldir-blanc-edital-no03-2024-fomento/"],
["Senador Canedo", "2024-08-07", "Site municipal (WordPress)", "RESULTADO", "Chamada Pública nº 001/2024 – entidades prestadoras de serviços de saúde – resultados", "https://www.senadorcanedo.go.gov.br/edital-de-chamada-publica-no-001-2024-de-entidade-prestadoras-de-servicos-de-assistencia-a-saude-resultados/"],
["Senador Canedo", "2024-04-30", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Convocação nº 001/2024 – Lei Paulo Gustavo (demais áreas)", "https://www.diariomunicipal.com.br/agm/materia/EF8095B7"],
["Senador Canedo", "2024-04-30", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Convocação nº 001/2024 – Lei Paulo Gustavo (audiovisual)", "https://www.diariomunicipal.com.br/agm/materia/E9902A1F"],
["Senador Canedo", "2024-04-15", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Resultado preliminar de habilitação – Editais 001 a 003/2024 (Lei Paulo Gustavo)", "https://www.diariomunicipal.com.br/agm/materia/5AB465EE"],
["Senador Canedo", "2024-03-25", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Resultado da análise de mérito – Editais 001 a 003/2024 (Lei Paulo Gustavo)", "https://www.diariomunicipal.com.br/agm/materia/B7FF0180"],
["Senador Canedo", "2024-03-20", "Diário AGM (diariomunicipal.com.br/agm)", "ATO_DO_EDITAL", "Errata de cronograma – Editais 007 e 008/2024 (Lei Paulo Gustavo)", "https://www.diariomunicipal.com.br/agm/materia/B23F8958"],
["Senador Canedo", "2024-02-06", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Credenciamento na Lei Paulo Gustavo", "https://www.senadorcanedo.go.gov.br/inscricoes-abertas-para-credenciamento-na-lei-paulo-gustavo-em-senador-canedo/"],
["Trindade", "2026-09-15", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.518/2026", "https://www.diariomunicipal.com.br/agm/materia/8BC44443"],
["Trindade", "2026-08-12", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Errata ao resultado da habilitação – Edital de Chamamento Público nº 002/2026 (Cultura)", "https://www.diariomunicipal.com.br/agm/materia/BC370AAC"],
["Trindade", "2026-07-15", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Resultado pós-recurso da habilitação – PNAB", "https://www.diariomunicipal.com.br/agm/materia/63022029"],
["Trindade", "2026-06-29", "Diário AGM (diariomunicipal.com.br/agm)", "CMDCA_FIA", "Edital 001/2026/CMDCA – resultado final das habilitações", "https://www.diariomunicipal.com.br/agm/materia/50216CE5"],
["Trindade", "2026-06-24", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.510/2026 (PNAB, Lei 14.399/2022)", "https://www.diariomunicipal.com.br/agm/materia/44E4C97E"],
["Trindade", "2026-06-17", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.501/2026 – autoriza convênios e parcerias com OSCs", "https://www.diariomunicipal.com.br/agm/materia/3D304AA9"],
["Trindade", "2026-06-15", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Resultado final da análise de mérito – PNAB", "https://www.diariomunicipal.com.br/agm/materia/FD9C21BE"],
["Trindade", "2026-06-04", "Diário AGM (diariomunicipal.com.br/agm)", "CMDCA_FIA", "Edital de recomposição do CMDCA (sociedade civil)", "https://www.diariomunicipal.com.br/agm/materia/E1410CF6"],
["Trindade", "2026-06-03", "Site municipal (WordPress)", "CMDCA_FIA", "Edital nº 001/2026/CMDCA", "https://www.trindade.go.gov.br/edital-no-001-2026-cmdca/"],
["Trindade", "2026-05-21", "Diário AGM (diariomunicipal.com.br/agm)", "ATO_DO_EDITAL", "Prorrogação de prazo e retificação nº 02/2026 – editais PNAB ciclo 2", "https://www.diariomunicipal.com.br/agm/materia/0F8A937E"],
["Trindade", "2026-05-06", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.487/2026 – execução por parcerias com organizações", "https://www.diariomunicipal.com.br/agm/materia/51FDF40A"],
["Trindade", "2026-04-28", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Lançamento do edital da PNAB", "https://www.trindade.go.gov.br/prefeitura-de-trindade-lanca-edital-da-pnab-com-participacao-de-autoridades-e-segmento-cultural/"],
["Trindade", "2025-12-18", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.463/2025 – entidades e OSCs", "https://www.diariomunicipal.com.br/agm/materia/65C11B27"],
["Trindade", "2025-12-18", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.465/2025", "https://www.diariomunicipal.com.br/agm/materia/AA514CB3"],
["Trindade", "2025-12-15", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_OSC", "Edital nº 01/2025 dos Conselhos Municipais (CMAS/CMDPI) – inscrição de programas e projetos", "https://www.diariomunicipal.com.br/agm/materia/BAAECEC7"],
["Trindade", "2025-11-04", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.453/2025 – repasse às organizações por termo", "https://www.diariomunicipal.com.br/agm/materia/CB02A3E8"],
["Trindade", "2025-10-22", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.451/2025 – convênios e parcerias com OSCs", "https://www.diariomunicipal.com.br/agm/materia/92DC0C18"],
["Trindade", "2025-06-06", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Chamamento – aviso de escuta pública nº 002/2025 – PNAB", "https://www.diariomunicipal.com.br/agm/materia/648103DA"],
["Trindade", "2025-04-01", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Termo de subvenção (convênio)", "https://www.diariomunicipal.com.br/agm/materia/1789E59A"],
["Trindade", "2025-02-14", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Lista homologatória – 2ª chamada de suplentes (Lei Complementar Aldir Blanc)", "https://www.diariomunicipal.com.br/agm/materia/2F15A35A"],
["Trindade", "2024-10-31", "Site municipal (WordPress)", "RESULTADO", "83 artistas contemplados com recursos da Lei Aldir Blanc", "https://www.trindade.go.gov.br/83-artistas-trindadenses-sao-contemplados-com-recursos-da-lei-aldir-blanc/"],
["Trindade", "2024-10-30", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Lista homologatória – editais de fomento 03/2024 e premiação 04/2024 (Aldir Blanc)", "https://www.diariomunicipal.com.br/agm/materia/00607189"],
["Trindade", "2024-10-09", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Cronograma de reabertura do Edital 05/2024 – Cultura Viva", "https://www.diariomunicipal.com.br/agm/materia/7F20DA13"],
["Trindade", "2024-06-05", "Diário AGM (diariomunicipal.com.br/agm)", "ACOMPANHAR", "Lei nº 2.333/2024 – certificação de Pontos de Cultura", "https://www.diariomunicipal.com.br/agm/materia/DAA0285A"],
["Trindade", "2024-05-07", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público 01/2024", "https://www.trindade.go.gov.br/edital-de-chamamento-publico-01-2024/"],
["Trindade", "2024-02-22", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Aditivo de prazo – termo de convênio", "https://www.diariomunicipal.com.br/agm/materia/7166081B"],
["Trindade", "2023-12-08", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 04/2023 (Turismo e Cultura)", "https://www.diariomunicipal.com.br/agm/materia/A07567DF"],
["Trindade", "2023-12-08", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 03/2023 (Turismo e Cultura)", "https://www.diariomunicipal.com.br/agm/materia/B299C8AB"],
["Trindade", "2023-11-08", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_OSC", "Edital de Chamamento nº 001/2023 – Secretaria de Assistência Social", "https://www.diariomunicipal.com.br/agm/materia/4B8FCA1E"],
["Trindade", "2023-10-26", "Diário AGM (diariomunicipal.com.br/agm)", "CMDCA_FIA", "Edital de convocação nº 007/2023 – CMDCA", "https://www.diariomunicipal.com.br/agm/materia/1BC204E9"],
["Valparaíso de Goiás", "2026-07-09", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Inscrições para 12 editais da PNAB", "https://www.valparaisodegoias.go.gov.br/cultura-abre-inscricoes-para-12-editais-da-pnab-em-valparaiso-de-goias/"],
["Valparaíso de Goiás", "2026-05-21", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Novos editais do ciclo 2 da PNAB com inscrições abertas", "https://www.valparaisodegoias.go.gov.br/novos-editais-do-ciclo-2-da-pnab-estao-com-inscricoes-abertas/"],
["Valparaíso de Goiás", "2026-04-08", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Lançamento dos editais da PNAB para diversos segmentos culturais", "https://www.valparaisodegoias.go.gov.br/valparaiso-lanca-editais-da-pnab-com-inscricoes-abertas-para-diversos-segmentos-culturais/"],
["Valparaíso de Goiás", "2025-05-21", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Credenciamento para parceria com instituições nas áreas de cultura e esporte", "https://www.valparaisodegoias.go.gov.br/aberto-credenciamento-para-parceria-com-instituicoes-nas-areas-de-cultura-e-esporte/"],
["Valparaíso de Goiás", "2024-10-29", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Editais para seleção de projetos culturais da PNAB", "https://www.valparaisodegoias.go.gov.br/prefeitura-de-valparaiso-publica-editais-para-selecao-de-projetos-culturais-da-politica-nacional-aldir-blanc-pnab/"],
["Águas Lindas de Goiás", "2026-09-22", "Diário AGM (diariomunicipal.com.br/agm)", "ATO_DO_EDITAL", "Extrato da Retificação nº 03/2026 dos Editais PNAB 01 a 04/2026", "https://www.diariomunicipal.com.br/agm/materia/4F162A9F"],
["Águas Lindas de Goiás", "2026-09-21", "Diário AGM (diariomunicipal.com.br/agm)", "PARCERIA_DIRETA", "Extrato de Termo de Colaboração 01/2026 – SEMOB", "https://www.diariomunicipal.com.br/agm/materia/3CCB9E42"],
["Águas Lindas de Goiás", "2026-08-07", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Divulgação de OSC com credenciamento deferido após recurso – SEMOB", "https://www.diariomunicipal.com.br/agm/materia/617777C4"],
["Águas Lindas de Goiás", "2026-08-03", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 01/2026 – projetos culturais PNAB", "https://www.diariomunicipal.com.br/agm/materia/EB8E79F2"],
["Águas Lindas de Goiás", "2026-08-03", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 02/2026 – projetos culturais PNAB", "https://www.diariomunicipal.com.br/agm/materia/68645187"],
["Águas Lindas de Goiás", "2026-08-03", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 03/2026 – projetos culturais PNAB", "https://www.diariomunicipal.com.br/agm/materia/927604F8"],
["Águas Lindas de Goiás", "2026-08-03", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público nº 04/2026 – projetos culturais PNAB", "https://www.diariomunicipal.com.br/agm/materia/0BA991F8"],
["Águas Lindas de Goiás", "2026-07-27", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Secretaria de Cultura e Turismo inaugura Plataforma Cultural e abre editais do ciclo PNAB 2026", "https://aguaslindasdegoias.go.gov.br/ciclo-pnab-2026-tem-inicio-com-lancamento-da-plataforma-cultural-e-abertura-das-inscricoes/"],
["Águas Lindas de Goiás", "2026-07-27", "Diário AGM (diariomunicipal.com.br/agm)", "ATO_DO_EDITAL", "Ata da comissão de seleção de propostas de OSCs – SEMOB", "https://www.diariomunicipal.com.br/agm/materia/5F9A988E"],
["Águas Lindas de Goiás", "2026-07-23", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Lista de OSCs com credenciamento – SEMOB", "https://www.diariomunicipal.com.br/agm/materia/8A1836AB"],
["Águas Lindas de Goiás", "2026-03-19", "Site municipal (WordPress)", "CONSELHO", "Edital de Chamamento nº 01/2026 – seleção de representantes da sociedade civil no Conselho Municipal dos Direitos das Mulheres", "https://aguaslindasdegoias.go.gov.br/secretaria-da-mulher-publica-edital-de-chamamento-no-01-2026-para-selecao-de-representantes-da-sociedade-civil-no-conselho-municipal-dos-direitos-das-mulheres/"],
["Águas Lindas de Goiás", "2025-09-09", "Site municipal (WordPress)", "CMDCA_FIA", "CMDCA publica Edital de Chamamento Público – Chancela nº 01/2025", "https://aguaslindasdegoias.go.gov.br/o-conselho-municipal-da-crianca-e-do-adolescente-cmdca-publica-edital-de-chamamento-publico-chancela-no-01-2025/"],
["Águas Lindas de Goiás", "2025-08-28", "Site municipal (WordPress)", "RESULTADO", "Resultado definitivo do chamamento para pré-qualificação de OSCs (Educação)", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-por-meio-da-secretaria-de-educacao-torna-publico-o-resultado-definitivo-do-chamamento-publico-para-a-pre-qualificacao-de-organizacoes-da-sociedade-civil-oscs/"],
["Águas Lindas de Goiás", "2025-08-20", "Site municipal (WordPress)", "RESULTADO", "Resultado preliminar do chamamento para pré-qualificação de OSCs (Educação)", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-por-meio-da-secretaria-de-educacao-torna-publico-o-resultado-preliminar-do-chamamento-para-pre-qualificacao-de-organizacoes-da-sociedade-civil-osc/"],
["Águas Lindas de Goiás", "2025-08-05", "Site municipal (WordPress)", "ACOMPANHAR", "Formulário de cadastramento de agentes culturais – 2º ciclo PNAB", "https://aguaslindasdegoias.go.gov.br/a-secretaria-de-cultura-disponibiliza-formulario-de-cadastramento-de-agentes-culturais-para-o-2o-ciclo-da-politica-nacional-aldir-blanc-de-fomento-a-cultura/"],
["Águas Lindas de Goiás", "2025-07-18", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público 004/2025 (Educação)", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-por-meio-da-secretaria-de-educacao-torna-publico-o-presente-edital-de-chamamento-publico-004-2025/"],
["Águas Lindas de Goiás", "2025-07-08", "Site municipal (WordPress)", "ATO_DO_EDITAL", "Revogação do Edital de Chamamento Público 003/2025 (Educação)", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-por-meio-da-secretaria-de-educacao-divulga-a-revogacao-do-edital-de-chamamento-publico-003-2025/"],
["Águas Lindas de Goiás", "2025-06-23", "Site municipal (WordPress)", "RESULTADO", "Resultado preliminar do Edital de Chamamento Público 003/2025 (Educação)", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-por-meio-da-secretaria-de-educacao-divulga-o-resultado-preliminar-do-edital-de-chamamento-publico-003-2025/"],
["Águas Lindas de Goiás", "2025-06-10", "Site municipal (WordPress)", "RESULTADO", "Resultado definitivo do Edital de Chamamento Público nº 01/2025 (Esporte)", "https://aguaslindasdegoias.go.gov.br/prefeitura-de-aguas-lindas-por-intermedio-da-secretaria-de-esporte-torna-publico-o-resultado-definitivo-do-edital-de-chamamento-publico-no01-2025/"],
["Águas Lindas de Goiás", "2025-05-16", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público 003/2025 (Educação)", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-por-meio-da-secretaria-de-educacao-torna-publico-o-edital-de-chamamento-publico-003-2025/"],
["Águas Lindas de Goiás", "2025-03-20", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público (Esporte) – seleção de OSC para termo de colaboração", "https://aguaslindasdegoias.go.gov.br/prefeitura-de-aguas-lindas-por-intermedio-da-secretaria-de-esporte-torna-publico-o-edital-de-chamamento-publico-visando-a-selecao-de-organizacao-da-sociedade-civil-interessada-em-celebrar-termo-de-c/"],
["Águas Lindas de Goiás", "2024-12-18", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento Público nº 08/2024 (Educação)", "https://aguaslindasdegoias.go.gov.br/a-secretaria-de-educacao-torna-publico-e-de-conhecimento-o-edital-de-chamamento-publico-n-o-08-2024/"],
["Águas Lindas de Goiás", "2024-11-29", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Credenciamento Público nº 02902419/2024 – Natal Luz e Prêmios 2024", "https://aguaslindasdegoias.go.gov.br/a-secretaria-de-cultura-torna-publico-o-edital-de-abertura-credenciamento-publico-no-02902419-2024-natal-luz-e-premios-2024/"],
["Águas Lindas de Goiás", "2024-10-31", "Site municipal (WordPress)", "RESULTADO", "Lista final de contemplados – Editais SECTUR/PNAB 2024", "https://aguaslindasdegoias.go.gov.br/cultura-e-turismo-torna-publica-a-lista-final-de-contemplados-com-os-respectivos-valores-a-serem-recebidos-conforme-ajuste-de-pagamento-n-o-0264520-editais-sectur-pnab-2024/"],
["Águas Lindas de Goiás", "2024-10-02", "Site municipal (WordPress)", "RESULTADO", "Homologação dos resultados dos Editais 002 a 005/2024 – Chamamento SECTUR/PNAB", "https://aguaslindasdegoias.go.gov.br/cultura-e-turismo-torna-publico-o-termo-de-homologacao-dos-resultados-dos-editais-n-o-002-003-004-e-005-2024-chamamento-publico-sectur-pnab/"],
["Águas Lindas de Goiás", "2024-08-02", "Site municipal (WordPress)", "CMDCA_FIA", "Edital de Chamamento nº 02/2024 – entidades não governamentais para o CMDCA (biênio 2024–2026)", "https://aguaslindasdegoias.go.gov.br/a-secr-de-assistencia-social-torna-publico-edital-de-chamamento-n-o02-2024-das-entidades-nao-governamentais-para-composicao-do-cmdca-ges-bienio-2024-2026/"],
["Águas Lindas de Goiás", "2024-07-17", "Site municipal (WordPress)", "RESULTADO", "Homologação dos inscritos – Edital de Chamamento Público PNAB 001/2024", "https://aguaslindasdegoias.go.gov.br/cultura-e-turismo-torna-publico-a-homologacao-dos-inscritos-ao-edital-de-chamamento-publico-pnab-001-2024/"],
["Águas Lindas de Goiás", "2024-06-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Chamamento Público SECTUR/PNAB 005/2024", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-de-aguas-lindas-de-goias-por-meio-da-secretaria-municipal-de-cultura-torna-publico-o-chamamento-publico-sectur-pnab-005-2024/"],
["Águas Lindas de Goiás", "2024-06-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Chamamento Público SECTUR/PNAB 004/2024", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-de-aguas-lindas-de-goias-por-meio-da-secretaria-municipal-de-cultura-torna-publico-o-chamamento-publico-sectur-pnab-004-2024/"],
["Águas Lindas de Goiás", "2024-06-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público SECTUR/PNAB 003/2024", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-de-aguas-lindas-de-goias-por-meio-da-secretaria-municipal-de-cultura-torna-publico-o-edital-de-chamamento-publico-sectur-pnab-003-2024/"],
["Águas Lindas de Goiás", "2024-06-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público SECTUR/PNAB 002/2024", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-de-aguas-lindas-de-goias-por-meio-da-secretaria-municipal-de-cultura-torna-publico-o-edital-de-chamamento-publico-pnab-no02-2024/"],
["Águas Lindas de Goiás", "2024-06-25", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital de Chamamento Público SECTUR/PNAB 001/2024", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-de-aguas-lindas-de-goias-por-meio-da-secretaria-municipal-de-cultura-torna-publico-o-edital-de-chamamento-publico-no01-2024/"],
["Águas Lindas de Goiás", "2024-06-14", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público nº 03/2024 – credenciamento de instituições privadas sem fins lucrativos/filantrópicas (Saúde)", "https://aguaslindasdegoias.go.gov.br/prefeitura-de-aguas-lindas-torna-publico-o-instrumento-de-chamamento-publico-n-o-03-2024-contratacao-da-organizacao-social-de-saude-osc-para-infermeiros-e-tecnicos/"],
["Águas Lindas de Goiás", "2024-06-14", "Diário AGM (diariomunicipal.com.br/agm)", "OPORTUNIDADE_OSC", "Convocação – Chamamento Público nº 02/2024 (Saúde)", "https://www.diariomunicipal.com.br/agm/materia/4BD58001"],
["Águas Lindas de Goiás", "2024-05-17", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Chamamento Público nº 02/2024 – seleção de Organização Social de Saúde (HMBJ e UPA)", "https://aguaslindasdegoias.go.gov.br/prefeitura-de-aguas-lindas-torna-publico-o-instrumento-de-chamamento-publico-n-o-02-2024-destinado-a-selecao-de-organizacao-social-de-saude-hmbj-e-upa-mansoes-odisseia/"],
["Águas Lindas de Goiás", "2024-02-28", "Site municipal (WordPress)", "CONSELHO", "Edital de Chamamento nº 002/2024 – eleição de conselheiros da sociedade civil (Conselho de Cultura)", "https://aguaslindasdegoias.go.gov.br/edital-de-chamamento-publico-n-o-002-2024-processo-de-convocacao-e-eleicao-dos-conselheiros-representantes-da-sociedade-civil-para-composicao-do-conselho-municipal-de-cultura/"],
["Águas Lindas de Goiás", "2024-01-31", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de Chamamento nº 001/2024 – Secretaria da Mulher e Família", "https://aguaslindasdegoias.go.gov.br/edital-de-chamamento-no-001-2024-secretaria-da-mulher-e-familia/"],
["Águas Lindas de Goiás", "2023-12-07", "Site municipal (WordPress)", "OPORTUNIDADE_OSC", "Edital de convocação para qualificação de Organização Social de Saúde", "https://aguaslindasdegoias.go.gov.br/edital-de-convocacao-para-qualificacao-de-organizacao-social-de-saude/"],
["Águas Lindas de Goiás", "2023-11-30", "Diário AGM (diariomunicipal.com.br/agm)", "RESULTADO", "Resultado final e homologação – editais da Lei Paulo Gustavo", "https://www.diariomunicipal.com.br/agm/materia/022628CB"],
["Águas Lindas de Goiás", "2023-11-21", "Site municipal (WordPress)", "RESULTADO", "Resultado final dos Editais 001, 002 e 003 da Lei Paulo Gustavo", "https://aguaslindasdegoias.go.gov.br/a-prefeitura-municipal-de-aguas-lindas-de-goias-por-meio-da-secretaria-municipal-de-cultura-e-turismo-torna-publico-o-resultado-final-dos-editais-no001-002-e-003-da-lei-paulo-gustavo/"],
["Águas Lindas de Goiás", "2023-11-13", "Site municipal (WordPress)", "RESULTADO", "Edital de publicação da lista de entidades habilitadas", "https://aguaslindasdegoias.go.gov.br/edital-de-publicacao-da-lista-de-entidades-habilitadas/"],
["Águas Lindas de Goiás", "2023-10-27", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital nº 002/2023 LPG – demais áreas culturais (retificação)", "https://aguaslindasdegoias.go.gov.br/edital-no-002-2023-lpg-demais-areas-culturais-paulo-gustavo/"],
["Águas Lindas de Goiás", "2023-10-27", "Site municipal (WordPress)", "OPORTUNIDADE_CULTURA", "Edital nº 001/2023 LPG – seleção de projetos para capacitação audiovisual (retificação)", "https://aguaslindasdegoias.go.gov.br/edital-no-001-2023-lpg-para-selecao-de-projetos-para-capacitacao-audiovisual/"]
]''')


# ════════════════════════════════════════════════ UTILITÁRIOS ═══════════════════════════════════════════════════════
def _j(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def sem(t) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(t or "").lower()) if not unicodedata.combining(c))


def limpar(html) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", str(html or "")))).strip()


def config() -> dict:
    c = _j(CFG, None)
    return c if isinstance(c, dict) and c.get("municipios") else CONFIG_PADRAO


def _get(url: str, timeout: float = 25) -> tuple[int, str, dict]:
    from . import ponte_brasil
    if ponte_brasil.usar(url):                            # 03/10 (titular): sites *.go.gov.br pela ponte da Hostgator
        try:
            st, _f, corpo, hdr = ponte_brasil.abrir(url, timeout=int(timeout) + 15)
            return st, corpo.decode("utf-8", "ignore"), hdr
        except Exception as e:  # noqa: BLE001
            return 0, f"ponte Brasil: {type(e).__name__}: {e}"[:200], {}
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/html;q=0.9,*/*;q=0.5",
                                               "Accept-Language": "pt-BR,pt;q=0.9", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            b = r.read(6_000_000)
            if (r.headers.get("Content-Encoding") or "") == "gzip":
                b = gzip.decompress(b)
            return r.status, b.decode("utf-8", "ignore"), {k.lower(): v for k, v in dict(r.headers).items()}
    except urllib.error.HTTPError as e:
        return e.code, "", {k.lower(): v for k, v in dict(e.headers or {}).items()}
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"[:200], {}


def _no_github_sem_brasil() -> bool:
    """No GitHub sem acesso ao Brasil: sem coleta local e sem a ponte da Hostgator configurada (03/10)."""
    if not (os.environ.get("GITHUB_ACTIONS") and not os.environ.get("ELDORADO_LOCAL_BR")):
        return False
    from . import ponte_brasil
    return not ponte_brasil.configurada()


def _exige_brasil(url: str) -> bool:
    h = (urllib.parse.urlsplit(url).hostname or "").lower()
    return h.endswith(".go.gov.br")


def _data_br(s: str) -> str:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def _id(*partes) -> str:
    return sha256("|".join(str(p) for p in partes).encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════ CLASSIFICAÇÃO ══════════════════════════════════════════════════════
def _prazo(txt: str, ref: date) -> date | None:
    t = sem(txt); cands = []
    for m in re.finditer(r"at[ée]\s+(?:o dia\s+)?(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", t):
        d, mo, a = int(m.group(1)), int(m.group(2)), m.group(3)
        ano = int(a) + (2000 if a and len(a) == 2 else 0) if a else ref.year
        cands.append((ano, mo, d))
    for m in re.finditer(r"at[ée]\s+(?:o dia\s+)?(\d{1,2})\s+de\s+([a-z]+)(?:\s+de\s+(\d{4}))?", t):
        mo = MESES.get(m.group(2))
        if mo:
            cands.append((int(m.group(3)) if m.group(3) else ref.year, mo, int(m.group(1))))
    out = []
    for a, mo, d in cands:
        try:
            x = date(a, mo, d)
            if x < ref - timedelta(days=5) and not re.search(r"\b20\d\d\b", t):
                x = date(a + 1, mo, d)
            out.append(x)
        except ValueError:
            pass
    return max(out) if out else None


def classificar(titulo: str, resumo: str = "", publicado: date | None = None, hoje: date | None = None, lex: dict | None = None) -> dict:
    """Uma publicação municipal → {veredito, categoria, motivo, prazo, aberta}. Só o título decide vetos e resultados;
    o resumo ajuda a achar o público (OSC) e o prazo."""
    lex = lex or config()["lexico"]; hoje = hoje or date.today()
    t = re.sub(r"^[\W_]+", "", sem(titulo)); s = sem(f"{titulo} . {resumo}")[:1200]   # 03/10: trecho do diário começa com "…"
    osc_forte = bool(re.search(lex["osc_forte"], s))
    if re.search(lex["agricultura"], t):
        return {"veredito": "ACOMPANHAR", "categoria": "AGRICULTURA_FAMILIAR", "motivo": "chamada da agricultura familiar (PAA/PNAE): só cooperativas e associações rurais"}
    for nome, rx, cede in lex["vetos"]:
        if re.search(rx, t) and not (cede and osc_forte):
            return {"veredito": "RUIDO", "categoria": "RUIDO", "motivo": f"veto: {nome}"}
    if re.search(lex["resultado"], t):
        return {"veredito": "ACOMPANHAR", "categoria": "RESULTADO", "motivo": "resultado, homologação ou lista de uma seleção já feita"}
    # 03/10 (teste do motor 13): título GENÉRICO ("EDITAL Nº 01/2025") — quem diz o que é o ato é o resumo. Trindade publicou
    # em 11/09/2026 a 3ª prorrogação do resultado do Edital 01/2025 (CMAS/CMDCA/CMDPI) e o motor marcou como seleção aberta.
    gen = re.fullmatch(r"(?:edital|aviso|comunicado)\b[^a-z0-9]{0,6}(?:n\S{0,2}\s*)?\d{1,4}\s*/\s*(\d{4})\.?", t.strip())
    if gen:
        r_ = sem(resumo)
        if re.search(lex["ato_do_edital"], r_) or re.search(lex["resultado"], r_):
            return {"veredito": "ACOMPANHAR", "categoria": "ATO_DO_EDITAL", "motivo": "título genérico e o texto é prorrogação, retificação ou resultado do edital"}
        if publicado and int(gen.group(1)) < publicado.year:
            return {"veredito": "ACOMPANHAR", "categoria": "ATO_DO_EDITAL",
                    "motivo": f"edital de {gen.group(1)} publicado de novo em {publicado.year}: ato posterior (prorrogação, resultado) — conferir"}
    abre = bool(re.search(lex["abertura"], t))
    osc = osc_forte or bool(re.search(lex["osc"], s))
    if abre and re.search(lex["ato_do_edital"], t):
        return {"veredito": "ACOMPANHAR", "categoria": "ATO_DO_EDITAL", "motivo": "retificação, prorrogação, errata ou revogação de edital"}
    if re.search(lex["parceria"], t) and (re.search(r"inexigibilidade|dispensa de chamamento|^extrato|^termo d|^contrato|^convenio|^c o n v|apostilamento|aditamento|aditivo ao termo", t)
                                          or not re.search(r"chamament|chamada publica|edital|selecao", t)):
        return {"veredito": "ACOMPANHAR", "categoria": "PARCERIA_DIRETA" if osc else "ACOMPANHAR",
                "motivo": "parceria celebrada sem disputa (fomento, colaboração, convênio, subvenção, inexigibilidade)" if osc else "ato de parceria sem público de entidades"}
    if re.search(lex["conselho"], t) and not re.search(r"projeto|fomento|colabora|financ|custeio|fia\b|fmdca", t):
        return {"veredito": "ACOMPANHAR", "categoria": "CONSELHO", "motivo": "vaga da sociedade civil em conselho (não é recurso)"}
    if abre and osc:
        pz = _prazo(f"{titulo} . {resumo}", publicado or hoje)
        cat = ("OPORTUNIDADE_CULTURA" if re.search(lex["cultura"], s) else
               "CMDCA_FIA" if re.search(lex["crianca"], s) else "OPORTUNIDADE_OSC")
        aberta = bool((pz and pz >= hoje) or (not pz and publicado and (hoje - publicado).days <= lex.get("dias_aberta_sem_prazo", 45)))
        return {"veredito": "OPORTUNIDADE", "categoria": cat, "motivo": "abertura de seleção com público de entidades/projetos",
                "prazo": pz.isoformat() if pz else None, "aberta": aberta}
    if abre:
        return {"veredito": "ACOMPANHAR", "categoria": "OUTRO_EDITAL", "motivo": "seleção sem público de entidades identificado"}
    if osc and re.search(lex["acompanhar"], s):
        return {"veredito": "ACOMPANHAR", "categoria": "ACOMPANHAR", "motivo": "sinal de recurso para entidades (fundo, emenda, programa)"}
    return {"veredito": "RUIDO", "categoria": "RUIDO", "motivo": "sem sinal de oportunidade"}


# ═════════════════════════════════════════════════ LEITORES ═════════════════════════════════════════════════════════
def _pub(cidade: str, rota: str, url: str, titulo: str, data: str = "", resumo: str = "") -> dict:
    return {"id": _id(rota, url), "cidade": cidade, "rota": rota, "url": url, "titulo": limpar(titulo)[:300],
            "data": (data or "")[:10], "resumo": limpar(resumo)[:900]}


def ler_wp(m: dict, cfg: dict, desde: str, fim: float, termos: list[str] | None = None, paginas: int | None = None) -> tuple[str, list[dict], dict]:
    """ROTA B — API do WordPress (posts e páginas)."""
    base = m["site"].rstrip("/"); w = cfg["wp"]; out = {}; vol = {}
    for termo in termos or w["termos"]:
        for tipo in w["tipos"]:
            for pg in range(1, (paginas or w["max_paginas"]) + 1):
                if time.time() > fim:
                    return "parcial (tempo)", list(out.values()), vol
                url = (f"{base}/wp-json/wp/v2/{tipo}?search={urllib.parse.quote(termo)}&after={desde}T00:00:00"
                       f"&per_page=100&page={pg}&_fields=id,date,title,excerpt,link")
                st, corpo, h = _get(url)
                if st in (401, 403):
                    return f"fechada (http {st})", list(out.values()), vol
                if st == 400:          # página além do fim
                    break
                if st != 200:
                    return (f"falhou (http {st})" if not out else "parcial"), list(out.values()), vol
                try:
                    lista = json.loads(corpo)
                except Exception:
                    return "falhou (resposta não é JSON)", list(out.values()), vol
                if pg == 1:
                    vol[f"{termo}/{tipo}"] = int(h.get("x-wp-total") or len(lista))
                for p in lista:
                    x = _pub(m["municipio"], "site (WordPress)", p.get("link") or "", (p.get("title") or {}).get("rendered", ""),
                             str(p.get("date") or "")[:10], (p.get("excerpt") or {}).get("rendered", ""))
                    out.setdefault(x["url"], x)
                time.sleep(cfg["pausa_segundos"])
                if len(lista) < 100:
                    break
    return ("lida" if out else "vazia"), list(out.values()), vol


_AGM_CARD = re.compile(r'<li[^>]*class="[^"]*materia-card[^"]*"[^>]*>(.*?)</li>', re.S | re.I)


def parse_agm(html: str, cidade: str) -> tuple[int, list[dict]]:
    tot = re.search(r"([\d.]+)\s*mat[ée]rias", limpar(html), re.I)
    out = []
    for bloco in _AGM_CARD.findall(html):
        cod = re.search(r"/agm/materia/([A-Z0-9]{6,12})", bloco)
        if not cod:
            continue
        h2 = re.search(r"<h2[^>]*>(.*?)</h2>", bloco, re.S | re.I)
        tx = limpar(bloco)
        mc = re.search(r"Circula[çc][ãa]o\s*(\d{2}/\d{2}/\d{4})", tx)
        dt = _data_br(mc.group(1)) if mc else ""
        titulo = limpar(h2.group(1)) if h2 else tx[:160]
        resumo = tx.split(titulo, 1)[-1] if titulo and titulo in tx else tx
        out.append(_pub(cidade, "diário AGM", f"https://www.diariomunicipal.com.br/agm/materia/{cod.group(1)}", titulo, dt, resumo))
    return (int(tot.group(1).replace(".", "")) if tot else len(out)), out


def ler_agm(m: dict, cfg: dict, desde: str, ate: str, fim: float, termos: list[str] | None = None) -> tuple[str, list[dict], dict]:
    """ROTA A — busca avançada do Diário Oficial dos Municípios (AGM/SIGPub), por entidade e período."""
    a = cfg["agm"]; out = {}; vol = {}; falhas = 0
    for termo in termos or a["termos"]:
        pg = 1
        while pg <= a["max_paginas"]:
            if time.time() > fim:
                return "parcial (tempo)", list(out.values()), vol
            q = urllib.parse.urlencode({"busca_avancada[texto]": termo, "busca_avancada[entidade]": m["agm"],
                                        "busca_avancada[dataInicio]": desde, "busca_avancada[dataFim]": ate,
                                        "busca_avancada[ordenacao]": "", "busca_avancada[pagina]": str(pg)})
            st, html, _ = _get(a["url"] + "?" + q, timeout=35)
            if st != 200:
                falhas += 1
                break
            tot, itens = parse_agm(html, m["municipio"])
            if pg == 1:
                vol[termo] = tot
            for x in itens:
                out.setdefault(x["url"], x)
            time.sleep(cfg["pausa_segundos"])
            if len(itens) < a["por_pagina"] or pg * a["por_pagina"] >= tot:
                break
            pg += 1
    if falhas and not out:
        return "falhou", [], vol
    return ("lida" if out else "vazia") if not falhas else "parcial", list(out.values()), vol


def ler_qd(m: dict, cfg: dict, desde: str, fim: float, termos: list[str] | None = None) -> tuple[str, list[dict], dict]:
    """ROTA C — Querido Diário (domínio novo). Cada edição com o termo vira uma publicação (o trecho é o resumo)."""
    q = cfg["querido_diario"]; out = {}; vol = {}; falhas = 0
    for termo in termos or q["termos"]:
        off = 0
        while off < q["max_por_termo"]:
            if time.time() > fim:
                return "parcial (tempo)", list(out.values()), vol
            url = (f"{q['api']}/gazettes?territory_ids={m['ibge']}&querystring={urllib.parse.quote(termo)}"
                   f"&published_since={desde}&size=100&offset={off}")
            st, corpo, _ = _get(url, timeout=40)
            try:
                j = json.loads(corpo) if st == 200 else None
            except Exception:
                j = None
            if not j:
                falhas += 1
                break
            vol[termo] = j.get("total_gazettes")
            for g in j.get("gazettes") or []:
                trecho = " … ".join((g.get("excerpts") or [])[:2])
                x = _pub(m["municipio"], "Querido Diário", g.get("url") or "", f"Diário Oficial de {m['municipio']} — edição {g.get('edition') or ''} "
                         f"({g.get('date')}) — {termo.strip(chr(34))}", g.get("date") or "", trecho)
                out.setdefault(x["url"] + termo, x)
            if len(j.get("gazettes") or []) < 100:
                break
            off += 100
            time.sleep(cfg["pausa_segundos"])
    if falhas and not out:
        return "falhou (Querido Diário instável)", [], vol
    return ("lida" if out else "vazia"), list(out.values()), vol


def _links(html: str, base: str) -> list[tuple[str, str]]:
    out = []
    for mm in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        out.append((urllib.parse.urljoin(base, unescape(mm.group(1))), limpar(mm.group(2))))
    return out


def ler_portal(m: dict, cfg: dict, desde: str, fim: float) -> tuple[str, list[dict], dict]:
    """ROTA D — portais próprios. Modo vem do catálogo: avisos_paginado · busca_wp_html · noticias_paginado · pagina_editais
    · requer_navegador."""
    p = m.get("portal") or {}; modo = p.get("modo"); base = m["site"].rstrip("/") + "/"; out = {}; vol = {}
    if modo == "requer_navegador":
        return "requer navegador (portal montado por script) — fica o inventário-base", [], vol
    if modo == "avisos_paginado":                                  # Catalão
        for sec in p["secoes"]:
            n = 0
            for pg in range(1, p.get("max_paginas", 15) + 1):
                if time.time() > fim:
                    return "parcial (tempo)", list(out.values()), vol
                st, html, _ = _get(urllib.parse.urljoin(base, f"{sec}?page={pg}"))
                if st != 200:
                    break
                itens = [(u, t) for u, t in _links(html, base) if re.match(r"\d{2}/\d{2}/\d{4}", t)]
                if not itens:
                    break
                velho = False
                for u, t in itens:
                    d = _data_br(t[:10])
                    if d and d < desde:
                        velho = True; continue
                    out.setdefault(u, _pub(m["municipio"], f"portal {sec}", u, t[13:] or t, d)); n += 1
                time.sleep(cfg["pausa_segundos"])
                if velho:
                    break
            vol[sec] = n
    elif modo == "busca_wp_html":                                   # Luziânia: /page/N/?s=termo
        for termo in p.get("termos") or cfg["wp"]["termos"][:8]:
            for pg in range(1, p.get("max_paginas", 6) + 1):
                if time.time() > fim:
                    return "parcial (tempo)", list(out.values()), vol
                st, html, _ = _get(base + (f"page/{pg}/" if pg > 1 else "") + "?s=" + urllib.parse.quote(termo))
                if st != 200:
                    break
                arts = re.findall(r"<article\b.*?</article>", html, re.S | re.I)
                if not arts:
                    break
                for a in arts:
                    h = re.search(r"<h[1-4][^>]*>.*?<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>", a, re.S | re.I)
                    if not h:
                        continue
                    tt = limpar(h.group(2)); u = urllib.parse.urljoin(base, h.group(1))
                    dt = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', a)
                    ano = re.search(r"\b(20[2-3]\d)\b", tt)
                    d = dt.group(1) if dt else (ano.group(1) if ano else "")
                    if d and d[:4] < desde[:4]:
                        continue
                    out.setdefault(u, _pub(m["municipio"], "busca interna do site", u, tt, d))
                vol[termo] = vol.get(termo, 0) + len(arts)
                time.sleep(cfg["pausa_segundos"])
    elif modo == "noticias_paginado":                               # Novo Gama: /noticias/N, 9 por página
        for pg in range(1, p.get("max_paginas", 260) + 1):
            if time.time() > fim:
                return "parcial (tempo)", list(out.values()), vol
            st, html, _ = _get(base + f"noticias/{pg}")
            if st != 200:
                break
            itens = [(u, t) for u, t in _links(html, base) if "noticia/" in u and re.search(r"\d{2}/\d{2}/\d{4}", t)]
            if not itens:
                break
            velhos = 0
            for u, t in itens:
                d = _data_br(t)
                if d and d < desde:
                    velhos += 1; continue
                out.setdefault(u, _pub(m["municipio"], "notícias do portal", u, re.sub(r"\d{2}/\d{2}/\d{4}\s*(EM\s+)?", "", t), d))
            time.sleep(cfg["pausa_segundos"] / 2)
            if velhos >= 3:
                break
        vol["noticias"] = len(out)
    elif modo == "pagina_editais":                                  # Goianésia, Anápolis, Rio Verde: página com links/PDF
        for cam in p["paginas"]:
            st, html, _ = _get(urllib.parse.urljoin(base, cam))
            if st != 200:
                continue
            n = 0
            for u, t in _links(html, base):
                ano = re.search(r"\b(20[2-3]\d)\b", t + " " + u)
                if 8 <= len(t) <= 220 and re.search(r"edita|chamament|chamada|sele[cç]|credenciament|pr[eê]mio|fomento", sem(t)) \
                   and (not ano or ano.group(1) >= desde[:4]):
                    out.setdefault(u, _pub(m["municipio"], f"página {cam}", u, t, ano.group(1) if ano else "")); n += 1
            vol[cam] = n
            time.sleep(cfg["pausa_segundos"])
    else:
        return "sem rota de portal", [], vol
    return ("lida" if out else "vazia"), list(out.values()), vol


# ═══════════════════════════════════════════════════ CAMADAS ════════════════════════════════════════════════════════
def _rotas(m: dict) -> list[str]:
    r = []
    if m.get("agm"):
        r.append("agm")
    if m.get("wp_api"):
        r.append("wp")
    if m.get("qd"):
        r.append("qd")
    if m.get("portal"):
        r.append("portal")
    return r


def _ler_rota(rota: str, m: dict, cfg: dict, desde: str, hoje: date, fim: float, monitorar: bool = False) -> tuple[str, list[dict], dict]:
    if rota in ("wp", "portal") and _exige_brasil(m["site"]) and _no_github_sem_brasil():
        return "aguardando coleta local (Brasil)", [], {}
    if rota == "agm":
        return ler_agm(m, cfg, desde, hoje.isoformat(), fim, cfg["agm"]["termos"][:5] if monitorar else None)
    if rota == "wp":
        return ler_wp(m, cfg, desde, fim, None, 1 if monitorar else None)
    if rota == "qd":
        return ler_qd(m, cfg, desde, fim)
    return ler_portal(m, cfg, desde, fim)


def processar_cidade(c: dict, m: dict, cfg: dict, hoje: date, fim: float) -> tuple[list[dict], list[dict]]:
    """Camadas 2-4 de UMA cidade. Devolve (abertas, do_passado)."""
    monitorar = c.get("camada") == 4
    desde = (c.get("ultima_publicacao_vista") if monitorar else None) or (hoje - timedelta(days=cfg["janela_historico_dias"])).isoformat()
    if monitorar:
        desde = min(desde, (hoje - timedelta(days=cfg["monitoramento_dias_minimos"])).isoformat())
    pubs, rotas_st, vol = [], {}, {}
    for rota in _rotas(m):
        if time.time() > fim:
            rotas_st[rota] = "não lida (tempo da execução acabou)"; continue
        try:
            st, itens, v = _ler_rota(rota, m, cfg, desde, hoje, fim, monitorar)
        except Exception as ex:
            st, itens, v = f"falhou ({type(ex).__name__})", [], {}
        rotas_st[rota] = st; vol[rota] = v; pubs += itens
    c["rotas"] = rotas_st; c["volume_por_rota"] = vol
    lidas = [r for r, s in rotas_st.items() if s.startswith(("lida", "vazia", "parcial"))]
    # 03/10 (teste do motor 13): rota que FALHOU aparece como falha, mesmo que a outra rota aguarde o Brasil (antes Senador
    # Canedo e Inhumas, com o diário AGM falhando, apareciam só como "aguardando coleta local")
    falhou = [r for r, s in rotas_st.items() if s.startswith(("falhou", "não lida"))]
    c["status"] = ("lida" if lidas and len(lidas) == len(rotas_st) else "parcial" if lidas else
                   "falhou" if falhou else
                   "aguardando coleta local (Brasil)" if any("Brasil" in s for s in rotas_st.values()) else "não lida")
    abertas, passadas = [], []
    ver, cat, por_ano = Counter(), Counter(), Counter()
    for x in pubs:
        try:
            pub = date.fromisoformat(x["data"]) if len(x.get("data") or "") == 10 else None
        except ValueError:
            pub = None
        if x.get("rota") == "Querido Diário":
            # 03/10 (teste do motor 13): a publicação do Querido Diário é a EDIÇÃO inteira; o título levava o termo buscado
            # ("— chamamento público") e toda edição virava "seleção aberta" (12 falsas abertas em Goiânia e Aparecida).
            # Quem decide é o TRECHO; sem prazo escrito no trecho, não é aberta — fica para conferir o ato.
            k = classificar(x["resumo"][:300], x["resumo"], pub, hoje, cfg["lexico"])
            if k["veredito"] == "OPORTUNIDADE" and not k.get("prazo"):
                k = {**k, "aberta": False, "motivo": k["motivo"] + " — trecho de edição do diário sem prazo; conferir o ato"}
        else:
            k = classificar(x["titulo"], x["resumo"], pub, hoje, cfg["lexico"])
        ver[k["veredito"]] += 1; cat[k["categoria"]] += 1
        if pub:
            por_ano[str(pub.year)] += 1
        if k["veredito"] == "OPORTUNIDADE":
            (abertas if k.get("aberta") else passadas).append({**x, **k})
    if lidas:
        c["ultima_leitura"] = hoje.isoformat()
        datas = [x["data"] for x in pubs if len(x.get("data") or "") == 10]
        if datas:
            c["ultima_publicacao_vista"] = max(datas + [c.get("ultima_publicacao_vista") or ""])
        if not monitorar and all(not s.startswith("parcial") for s in rotas_st.values()):
            c["camada"] = 4; c["historico_em"] = hoje.isoformat()
        elif not monitorar:
            c["camada"] = 2
    hist = c.setdefault("historico", {"vereditos": {}, "categorias": {}, "publicacoes_por_ano": {}})
    for chave, cont in (("vereditos", ver), ("categorias", cat), ("publicacoes_por_ano", por_ano)):
        for k_, v_ in cont.items():
            hist[chave][k_] = hist[chave].get(k_, 0) + v_
    c["exemplos"] = ([{"titulo": r["titulo"][:140], "data": r["data"], "url": r["url"], "categoria": r["categoria"], "aberta": bool(r.get("aberta"))}
                      for r in sorted(abertas + passadas, key=lambda z: z["data"], reverse=True)[:8]] or c.get("exemplos") or [])
    c["oportunidades_abertas"] = len(abertas)
    return abertas, passadas


def janelas_previsiveis(base: list | None = None) -> dict:
    """Do inventário-base: em que meses cada cidade abriu seleções (cultura, CMDCA/FIA, OSC) — calendário de ciclo."""
    base = base if base is not None else INVENTARIO_BASE
    out = defaultdict(lambda: defaultdict(set))
    for mun, d, _f, cat, _t, _u in base:
        if cat in ("OPORTUNIDADE_CULTURA", "CMDCA_FIA", "OPORTUNIDADE_OSC") and len(d) == 10:
            out[mun][cat].add(int(d[5:7]))
    return {m: {c: sorted(v) for c, v in cs.items()} for m, cs in sorted(out.items())}


def _registro(r: dict) -> dict:
    ev = re.sub(r"\s+", " ", f"{r['titulo']} {r.get('resumo') or ''}")[:700]
    return {"id": sha256(f"pref25|{r['url']}".encode()).hexdigest()[:20], "status": "capturada", "titulo": f"{r['cidade']} — {r['titulo']}"[:300],
            "url": r["url"], "fonte_id": MOTOR_ID, "fonte_nome": NOME, "territorio": r["cidade"], "uf": "GO", "nivel": "municipal",
            "tipo_fonte": "site_oficial_municipal" if r["rota"] != "diário AGM" and r["rota"] != "Querido Diário" else "diario_oficial_municipal",
            "confianca": "primaria", "forma_divulgacao": r["rota"], "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "data_publicacao": r.get("data") or None, "fim": r.get("prazo"), "prazo_texto": r.get("prazo"), "orgao": f"Prefeitura de {r['cidade']}",
            "evidencia": ev, "hash_evidencia": sha256(ev.encode()).hexdigest(),
            "classificacao_ato": {"veredito": r["veredito"], "categoria": r["categoria"], "motivos": [r["motivo"]]},
            "sensor": MOTOR_ID, "forca_lexica": 3}


def _livros(est: dict, itens: list[dict], diag: dict) -> None:
    """O do passado (e o inventário-base, uma vez) vai para o histórico dos livros — alimenta a previsão de ciclo."""
    pend = {x["url"]: x for x in (est.get("pendentes_livros") or []) + itens}
    if os.environ.get("PREFEITURAS_SEM_LIVROS") or not pend:
        est["pendentes_livros"] = list(pend.values()); return
    try:
        from .livros_regra import registrar_achados
        diag["livros"] = registrar_achados(list(pend.values()), NOME); est["pendentes_livros"] = []
    except Exception as ex:
        est["pendentes_livros"] = list(pend.values()); diag["falhas"].append(f"livros: {type(ex).__name__}: {ex}"[:160])


def ler_motor(sensor: dict | None = None, hoje: date | None = None, limites: dict | None = None, orcamento: float | None = None) -> dict:
    cfg = config(); hoje = hoje or date.today()
    est = _j(ESTADO, {}) or {}
    est.setdefault("cidades", {})
    fim = time.time() + float(orcamento or cfg.get("orcamento_segundos_por_execucao", 900))
    diag = {"motor": NOME, "cidades": len(cfg["municipios"]), "falhas": [], "camadas": Counter(), "motivo_zero": None,
            "origem": "coleta local (Brasil)" if os.environ.get("ELDORADO_LOCAL_BR") else ("GitHub" if os.environ.get("GITHUB_ACTIONS") else "local")}
    for m in cfg["municipios"]:
        est["cidades"].setdefault(m["municipio"], {"municipio": m["municipio"], "camada": 1})
    abertas, passadas = [], []
    # 1º monitoramento (barato) das que já têm histórico; 2º as demais, uma por vez — AGM primeiro (maior rendimento)
    ordem = sorted(cfg["municipios"], key=lambda m: (est["cidades"][m["municipio"]].get("camada") != 4, not m.get("agm"), m["municipio"]))
    vistas = set()
    for m in ordem:
        if time.time() > fim:
            break
        vistas.add(m["municipio"])
        c = est["cidades"][m["municipio"]]
        try:
            a, p = processar_cidade(c, m, cfg, hoje, fim)
            abertas += a; passadas += p; diag["camadas"]["4" if c.get("camada") == 4 else "2-3"] += 1
        except Exception as ex:
            diag["falhas"].append(f"{m['municipio']}: {type(ex).__name__}: {ex}"[:160]); c["status"] = "não lida"
    hist = [{"titulo": f"{r['cidade']} — {r['titulo']}", "url": r["url"], "orgao": f"Prefeitura de {r['cidade']}", "uf": "GO",
             "prazo": r.get("prazo"), "publicado_em": r.get("data")} for r in passadas + abertas]
    if not est.get("inventario_base_registrado"):
        hist += [{"titulo": f"{mu} — {t}", "url": u, "orgao": f"Prefeitura de {mu}", "uf": "GO", "prazo": None,
                  "publicado_em": d if len(d) == 10 else None} for mu, d, _f, cat, t, u in INVENTARIO_BASE
                 if cat in ("OPORTUNIDADE_OSC", "OPORTUNIDADE_CULTURA", "CMDCA_FIA")]
    antes = len(est.get("pendentes_livros") or []) + len(hist)
    _livros(est, hist, diag)
    if not est.get("pendentes_livros") and antes:
        est["inventario_base_registrado"] = True
    achados = [_registro(r) for r in {r["url"]: r for r in abertas}.values()]
    st = Counter(c.get("status", "não lida") for c in est["cidades"].values())
    diag["cidades_por_status"] = dict(st); diag["camadas"] = dict(diag["camadas"])
    diag["paginas_lidas"] = sum(diag["camadas"].values())
    # 03/10 (teste do motor 13): PUBLICADO × LIDO por cidade e rota. O que a NUVEM podia ler e não leu (falha, tempo, cidade
    # não alcançada) vira `paginas_nao_lidas` → o maestro vê "parcial" e dispara de novo. O que só abre pelo Brasil fica em
    # `aguardando_brasil` → o maestro vê "pendente_local" (nunca "completa"), e o painel diz quantas cidades faltam.
    nao_lidas, brasil = [], []
    for m in cfg["municipios"]:
        c = est["cidades"][m["municipio"]]
        if m["municipio"] not in vistas:
            nao_lidas.append(f"{m['municipio']}: não alcançada nesta execução (tempo)"); continue
        for r, s_ in (c.get("rotas") or {}).items():
            if s_.startswith(("falhou", "não lida")) or "tempo" in s_:
                nao_lidas.append(f"{m['municipio']} · {r}: {s_}")
            elif "Brasil" in s_:
                brasil.append(f"{m['municipio']} · {r}")
    if nao_lidas:
        diag["paginas_nao_lidas"] = nao_lidas[:25]
    if brasil:
        diag["aguardando_brasil"] = brasil; diag["exige_brasil"] = True
    diag["leitura_do_dia"] = {"cidades": len(cfg["municipios"]), "lidas": st.get("lida", 0), "parciais": st.get("parcial", 0),
                              "aguardando_brasil": st.get("aguardando coleta local (Brasil)", 0), "falharam": st.get("falhou", 0),
                              "rotas_aguardando_brasil": len(brasil), "rotas_nao_lidas": len(nao_lidas)}
    if not achados:
        diag["motivo_zero"] = ("; ".join(f"{k}: {v}" for k, v in st.items()) + " — nenhuma seleção aberta nova hoje") if not diag["falhas"] \
            else "falhas: " + "; ".join(diag["falhas"][:2])
    est["ultima"] = {"em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "data": hoje.isoformat(), "achados": len(achados),
                     "historicas": len(passadas), "cidades_por_status": diag["cidades_por_status"], "falhas": diag["falhas"][:10]}
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(est, ensure_ascii=False, indent=1), encoding="utf-8")
    painel()
    saude = [{"url": m["site"], "status": est["cidades"][m["municipio"]].get("status")} for m in cfg["municipios"]]
    return {"sensor": MOTOR_ID, "achados": achados, "falhas": [{"erro": f} for f in diag["falhas"]], "saude": saude, "diagnostico": diag}


def painel() -> dict:
    est = _j(ESTADO, {}) or {}; cfg = config()
    base_cid = Counter(r[0] for r in INVENTARIO_BASE)
    base_cat = defaultdict(Counter)
    for r in INVENTARIO_BASE:
        base_cat[r[0]][r[3]] += 1
    jan = janelas_previsiveis()
    cid = []
    for m in cfg["municipios"]:
        c = (est.get("cidades") or {}).get(m["municipio"], {})
        cid.append({"municipio": m["municipio"], "status": c.get("status") or "ainda não lida", "rotas": c.get("rotas") or {r: "ainda não lida" for r in _rotas(m)},
                    "camada": c.get("camada", 1), "ultima_leitura": c.get("ultima_leitura"), "historico": c.get("historico"),
                    "oportunidades_abertas": c.get("oportunidades_abertas", 0), "exemplos": c.get("exemplos") or [],
                    "inventario_base": {"total": base_cid.get(m["municipio"], 0), "por_categoria": dict(base_cat[m["municipio"]])},
                    "janelas_previsiveis_meses": jan.get(m["municipio"], {}),
                    "onde_publica": {k: m.get(k) for k in ("site", "diario", "transparencia", "agm", "qd") if m.get(k)}})
    st = Counter(x["status"] for x in cid)
    out = {"motor": NOME, "em": (est.get("ultima") or {}).get("em"), "regra_de_honestidade":
           "cidade só aparece como 'lida' quando TODAS as suas rotas responderam nesta leitura; 'aguardando coleta local (Brasil)' "
           "significa que o site recusa IP estrangeiro e será lido pelo coletor local", "cidades": cid,
           "totais": {"cidades": len(cid), "por_status": dict(st), "inventario_base": len(INVENTARIO_BASE),
                      "oportunidades_abertas": sum(x["oportunidades_abertas"] for x in cid)}}
    PAINEL.parent.mkdir(parents=True, exist_ok=True)
    PAINEL.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out["totais"]


# ═══════════════════════════════════════════════ IMPLANTAÇÃO ════════════════════════════════════════════════════════
_DESPACHO = '''    # MOTOR 08 v2 (parecer complementar de 02/10/2026): as 25 maiores prefeituras de Goiás lidas onde publicam — diário
    # AGM, API do WordPress, Querido Diário (domínio novo) e portais próprios —, com status honesto por cidade e por rota
    if sensor.get("id") == "plat-prefeituras-50-go":
        from .prefeituras_25_go import ler_motor as ler_motor_pref
        return ler_motor_pref(sensor, data, limites)
'''

TESTES = r'''"""02/10/2026 (titular): motor 08 v2 — 25 maiores prefeituras de Goiás (diário AGM, WordPress, Querido Diário, portais)."""
import importlib.util, json, os, sys, tempfile, unittest
from datetime import date
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from src import prefeituras_25_go as P
except Exception:                                   # autoteste (--testar) fora do repositório
    _spec = importlib.util.spec_from_file_location("prefeituras_25_go", os.environ["PREF25_MODULO"])
    P = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(P)

H = date(2026, 10, 2)
LEX = P.CONFIG_PADRAO["lexico"]


def c(t, r="", pub=H):
    return P.classificar(t, r, pub, H, LEX)


class TesteClassificador(unittest.TestCase):
    def test_oportunidades_reais_do_inventario(self):
        casos = [
            ("Prefeitura de Goiânia abre chamamento público para seleção de instituições de longa permanência e Casa-Lar para idosos", "", "OPORTUNIDADE_OSC"),
            ("CHAMADA PUBLICA", "objeto é a Seleção de Organização da Sociedade Civil (OSC) para celebrar Termo de Colaboração", "OPORTUNIDADE_OSC"),
            ("CHAMAMENTO PÚBLICO Nº 06/2026 – PROCESSO Nº 23713/2026", "", "OPORTUNIDADE_OSC"),
            ("Edital de Chamamento Público - Termo de Fomento Nº 001/2026", "", "OPORTUNIDADE_OSC"),
            ("SEMASC abre Chamamento Público para seleção de projetos voltados à proteção de crianças e adolescentes", "", "CMDCA_FIA"),
            ("Prefeitura de Anápolis lança editais da lei Aldir Blanc para o setor cultural", "", "OPORTUNIDADE_CULTURA"),
            ("EDITAL DE CHAMAMENTO PÚBLICO Nº 001-CMDCA-2026", "", "CMDCA_FIA"),
            ("Prefeito Mabel lança credenciamento para entidades socioassistenciais e destaca parceria com o terceiro setor", "", "OPORTUNIDADE_OSC"),
        ]
        for t, r, cat in casos:
            x = c(t, r)
            self.assertEqual(x["veredito"], "OPORTUNIDADE", t); self.assertEqual(x["categoria"], cat, t)

    def test_parceria_direta(self):
        for t, r in (("TERMO DE FOMENTO N° 007/2026", "O presente Termo de Fomento tem por objeto"),
                     ("EXTRATO – JUSTIFICATIVA DE INEXIGIBILIDADE DE CHAMAMENTO PÚBLICO", "organização da sociedade civil"),
                     ("EXTRATO DE CONVENIO", "Termo de Convênio de subvenção social com a entidade filantrópica")):
            x = c(t, r)
            self.assertEqual(x["categoria"], "PARCERIA_DIRETA", t); self.assertEqual(x["veredito"], "ACOMPANHAR", t)

    def test_ruido_tipico_vira_veto(self):
        for t, r in (("Chamada Pública Escolar 2027: Secretaria de Educação divulga edital para ingresso na Rede Municipal", ""),
                     ("Prefeitura de Aparecida reforça o chamamento para quem ainda não se vacinou contra a febre amarela", ""),
                     ("CHAMAMENTO PÚBLICO Nº 05/2026 – FESTIVAL GASTRONÔMICO", ""),
                     ("Prefeitura de Goiânia publica Chamamento Público para seleção de influenciadores digitais", ""),
                     ("Aparecida conquista 1º lugar em Prêmio da Qualidade da Informação Contábil do Tesouro Nacional", ""),
                     ("EXTRATO DE ORDEM DE FORNECIMENTO N° 51285/2026", "CONTRATAÇÃO DE EMPRESA PARA FORNECIMENTO DE COMBUSTÍVEL"),
                     ("EDITAL DE INTIMAÇÃO FISCAL Nº 00043, DE 01 DE OUTUBRO DE 2026", ""),
                     ("EDITAL DE CONVOCAÇÃO N.° 023/2026 PARA APRESENTAÇÃO DE DOCUMENTOS E EXAME DE APTIDÃO FÍSICA", "")):
            self.assertEqual(c(t, r)["veredito"], "RUIDO", t)

    def test_resultado_e_ato_do_edital(self):
        self.assertEqual(c("RESULTADO PRELIMINAR – CHAMAMENTO PÚBLICO 01/2026")["categoria"], "RESULTADO")
        self.assertEqual(c("Prefeitura de Anápolis prorroga inscrições dos editais da Política Nacional Aldir Blanc até 26 de julho")["categoria"], "ATO_DO_EDITAL")
        self.assertEqual(c("Chamada Pública nº 01/2026 do programa de aquisição de alimentos (PAA)")["categoria"], "AGRICULTURA_FAMILIAR")

    def test_prazo_e_aberta(self):
        x = c("Edital de Chamamento Público nº 01/2026 – projetos culturais PNAB", "inscrições até 20/10/2026", date(2026, 9, 20))
        self.assertTrue(x["aberta"]); self.assertEqual(x["prazo"], "2026-10-20")
        self.assertFalse(c("Edital de Chamamento Público nº 01/2024 – PNAB", "inscrições até 20/07/2024", date(2024, 6, 25))["aberta"])

    def test_concordancia_com_o_inventario(self):
        """A régua automática concorda com a curadoria humana do inventário em pelo menos 70% das oportunidades e nunca
        manda para RUÍDO mais de 1/4 delas."""
        ops = [r for r in P.INVENTARIO_BASE if r[3] in ("OPORTUNIDADE_OSC", "OPORTUNIDADE_CULTURA", "CMDCA_FIA")]
        ver = [c(r[4])["veredito"] for r in ops]
        self.assertGreaterEqual(sum(v == "OPORTUNIDADE" for v in ver) / len(ver), 0.70)
        self.assertLessEqual(sum(v == "RUIDO" for v in ver) / len(ver), 0.25)


class TesteInventarioECatalogo(unittest.TestCase):
    def test_inventario(self):
        self.assertEqual(len(P.INVENTARIO_BASE), 357)
        nomes = {m["municipio"] for m in P.CONFIG_PADRAO["municipios"]}
        self.assertEqual(len(nomes), 25); self.assertEqual({r[0] for r in P.INVENTARIO_BASE}, nomes)
        self.assertTrue(all(r[5].startswith("https://") for r in P.INVENTARIO_BASE))

    def test_catalogo_rotas(self):
        ms = {m["municipio"]: m for m in P.CONFIG_PADRAO["municipios"]}
        self.assertEqual(sorted(k for k, m in ms.items() if m.get("agm")),
                         sorted(["Águas Lindas de Goiás", "Cristalina", "Formosa", "Inhumas", "Senador Canedo", "Trindade"]))
        self.assertEqual(P.CONFIG_PADRAO["querido_diario"]["api"], "https://api.queridodiario.org.br")
        for m in ms.values():
            self.assertTrue(P._rotas(m), m["municipio"])
        self.assertTrue(all(m.get("ibge") is None or len(m["ibge"]) == 7 for m in ms.values()))

    def test_janelas_previsiveis(self):
        j = P.janelas_previsiveis()
        self.assertIn(4, j["Itaberaí"]["CMDCA_FIA"])
        self.assertTrue(j["Águas Lindas de Goiás"]["OPORTUNIDADE_CULTURA"])


AGM_HTML = """<p>33 matérias</p><ul>
<li class="materia-card"><h2>TERMO DE FOMENTO N° 007/2026</h2><span>Prefeitura Municipal de Inhumas</span>
<p>O presente Termo de Fomento tem por objeto a execução do projeto da associação</p><span>Circulação 17/07/2026 Edição 3640</span>
<a href="https://www.diariomunicipal.com.br/agm/materia/824F71A0">Abrir matéria</a></li>
<li class="materia-card"><h2>CHAMADA PUBLICA</h2><p>Seleção de Organização da Sociedade Civil (OSC) para celebrar Termo de Colaboração, inscrições até 30/10/2026</p>
<span>Circulação 25/09/2026</span><a href="/agm/materia/D8B273E6">Abrir matéria</a></li></ul>"""


class TesteLeitores(unittest.TestCase):
    def test_parse_agm(self):
        tot, itens = P.parse_agm(AGM_HTML, "Inhumas")
        self.assertEqual(tot, 33); self.assertEqual(len(itens), 2)
        self.assertEqual(itens[0]["data"], "2026-07-17"); self.assertTrue(itens[1]["url"].endswith("/agm/materia/D8B273E6"))
        self.assertEqual(c(itens[1]["titulo"], itens[1]["resumo"], date(2026, 9, 25))["veredito"], "OPORTUNIDADE")

    def test_wp_e_volume(self):
        cfg = P.CONFIG_PADRAO; m = {"municipio": "Planaltina", "site": "https://www.planaltina.go.gov.br", "wp_api": True}
        post = [{"id": 1, "date": "2026-09-08T10:00:00", "link": "https://www.planaltina.go.gov.br/chamamento-publico-no-06-2026/",
                 "title": {"rendered": "CHAMAMENTO PÚBLICO Nº 06/2026"}, "excerpt": {"rendered": "<p>seleção de OSC</p>"}}]
        with mock.patch.object(P, "_get", return_value=(200, json.dumps(post), {"x-wp-total": "1"})), mock.patch.object(P.time, "sleep"):
            st, itens, vol = P.ler_wp(m, cfg, "2023-10-02", 1e18, ["chamamento"], 1)
        self.assertEqual(st, "lida"); self.assertEqual(len(itens), 1); self.assertEqual(vol["chamamento/posts"], 1)
        with mock.patch.object(P, "_get", return_value=(401, "", {})):
            self.assertTrue(P.ler_wp(m, cfg, "2023-10-02", 1e18, ["x"], 1)[0].startswith("fechada"))

    def test_catalao_avisos(self):
        html = ('<a href="/avisos/edital-de-chamamento-publico/termo-de-fomento-001-2026">01/06/2026 | EDITAL DE CHAMAMENTO PÚBLICO Termo de Fomento Nº 001/2026</a>'
                '<a href="/avisos/x/velho">01/06/2022 | antigo</a>')
        m = {"municipio": "Catalão", "site": "https://www.catalao.go.gov.br", "portal": {"modo": "avisos_paginado", "secoes": ["avisos/edital-de-chamamento-publico"], "max_paginas": 2}}
        with mock.patch.object(P, "_get", return_value=(200, html, {})), mock.patch.object(P.time, "sleep"):
            st, itens, _ = P.ler_portal(m, P.CONFIG_PADRAO, "2023-10-02", 1e18)
        self.assertEqual(st, "lida"); self.assertEqual(len(itens), 1); self.assertEqual(itens[0]["data"], "2026-06-01")

    def test_requer_navegador_nao_finge_leitura(self):
        m = {"municipio": "Mineiros", "site": "https://www.mineiros.go.gov.br", "portal": {"modo": "requer_navegador"}}
        st, itens, _ = P.ler_portal(m, P.CONFIG_PADRAO, "2023-10-02", 1e18)
        self.assertTrue(st.startswith("requer navegador")); self.assertEqual(itens, [])

    def test_qd_instavel_vira_falha_explicita(self):
        m = {"municipio": "Goiânia", "ibge": "5208707", "qd": "5208707"}
        with mock.patch.object(P, "_get", return_value=(0, "TimeoutError", {})):
            self.assertTrue(P.ler_qd(m, P.CONFIG_PADRAO, "2023-10-02", 1e18, ["x"])[0].startswith("falhou"))


class TesteHonestidade(unittest.TestCase):
    def test_github_sem_brasil_nao_tenta_sites_e_nao_marca_lida(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(P, "ESTADO", Path(d) / "e.json"), mock.patch.object(P, "PAINEL", Path(d) / "p.json"), \
             mock.patch.object(P, "CFG", Path(d) / "nao-existe.json"), mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "1", "PREFEITURAS_SEM_LIVROS": "1"}), \
             mock.patch.object(P, "_get", return_value=(0, "TimeoutError", {})) as g, mock.patch.object(P.time, "sleep"):
            os.environ.pop("ELDORADO_LOCAL_BR", None)
            r = P.ler_motor(hoje=H, orcamento=60)
            self.assertFalse(any(".go.gov.br" in str(a.args[0]) for a in g.call_args_list))
            st = r["diagnostico"]["cidades_por_status"]
            self.assertNotIn("lida", st)
            self.assertGreaterEqual(st.get("aguardando coleta local (Brasil)", 0), 15)
            pn = json.loads((Path(d) / "p.json").read_text(encoding="utf-8"))
            self.assertEqual(pn["totais"]["inventario_base"], 357); self.assertEqual(len(pn["cidades"]), 25)
            e = json.loads((Path(d) / "e.json").read_text(encoding="utf-8"))
            self.assertTrue(e["pendentes_livros"])          # o inventário-base fica pendente para os livros (não se perde)


class TesteInstalacao(unittest.TestCase):
    def test_instalar_e_idempotente(self):
        with tempfile.TemporaryDirectory() as d:
            R = Path(d); (R / "src").mkdir(); (R / "config").mkdir()
            (R / "src/sensores.py").write_text('def ler(sensor, limites=None, pausa=None, data=None):\n    if sensor.get("id") == "dou":\n        return 1\n', encoding="utf-8")
            (R / "config/coletores_api.json").write_text('{"bases": [\n   "https://queridodiario.ok.org.br/api",\n   "https://api.queridodiario.ok.org.br"\n]}', encoding="utf-8")
            P.instalar(R); P.instalar(R)
            t = (R / "src/sensores.py").read_text(encoding="utf-8")
            self.assertEqual(t.count("prefeituras_25_go"), 1)
            self.assertIn("api.queridodiario.org.br", (R / "config/coletores_api.json").read_text(encoding="utf-8"))
            json.loads((R / "config/coletores_api.json").read_text(encoding="utf-8"))
            self.assertTrue((R / "tests/test_motor_prefeituras_25_go.py").exists())
            self.assertEqual(len(json.loads((R / "config/prefeituras_25_go.json").read_text(encoding="utf-8"))["municipios"]), 25)


if __name__ == "__main__":
    unittest.main()
'''


def instalar(raiz: Path | None = None) -> list[str]:
    raiz = raiz or ROOT; feito = []
    s = raiz / "src/sensores.py"
    if s.exists():
        t = s.read_text(encoding="utf-8")
        if "prefeituras_25_go" not in t:
            alvo = '    if sensor.get("id") == "dou":'
            if alvo not in t:
                raise SystemExit("não achei o ponto de despacho em src/sensores.py — inserir o bloco _DESPACHO à mão")
            s.write_text(t.replace(alvo, _DESPACHO + alvo, 1), encoding="utf-8"); feito.append("despacho ligado em src/sensores.py")
    (raiz / "config").mkdir(exist_ok=True)
    (raiz / "config/prefeituras_25_go.json").write_text(json.dumps(CONFIG_PADRAO, ensure_ascii=False, indent=1), encoding="utf-8")
    feito.append("config/prefeituras_25_go.json gravado")
    ca = raiz / "config/coletores_api.json"
    if ca.exists():
        t = ca.read_text(encoding="utf-8")
        if "https://api.queridodiario.org.br" not in t and "https://queridodiario.ok.org.br/api" in t:
            ca.write_text(t.replace('"https://queridodiario.ok.org.br/api"', '"https://api.queridodiario.org.br",\n   "https://queridodiario.ok.org.br/api"', 1), encoding="utf-8")
            feito.append("config/coletores_api.json: domínio novo do Querido Diário em primeiro")
    (raiz / "tests").mkdir(exist_ok=True)
    (raiz / "tests/test_motor_prefeituras_25_go.py").write_text(TESTES, encoding="utf-8"); feito.append("tests/test_motor_prefeituras_25_go.py criado")
    return feito


if __name__ == "__main__":
    if "--instalar" in sys.argv:
        for f in instalar():
            print("✔", f)
    elif "--testar" in sys.argv:
        import unittest
        os.environ["PREF25_MODULO"] = str(Path(__file__).resolve())
        ns = {"__file__": str(ROOT / "tests/test_motor_prefeituras_25_go.py"), "__name__": "teste_pref25"}
        exec(compile(TESTES, "test_motor_prefeituras_25_go.py", "exec"), ns)
        suite = unittest.TestSuite()
        for v in ns.values():
            if isinstance(v, type) and issubclass(v, unittest.TestCase):
                suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(v))
        sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
    else:
        sys.path.insert(0, str(ROOT))
        r = ler_motor()
        print(json.dumps(r["diagnostico"], ensure_ascii=False, indent=1)); print(len(r["achados"]), "oportunidade(s) aberta(s)")
