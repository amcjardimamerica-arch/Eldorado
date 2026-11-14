"""14/11/2026 (a análise externa em 3 grupos): os vetos novos dos motores — barram o ruído confirmado pelo Claude no Chrome e
não barram nenhum livro válido ou encerrado do lote (a contraprova, com títulos e endereços reais)."""
import tomllib
from pathlib import Path

from eldorado.motores.canal.motor import MotorCanal, _sem_acento

CFG = Path("eldorado/motores/canal/config")


def _barra(motor, titulo, link):
    lx = tomllib.loads((CFG / f"{motor}.toml").read_text(encoding="utf-8")).get("lexico", {})
    t = _sem_acento(titulo)
    salvo = MotorCanal._casa(t, lx.get("salvos", []))          # a exceção («doação») vale para os dois vetos, como no motor
    if lx.get("vetos") and MotorCanal._casa(t, lx["vetos"]) and not salvo:
        return True
    return bool(lx.get("vetos_endereco") and link and MotorCanal._casa(link.lower(), lx["vetos_endereco"]) and not salvo)


CASOS = {
 "sistema-s": [
  [
   [
    "edital patrocinio sebraeba 01 2026",
    "https://sebrae.com.br/ba/subsites/servicos/edital-patrocinio-sebraeba-01-2026"
   ],
   [
    "EDITAL CHAMAMENTO PUBLICO DOACAO GRATUITA DE BENS 18 01 00001.pdf",
    "https://www3.sescgo.com.br/licitacao/download/22126"
   ]
  ],
  [
   [
    "claque divulga programacao cultural de jatai para dezembro",
    "https://www.sescgo.com.br/noticias/claque-divulga-programacao-cultural-de-jatai-para-dezembro/"
   ],
   [
    "theatro sebastiao pompeu de pina em pirenopolis go oferece programacao cultural gratuita em janeiro",
    "https://www.sescgo.com.br/noticias/theatro-sebastiao-pompeu-de-pina-em-pirenopolis-go-oferece-programacao-cultural-gratuita-em-janeiro/"
   ],
   [
    "sesc goias divugla alteracao dde cronograma no edital de credenciamento de guias de turismo",
    "https://www.sescgo.com.br/wp-content/themes/sesc-go/assets/files/politica-de-cookies-sesc-goias.pdf"
   ],
   [
    "cine teatro sao joaquim tem programacao gratuita com teatro e musica em maio",
    "https://www.sescgo.com.br/noticias/cine-teatro-sao-joaquim-tem-programacao-gratuita-com-teatro-e-musica-em-maio/"
   ]
  ]
 ],
 "site-transferegov": [
  [],
  [
   [
    "Ferramentas de Gestão e Transparência",
    "https://www.gov.br/transferegov/pt-br/ferramentas-gestao"
   ],
   [
    "Acesso a sistemas",
    "https://www.gov.br/transferegov/pt-br/sistemas"
   ],
   [
    "Sistema Modelo Gestaopublicagov.br",
    "https://www.gov.br/transferegov/pt-br/sistemas/sistema-modelo-gestao-gov.br"
   ],
   [
    "Acesso Livre",
    "https://www.gov.br/transferegov/pt-br/sistemas/acesso-livre"
   ]
  ]
 ],
 "mpu-destinacao": [
  [
   [
    "CHAMAMENTO PÚBLICO PARA CADASTRAMENTO DE PESSOAS JURÍDICAS DE ...",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-go/transparencia/entidades-cadastradas-recebimento-bens-valores/edital-18_2025-gabpc-pr-go-00023045_2025-1.pdf/@@download/file"
   ],
   [
    "edital 24_2025 gabpc pr sp 00127286_2025.pdf",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-sp/noticias/edital-24_2025-gabpc-pr-sp-00127286_2025.pdf"
   ],
   [
    "bens e valores",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-ap/transparencia/bens-e-valores"
   ],
   [
    "FDD/Pronasci - cultura e cidadania em territórios vulneráveis — Brasil",
    "https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/direitos-difusos"
   ]
  ],
  [
   [
    "Edital - atualizacao do cronograma.pdf",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-sp/estagio/edital-atualizacao-do-cronograma-2-26.pdf"
   ],
   [
    "2%20Edital_de_abertura_1 2024_legislacaoalterada.pdf",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-sp/estagio/2%20Edital_de_abertura_1-2024_legislacaoalterada.pdf"
   ],
   [
    "Edital%20de%20abertura%20assinado.pdf",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-sp/estagio/Edital%20de%20abertura%20assinado.pdf"
   ],
   [
    "Edital%20divulgacao%20gabarito_assinado.pdf",
    "https://www.mpf.mp.br/o-mpf/unidades/pr-sp/estagio/Edital%20divulgacao%20gabarito_assinado.pdf"
   ]
  ]
 ],
 "site-capitaai": [
  [
   [
    "Edital Floresta Viva – Águas do São FranciscoBNDES / FUNBIOR$ 17,8 miAceita:organizações da sociedade civilPrazo:02/12/2",
    "https://capitaai.com.br/captacao/floresta-viva-aguas-sao-francisco-bndes-dgztj1"
   ],
   [
    "Programa Funarte Aberta 2026: Edital Minas Geraisaté 30 de abr. de 2027",
    "https://capitaai.com.br/captacao/programa-funarte-aberta-2026-complexo-funarte-fundacao-nacional-xba92p"
   ],
   [
    "Edital CEPI Vacinas 2026: Guia de Captação e Inscrição",
    "https://capitaai.com.br/captacao/cepi-innovations-prepare-for-future-epidemics-pandemics-area-hmdl07"
   ],
   [
    "Edital CEPI Vacinas 2026: Tecnologias e Inovação",
    "https://capitaai.com.br/captacao/cepi-tecnologias-analiticas-inovadoras-acelerar-fabricacao-vacinas-ace-selgdv"
   ]
  ],
  [
   [
    "top 10 editais para prefeituras em 2026 saude educacao infraestrutura",
    "https://capitaai.com.br/blog/top-10-editais-para-prefeituras-em-2026-saude-educacao-infraestrutura"
   ],
   [
    "autodeclaracao etnico racial modelo para edital",
    "https://capitaai.com.br/blog/autodeclaracao-etnico-racial-modelo-para-edital"
   ],
   [
    "RECIBO DE DOAÇÃO Nº [NÚMERO]",
    "https://capitaai.com.br/modelos/arquivos/recibo-de-doacao.docx"
   ],
   [
    "checklist documentos edital",
    "https://capitaai.com.br/ferramentas/checklist-documentos-edital"
   ]
  ]
 ],
 "governo-federal": [
  [
   [
    "Programa Nacional dos Comitês de Cultura (PNCC)",
    "https://www.gov.br/cultura/pt-br/acesso-a-informacao/perguntas-frequentes/programa-nacional-dos-comites-de-cultura"
   ],
   [
    "Edital CP 004_2022",
    "https://www.anater.org/wp-content/uploads/2022/07/EDITAL-DE-CHAMAMENTO-PUBLICO-No-001-2022.pdf"
   ],
   [
    "EDITAL DE SELEÇÃO PÚBLICA Nº 04_2026_QUINTAIS PRODUTIVOS RIO DOCE",
    "https://www.anater.org/wp-content/uploads/2026/10/EDITAL-DE-SELECAO-PUBLICA-No-04_2026_QUINTAIS-PRODUTIVOS-RIO-DOCE.pdf"
   ],
   [
    "Resposta a Impugnação da Chamada Pública nº 001/2026",
    "https://www.anater.org/wp-content/uploads/2026/02/SEI_50224515_Resposta_a_impugnacao-6.pdf"
   ]
  ],
  [
   [
    "Encerramento da Vigência do Processo Seletivo Simplificado – Edital nº 001/2025 – ANATER/DF",
    "https://www.anater.org/wp-content/uploads/2026/08/COMUNICADO_Termino-Vigencia-PSS-01.2025.pdf"
   ],
   [
    "Convocação 01– INSTITUTO ACARIQUARA ORGANIZAÇÃO DE SERVIÇOS SOCIOAMBIENTAIS SUSTENTAVEIS – Edital de Chamada Pública de",
    "https://www.anater.org/wp-content/uploads/2023/08/CONVOCACAO-No-01-INSTITUTO-ACARIQUARA-ORGANIZACAO-DE-SERVICOS-SOCIOAMBIENTAIS-SUSTENTAVEIS.pdf"
   ],
   [
    "Convocação 02– INSTITUTO NACIONAL DE ADMINISTRATAÇÃO, PROJETOS E ESTUDOS MUNICIPAIS – Edital de Chamada Pública de ATER",
    "https://www.anater.org/wp-content/uploads/2023/08/CONVOCACAO-No-02-INSTITUTO-NACIONAL-DE-ADMINISTRATACAO-PROJETOS-E-ESTUDOS-MUNICIPAIS.pdf"
   ],
   [
    "Convocação 03– LEGALIZA BRASIL GESTAO TERRITORIAL GEOTECNOLOGICA LTDA – Edital de Chamada Pública de ATER nº 001_2023",
    "https://www.anater.org/wp-content/uploads/2023/08/CONVOCACAO-No-29-LEGALIZA-BRASIL-GESTAO-TERRITORIAL-GEOTECNOLOGICA-LTDA.pdf"
   ]
  ]
 ]
}


def test_os_vetos_novos_nao_barram_as_oportunidades_reais():
    for motor, (bons, _ruins) in CASOS.items():
        for titulo, link in bons:
            assert not _barra(motor, titulo, link), (motor, titulo)


def test_os_vetos_novos_barram_o_ruido_confirmado():
    for motor, (_bons, ruins) in CASOS.items():
        for titulo, link in ruins:
            assert _barra(motor, titulo, link), (motor, titulo, link)


def test_as_fontes_de_compras_sairam_e_a_ferramenta_esta_no_modelo():
    ss = tomllib.loads((CFG / "sistema-s.toml").read_text(encoding="utf-8"))
    assert not any("www3.sescgo.com.br/licitac" in f["url"] or "PortalCf/Licitacoes" in f["url"] for f in ss["fonte"])
    tg = tomllib.loads((CFG / "site-transferegov.toml").read_text(encoding="utf-8"))
    assert not any("www.gov.br/sitemap.xml.gz" in f["url"] for f in tg["fonte"])
    assert "vetos_endereco" in Path("eldorado/base/motor_modelo/modelo.toml").read_text(encoding="utf-8")
