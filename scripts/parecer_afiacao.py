#!/usr/bin/env python3
"""Parecer de afiação dos motores (24/09/2026): causa raiz, correções, tabela motor a motor com
evolução gratuita, a evolução única do sistema e o conselho. A tabela sai dos dados atuais."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
D = json.loads((RAIZ / "docs/dados/descricao_motores.json").read_text(encoding="utf-8"))["motores"]
REL = {x["id"]: x for x in json.loads((RAIZ / "docs/dados/relatorio_motores.json").read_text(encoding="utf-8"))["motores"]}

linhas = []
for mid in sorted(D, key=lambda k: (REL.get(k, {}).get("veredito", {}).get("decisao", "~"), k)):
    d = D[mid]
    dec = REL.get(mid, {}).get("veredito", {}).get("decisao", "—")
    extra = d["para_afiar"][1:]
    fazer = "; ".join(extra) if extra else (d["para_afiar"][0].split(": ", 1)[-1] if d["para_afiar"] else "—")
    linhas.append(f"| `{mid}` | **{dec}** | {d['onde_para']} | {fazer} | {d['evolucao_gratuita']} |")

MD = """# Auditoria de afiação dos motores — 24/09/2026

## 1. O que realmente travou a busca nos últimos 20 dias

**Os motores não estavam falhando: estavam sendo impedidos de começar.** O workflow dos motores roda a suíte
de testes antes da coleta e, com qualquer falha, nenhum motor roda. Nos 20 dias até hoje, o horário das 09h UTC
teve 17 execuções e 16 falharam; o das 08h, 13 de 13 — todas no passo "Testes antes da coleta". Os blocos da
madrugada (diários, justiça, plataformas) rodaram em 4 dos 20 dias.

Seis testes seguravam o portão — dois quebrados por mim (um import de `yaml` e a regra do `piloto.json` que
reescrevi ao empossar o Qwen3), os outros por data fixa apodrecida, arquivo gerado fora do git, motor novo sem
finalidade declarada e um teste do DOU que dependia de rede sem saber. **Todos corrigidos**, e o portão foi
redesenhado: **só teste crítico bloqueia a coleta** — privacidade, segredo, injeção de prompt, data inventada. O
resto vira aviso registrado em `estado/ultimo_teste_ci.txt`, e os motores rodam.

Consequência para a leitura dos números: a "linha de busca de 20 dias" é, na prática, **uma linha de 4 a 13 dias
efetivos por bloco**. Motores julgados lentos ou secos estavam, em boa parte, simplesmente sem rodar.

## 2. Correções implantadas hoje

- **Veto geral de 12 para 37 termos**, tirados das famílias que responderam por 344 dos 409 descartes: serviço ao
  órgão (174), compra pública (69), imóvel e uso de espaço (23), instituição financeira (13), parecerista (12),
  cachê (10) e resultado ou extrato de parceria já julgada (19). O veto age no **rótulo do link**, antes de abrir
  a página: descarta sem gastar leitura — e não toca o corpo de um edital aberto que cite "resultado final" no
  cronograma.
- **Um leitor só para o Diário Oficial de Goiás.** `plat-ovg`, `plat-fapeg`, `plat-fundos-estaduais-go` e
  `plat-secult-go` deixaram de ler `diariooficial.abc.go.gov.br`; o `do-goias` lê e recebeu os termos próprios de
  cada um. As páginas próprias deles em `goias.gov.br` continuam — aquilo não era duplicata.
- **Finalidade declarada** para os quatro motores que não tinham; **cadência coerente** do `cnj-destinacoes` (30 dias).
- **Descrição interna de cada motor** no painel — objetivo, como funciona, onde para hoje, o que fazer e uma
  evolução gratuita —, visível só com o mouse parado sobre o quadro, na Bússola.

## 3. Motor a motor: o que fazer e como evoluir de graça

| motor | decisão | onde para hoje | o que fazer | evolução gratuita |
|---|---|---|---|---|
""" + "\n".join(linhas) + """

## 4. Uma única evolução para o sistema inteiro

**Um servidor próprio no Brasil, ligado ao GitHub como executor dos voos e dos motores (runner auto-hospedado).**

É a única mudança que atinge os três pontos de busca ao mesmo tempo:

- **Motores:** o endereço brasileiro libera as fontes que recusam servidor estrangeiro — Diário de Goiânia, TJGO,
  TRF1, Câmara — sem depender do seu computador ligado. (O WAF do TJGO pode continuar recusando endereço de
  datacenter; isso só se confirma na prática.)
- **Piloto:** com máquina própria, o modelo fica carregado entre voos — hoje cada voo baixa 1,1 GB e sobe o servidor
  antes de começar, parte grande de um voo de 2 minutos —, e cabe um modelo maior. Acaba a fila do GitHub que
  cancelou o benchmark duas vezes.
- **Busca:** o servidor pode hospedar um SearXNG (metabuscador de código aberto) como rota própria, somado à chave
  gratuita da Brave.

**Como pagar pouco ou nada — programas com ação social para ONGs.** *Não tenho acesso à internet nesta conversa:
os termos abaixo são os que eu conhecia até meados de 2026 e precisam ser conferidos antes de qualquer cadastro.*

- **Goodstack** (antiga Percent): valida organizações sem fins lucrativos e dá acesso a descontos de empresas
  parceiras. A AMC, com CNPJ de associação, valida-se uma vez e usa a validação em vários programas.
- **TechSoup Brasil**: doações e descontos de software e nuvem para ONGs brasileiras; historicamente, a porta para os
  créditos anuais da **AWS** para organizações sem fins lucrativos (a AWS tem região em São Paulo).
- **Microsoft para ONGs**: historicamente oferecia crédito anual de Azure a organizações elegíveis; o Azure tem região
  em São Paulo (Brazil South), onde caberia o servidor.
- **Oracle Cloud Always Free**: sem ação social, mas **gratuito** — máquina ARM de 4 núcleos e 24 GB de memória, com
  região em São Paulo. Exige cartão no cadastro e costuma ter fila de capacidade.

**Recomendação:** tentar primeiro a via social — validar a AMC na Goodstack e na TechSoup Brasil e pedir crédito de
nuvem com região em São Paulo; em paralelo, a Oracle gratuita como alternativa imediata. Se nenhuma sair, um servidor
pago pequeno em São Paulo custa na faixa de dezenas de reais por mês.

## 5. O conselho

**Extremamente pessimista — chief engineer.** Passamos dias afinando léxico de motores que nem rodavam. Nenhum número
de desempenho vale sem antes conferir se o motor executou.

**Pessimista — staff engineer.** O veto novo sai de 409 descartes de uma só rodada de análise. É boa amostra, mas
regra de exclusão precisa de retorno: se em duas semanas algum edital legítimo aparecer descartado por ela, o termo sai.

**Levemente pessimista — professor de engenharia de software.** Portão que bloqueia produção por teste de texto de
painel é defeito de desenho. Corrigido, o risco vira o oposto: aviso que ninguém lê. `estado/ultimo_teste_ci.txt`
precisa ser olhado.

**Neutro — CTO (ponderador).** Ordem de execução: (1) confirmar nos próximos dias que os blocos da madrugada voltaram
a rodar — sem isso nada mais importa; (2) medir o efeito do veto no PNCP, com meta de cair de 74% para menos de 40% de
descarte; (3) aplicar as evoluções gratuitas começando pelas de maior alcance — filtro na consulta do PNCP e API do
SALIC para empresas; (4) buscar o servidor no Brasil pela via social.

**Levemente otimista — professor de ciência da computação.** Metade das evoluções gratuitas troca raspagem por API
oficial ou feed: menos bloqueio, menos quebra por mudança de layout, dado mais limpo.

**Otimista — staff engineer.** A API do SALIC responde de uma vez uma pergunta que o sistema tenta responder por três
motores: quem já destinou por lei de incentivo, quanto e em que ano.

**Extremamente otimista — CTO.** Com os motores rodando todo dia pela primeira vez em semanas, o próximo relatório vai
medir o sistema de verdade — e é provável que muitos motores "secos" deixem de ser.
"""

if __name__ == "__main__":
    out = RAIZ / "biblioteca_alexandria/pareceres/AUDITORIA-AFIACAO-MOTORES-2026-09-24.md"
    out.write_text(MD, encoding="utf-8")
    print(f"{out.relative_to(RAIZ)} · {len(linhas)} motores")
