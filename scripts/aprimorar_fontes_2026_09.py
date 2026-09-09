#!/usr/bin/env python3
"""Leva ao catálogo de fontes o que a verificação de 09/09/2026 confirmou.

O QUE ESTE SCRIPT CORRIGE

A verificação dos 467 registros sem verificação (408 do PNCP e 59 de outras
fontes) achou o endereço EXATO de 12 portas de captação que o catálogo já
conhecia por nome, mas apontava para o lugar errado. O caso mais caro é o
BNDES Periferias: o catálogo mandava o coletor para a busca do Diário Oficial
da União e para a home do BNDES, e a chamada aberta — 6º ciclo, inscrições de
18/08/2026 a 04/12/2026, para pessoa jurídica de direito privado sem fins
lucrativos — está em `bndes.gov.br/periferias`, que não estava na lista.
Enquanto o endereço certo não entra, o motor procura para sempre no lugar onde
a informação não está.

Também registra as armadilhas medidas: o que não abre, o que exige navegador e
o ritmo que o PNCP aceita.

Roda quantas vezes quiser: só acrescenta o que falta e não reescreve o que já
está lá.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/fontes_captacao_260.json"
VERIFICADO_EM = "2026-09-09"

# id da fonte já existente -> endereços exatos confirmados nesta rodada.
# Entram no INÍCIO da lista de sites, porque é por onde o coletor deve começar.
ENDERECOS_CONFIRMADOS = {
    "captacao-175": [
        # 6º ciclo aberto: 18/08/2026 a 04/12/2026, às 17h. Protocolo apenas
        # pelo Portal do Cliente do BNDES.
        "https://www.bndes.gov.br/periferias",
        "https://portal.bndes.gov.br/prc/",
    ],
    "captacao-174": ["https://www.bndes.gov.br/wps/portal/site/home/onde-atuamos/desenvolvimento-social-e-urbano/bndes-fundo-social"],
    "captacao-220": ["https://www.bndes.gov.br/wps/portal/site/home/onde-atuamos/desenvolvimento-social-e-urbano/bndes-fundo-social"],
    "captacao-235": [
        # Edital Encantando Comunidades: Recursos Flexíveis — até 13/09/2026.
        "https://www.institutolojasrenner.org.br/edital-encantando-comunidades/",
    ],
}

# Fontes que a rodada confirmou e que não existiam no catálogo.
FONTES_NOVAS = [
    {
        "programa": "Banco do Nordeste — Editais Sociais (incentivo fiscal)",
        "nivel": "federal",
        "area": "crianca_adolescente_idoso_esporte_saude",
        "tipo": "incentivo_fiscal",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": True,
        "uf": None,
        "goias": False,
        "orgao": "Banco do Nordeste do Brasil — BNB",
        "sites": [
            "https://www.bnb.gov.br/web/guest/sustentabilidade/investimentos-sociais-e-esportivos",
            "https://www.bnb.gov.br/ConveniosWeb/Logar.aspx",
        ],
        "dominios": ["www.bnb.gov.br"],
        "confianca_site": "confirmada",
        "nota": ("Editais Sociais 2026: inscrições de 10/08/2026 a 13/09/2026 pelo sistema Convênios "
                 "Web, aporte de até R$ 1,5 milhão por projeto, nas linhas FIA, Pessoa Idosa, "
                 "Incentivo ao Esporte e Pronon/Pronas-PCD. Confirmado no informe do próprio portal "
                 "em 09/09/2026. O ciclo é anual, com lançamento em agosto."),
    },
    {
        "programa": "Funbio — Programa Biodiversidade Litoral do Paraná",
        "nivel": "privada",
        "area": "meio_ambiente",
        "tipo": "edital",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": "PR",
        "goias": False,
        "orgao": "Fundo Brasileiro para a Biodiversidade — Funbio",
        "sites": [
            "https://chamadas.funbio.org.br/planodemanejo-rppn",
            "https://chamadas.funbio.org.br/usopublico-rppn",
            "https://www.funbio.org.br/chamadas-de-projetos/",
        ],
        "dominios": ["chamadas.funbio.org.br", "www.funbio.org.br"],
        "confianca_site": "confirmada",
        "nota": ("Duas chamadas abertas para OSC ambiental em 09/09/2026: 07/2026 (planos de manejo "
                 "de RPPN, até 25/09/2026) e 08/2026 (uso público e negócios sustentáveis em RPPN, "
                 "até 09/10/2026). As datas do próprio Funbio divergem das que a imprensa "
                 "especializada publicou — houve prorrogação, e vale a página oficial."),
    },
    {
        "programa": "Movimento Bem Maior — Edital Futuro Bem Maior",
        "nivel": "privada",
        "area": "fortalecimento_institucional",
        "tipo": "edital",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": None,
        "goias": True,
        "orgao": "Movimento Bem Maior",
        "sites": ["https://editais.movimentobemmaior.org.br/2026/", "https://movimentobemmaior.org.br/"],
        "dominios": ["editais.movimentobemmaior.org.br", "movimentobemmaior.org.br"],
        "confianca_site": "confirmada",
        "nota": ("6ª edição: inscrições de 27/07 a 24/08/2026, encerradas. Elegível OSC ou coletivo "
                 "não formalizado em município de até 200 mil habitantes com receita anual de até "
                 "R$ 500 mil — recorte que serve à maior parte do interior de Goiás. Ciclo anual "
                 "com abertura em julho: revisitar em junho de 2027."),
    },
    {
        "programa": "Agência do Bem / Rede do Bem — Edital de Microprojetos",
        "nivel": "privada",
        "area": "fortalecimento_institucional",
        "tipo": "edital",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": "SP",
        "goias": False,
        "orgao": "Agência do Bem",
        "sites": ["https://rededobem.org.br/editais/"],
        "dominios": ["rededobem.org.br"],
        "confianca_site": "confirmada",
        "nota": "6º edital encerrado em 29/08/2026. Recorte: Região Metropolitana de São Paulo.",
    },
    {
        "programa": "Fundação Tide Setubal — Edital Territórios Clínicos",
        "nivel": "privada",
        "area": "saude_mental",
        "tipo": "edital",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": "SP",
        "goias": False,
        "orgao": "Fundação Tide Setubal",
        "sites": ["https://fundacaotidesetubal.org.br/editais/", "https://conteudo.fundacaotidesetubal.org.br/"],
        "dominios": ["fundacaotidesetubal.org.br", "conteudo.fundacaotidesetubal.org.br"],
        "confianca_site": "curada",
        "nota": ("3ª edição encerrada em 31/08/2026, R$ 200 mil para dez organizações. A página do "
                 "formulário sai do ar quando o edital fecha, então o coletor tem de mirar a seção "
                 "de editais, não a landing page da edição."),
    },
    {
        "programa": "Instituto Clima e Sociedade (iCS) — chamadas de comunicação e clima",
        "nivel": "privada",
        "area": "meio_ambiente",
        "tipo": "grant",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": None,
        "goias": True,
        "orgao": "Instituto Clima e Sociedade",
        "sites": ["https://climaesociedade.org/editais/"],
        "dominios": ["climaesociedade.org"],
        "confianca_site": "confirmada",
        "nota": ("Chamada Comunicação para Ação Climática encerrada em 31/08/2026. Admite OSC com "
                 "CNPJ, coletivo sem CNPJ com organização financeira responsável, e também "
                 "empresa — o que muda o enquadramento e precisa ser lido no edital."),
    },
    {
        "programa": "Banrisul Instituto Cultural e Social — Edital Merece!",
        "nivel": "privada",
        "area": "impacto_social",
        "tipo": "edital",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": "RS",
        "goias": False,
        "orgao": "Banrisul Instituto Cultural e Social",
        "sites": ["https://banrisulcultural.com.br/editais/", "https://banrisulcultural.com.br/projeto/merece/"],
        "dominios": ["banrisulcultural.com.br"],
        "confianca_site": "confirmada",
        "nota": ("Prêmio de impacto social: 50 prêmios de R$ 50 mil, inscrições de 21/07 a "
                 "21/08/2026 às 16h59, restrito a entidade com sede no Rio Grande do Sul."),
    },
    {
        "programa": "Instituto Impactarte — cadastro de proponente em fluxo contínuo",
        "nivel": "privada",
        "area": "impacto_social",
        "tipo": "doacao_patrocinio",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": False,
        "uf": None,
        "goias": True,
        "orgao": "Instituto Impactarte",
        "sites": ["https://www.impactarte.org.br/cadastro-proponente"],
        "dominios": ["www.impactarte.org.br"],
        "confianca_site": "curada",
        "nota": ("Apoio de até R$ 150 mil por iniciativa, mas SEM edital e SEM cronograma: a "
                 "captação é por cadastro de proponente em fluxo contínuo. Fonte de fluxo "
                 "contínuo não deve gerar registro com prazo — os dois campos de data vão nulos."),
    },
    {
        "programa": "SECULT Goiás — chamamentos públicos da Lei 13.019/2014",
        "nivel": "estadual",
        "area": "cultura",
        "tipo": "edital",
        "forma_divulgacao": "site_oficial",
        "publicacao_obrigatoria": True,
        "uf": "GO",
        "goias": True,
        "orgao": "Secretaria de Estado da Cultura de Goiás — SECULT",
        "sites": [
            "https://goias.gov.br/cultura/chamamentos-publicos-2026-lei-13-019-14/",
            "https://goias.gov.br/cultura/editais/",
        ],
        "dominios": ["goias.gov.br"],
        "confianca_site": "confirmada",
        "nota": ("Página índice que reúne os chamamentos do ano. Em 09/09/2026 trazia dois: o "
                 "Chamamento 02/2026 (Termo de Colaboração com OSC para o Circuito das Cavalhadas, "
                 "inscrições de 13/02 a 15/03/2026) e a Chamada 01/2026 (adesão de municípios ao "
                 "CineLeitura do Bem — esta NÃO admite OSC). Uma página índice pode conter editais "
                 "de destinatários diferentes: cada um precisa de leitura própria."),
    },
]

ARMADILHAS_NOVAS = [
    {
        # Registrada em 08/09/2026 e PERDIDA depois: o catálogo em produção
        # voltou a ter zero armadilhas, sinal de que a regeneração de dados
        # reescreve o arquivo e descarta a lista. Reposta aqui, e este script
        # pode ser rodado de novo depois de cada regeneração.
        "url": "https://goias.gov.br/cultura/termos-de-fomento",
        "motivo": ("lista de termos JÁ CELEBRADOS por inexigibilidade: não há fase de inscrição e "
                   "nunca haverá prazo"),
        "verificado_em": "2026-09-08",
    },
    {
        # Achado de 09/09/2026, e vale para todo o monitoramento de Goias.
        "url": "https://goias.gov.br/cultura/ (secao de noticias)",
        "motivo": ("durante o periodo de restricoes eleitorais o portal SUSPENDE a divulgacao de "
                   "noticias: a pagina responde com o comunicado 'em cumprimento a legislacao "
                   "eleitoral, este portal tera a divulgacao de noticias temporariamente suspensa'. "
                   "As paginas de EDITAIS continuam no ar e completas — foi por elas que os 14 editais "
                   "do PNAB 2026 e os cronogramas retificados foram lidos. Um monitor que le a secao de "
                   "noticias conclui que nao ha nada publicado, e conclui errado. Em periodo eleitoral, "
                   "mirar /cultura/pnab/edital-2026-pnab/ e /cultura/chamamentos-publicos-*, nunca as noticias."),
        "verificado_em": VERIFICADO_EM,
    },
    {
        "url": "https://goias.gov.br/cultura/pnab/edital-2026-pnab/",
        "motivo": ("nao e armadilha, e a rota certa: esta pagina lista os 14 editais do PNAB 2026 com o "
                   "PDF de cada um e TODAS as retificacoes de cronograma. As datas de inscricao nao estao "
                   "no corpo do edital, estao nos anexos de cronograma e nas erratas publicadas no Diario "
                   "Oficial — e ha seis retificacoes so nos editais 04 e 06. Ler o edital e ignorar as "
                   "erratas produz prazo errado. Alguns anexos de cronograma sao PDF digitalizado e "
                   "exigem OCR."),
        "verificado_em": VERIFICADO_EM,
    },
    {
        "url": "https://fundacaomariaemilia.org.br/",
        "motivo": ("certificado SSL inválido (hostname mismatch): não abre nem por requisição nem "
                   "por navegador. O Edital FME Transforma 02/2026 existe e a imprensa "
                   "especializada informa inscrições até 30/10/2026, mas o único canal citado é um "
                   "formulário do Google, que não é domínio do patrocinador. Fica como pendência de "
                   "fonte oficial, sem data registrada."),
        "verificado_em": VERIFICADO_EM,
    },
    {
        "url": "https://www.bndes.gov.br/wps/portal/site/home/transparencia/patrocinios",
        "motivo": ("portal em JavaScript: requisição simples devolve só metadados, e o conteúdo só "
                   "aparece com navegador. É vetor permanente, não edital — a Escolha Direta é "
                   "fluxo contínuo por formulário, e os ciclos indicativos de 2026 (limites 08/02, "
                   "08/03, 12/04, 07/06 e 09/08) já venceram. Revisitar quando saírem os de 2027."),
        "verificado_em": VERIFICADO_EM,
    },
    {
        "url": "https://pncp.gov.br/api/consulta/v1/",
        "motivo": ("a API oficial do PNCP devolve HTTP 429 a partir de cerca de 14 requisições "
                   "seguidas em ritmo rápido. Com intervalo de 2,5 s e recuo progressivo no 429, "
                   "317 consultas passaram sem um único erro. Consultar em fila, nunca em paralelo."),
        "verificado_em": VERIFICADO_EM,
    },
    {
        "url": "https://captadores.org.br/editais/",
        "motivo": ("útil só para descobrir o NOME do patrocinador e do edital, como manda a regra do "
                   "titular. Nesta rodada as datas de duas chamadas do Funbio estavam vencidas em "
                   "relação à página oficial (prorrogação não refletida), e um edital de Santa Luzia "
                   "do Paruá/MA descrito como 'Diálogo Competitivo 002/2026' não existe no portal de "
                   "licitações do município. Nunca usar como fonte de prazo."),
        "verificado_em": VERIFICADO_EM,
    },
    {
        "url": "portaldecompraspublicas.com.br | bllcompras.com | licitamaisbrasil.com.br | bnccompras.com | licitanet.com.br | licitardigital.com.br",
        "motivo": ("plataformas privadas de licitação: 86 dos 408 registros do PNCP tinham o link "
                   "capturado apontando para uma delas, sem a chave do PNCP no endereço. A saída é "
                   "a busca oficial `pncp.gov.br/api/search/?q=<termos>&tipos_documento=edital`, "
                   "que devolve `item_url` no formato /compras/{cnpj}/{ano}/{sequencial}` — foi "
                   "assim que 12 registros voltaram a ter página oficial."),
        "verificado_em": VERIFICADO_EM,
    },
]


def main() -> int:
    dados = json.loads(CONFIG.read_text(encoding="utf-8"))
    fontes = dados["fontes"]
    por_id = {f["id"]: f for f in fontes}
    mudou = False

    for fid, urls in ENDERECOS_CONFIRMADOS.items():
        fonte = por_id.get(fid)
        if fonte is None:
            print(f"aviso: fonte {fid} não está no catálogo — nada a corrigir")
            continue
        sites = fonte.setdefault("sites", [])
        novos = [u for u in urls if u not in sites]
        if novos:
            fonte["sites"] = novos + sites
            mudou = True
        dominios = fonte.setdefault("dominios", [])
        for url in urls:
            host = url.split("//", 1)[-1].split("/", 1)[0]
            if host not in dominios:
                dominios.append(host)
                mudou = True
        if fonte.get("verificado_em") != VERIFICADO_EM:
            fonte["verificado_em"] = VERIFICADO_EM
            mudou = True
        if novos:
            print(f"{fid}: {len(novos)} endereço(s) confirmado(s) no topo da lista")

    existentes = {f.get("programa") for f in fontes}
    proximo = max(int(f["id"].rsplit("-", 1)[1]) for f in fontes) + 1
    for nova in FONTES_NOVAS:
        if nova["programa"] in existentes:
            continue
        registro = dict(nova)
        registro["id"] = f"captacao-{proximo}"
        registro["verificado_em"] = VERIFICADO_EM
        registro["padrao"] = {"natureza": nova["tipo"], "canal": "site_oficial",
                              "confianca_rota": "primaria"}
        fontes.append(registro)
        print(f"{registro['id']}: fonte nova — {nova['programa']}")
        proximo += 1
        mudou = True

    armadilhas = dados.setdefault("armadilhas", [])
    urls_arm = {a.get("url") for a in armadilhas}
    for arm in ARMADILHAS_NOVAS:
        if arm["url"] not in urls_arm:
            armadilhas.append(arm)
            print(f"armadilha registrada: {arm['url'][:60]}")
            mudou = True

    if not mudou:
        print("nada a fazer: o catálogo já está com as correções de 09/09/2026")
        return 0

    dados["resumo"]["total"] = len(fontes)
    dados["resumo"]["ultima_correcao"] = VERIFICADO_EM
    CONFIG.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"catálogo gravado com {len(fontes)} fontes e {len(armadilhas)} armadilhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
