# Eldorado · Ficha da oportunidade (janela ao clicar) · 12/10/2026

## Finalidade
1. **Os cartões voltam a ser como eram** (sem botões; nada muda neles).
2. **Clicar no cartão abre uma janela** (ficha da oportunidade) com TODAS as informações: o achado (qual motor
   encontrou, datas, trecho que indica ser oportunidade), a esteira (o que foi feito, quais sistemas já averiguaram, o
   que falta para completar) e o livro (tudo o que o livro da oportunidade guarda).
3. **As ações ficam dentro da janela**: ✓ Inscrição realizada (arquivar) · ✕ Descartar · ✦ Aprimorar análise com IA ·
   Exportar decisões.
4. **Descartar não apaga o livro**: sinaliza o livro para o Claude analisar se exclui ou não.

## Dados da ficha (gerados por `src/fichas_oportunidades.py` → `docs/dados/fichas_oportunidades.json`)
- **Identificação:** título, órgão, UF, área, endereço oficial, link de origem.
- **Achado:** cada origem (ids_origem) com o motor/sensor ou agregador que encontrou, a fonte, as datas (descoberta,
  coleta, publicação, primeira vez vista) e o **trecho** (evidência) que indica ser oportunidade.
- **Esteira:** etapa atual, próximo passo, desde quando está no passo, estagnação, os 12 itens (conhecidos,
  dispensados e o que falta), onde buscar, nota da rede neural, prioridade.
- **Sistemas que averiguaram:** motores (coleta), rede neural (nota), Cartório (certidão), Interceptador (inspeção),
  validação individual/Chrome, verificação externa — com data e resultado de cada um; e o que ainda falta.
- **Livro:** id, nome, selo e estante, edições anteriores (histórico), previsão da próxima janela, regime de
  inscrição, como o livro é acionado (termos, motores, origens), diagnóstico, validação, vigilância (ligado ou não),
  criado em, última leitura e, se houver, a sinalização de revisão.

## Descarte → sinalizador no livro
- No painel, Descartar grava a decisão (como sempre) e avisa: o livro **não é apagado**; ao exportar as decisões
  para `estado/decisoes_editais.json`, o livro recebe `revisao_exclusao` (pedido em, por, oportunidade, motivo,
  situação "aguardando análise do Claude") e entra na fila `docs/dados/fila_revisao_exclusao.json`.
- A oportunidade descartada sai de Em andamento (no painel na hora; no repositório, depois da exportação, como
  "descartada pela titular — aguardando análise do Claude"). Inscrição realizada: "inscrição realizada".
- Roda no monitoramento diário e no fluxo 22 (uma vez por dia), junto do arquivamento na Biblioteca.
