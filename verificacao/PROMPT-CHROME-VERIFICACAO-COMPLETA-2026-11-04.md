# Verificação completa pelo Claude no Chrome — lote-2026-11-04-completo

Repositório: `amcjardimamerica-arch/Eldorado` (público). Leia os arquivos direto do GitHub.

## Objetivo

Decidir TODOS os livros que ainda estão sem decisão no Eldorado e fazer, junto, o expurgo dos documentos. Depois desta
verificação não pode sobrar nenhuma pendência: o sistema fica livre para as oportunidades novas.

| O que | Quantidade | Onde |
|---|---|---|
| Livros sem decisão | 942 (541 na verificação externa, 386 na preparação, 15 na recepção; inclui os 232 chegados na semana ainda sem decisão) | `verificacao/lotes/lote-2026-11-04-completo-parte-1.json` a `-parte-19.json` (50 por parte; a última com 42) |
| Documentos para o expurgo junto | 16 lotes | `verificacao/expurgo/lote-chrome-documentos-*.json` |

Os livros já vêm na ordem do Comandante: Goiás → Brasil → internacional → outras capitais e estados; dentro de cada um,
as abertas que fecham antes. Os livros com `"verificacao_para_expurgo": true` (818) não têm nenhuma estrela: ache a
oportunidade oficial ou decida o expurgo.

## ENTREGA COMPLETA E TOTAL (R41) — obrigatória

1. Trabalhe UMA PARTE de cada vez. Antes de começar, conte os livros da parte (`total_livros`).
2. Entregue UM veredito decisivo para CADA livro da parte, num único arquivo por parte.
3. Copie do arquivo da parte o `lote` (ex.: `lote-2026-11-04-completo-parte-7`) e o `gerado_em` (no campo `lote_gerado_em`).
4. É proibido reduzir o escopo, escolher só uma parte dos livros, deixar livro como "pendente" ou "não verificado".
5. Se não conseguir terminar uma parte, não entregue essa parte. O sistema recusa por inteiro o veredito que não cobre
   todos os livros da parte, e nada dele é importado.

## As quatro decisões (use exatamente estas palavras)

| decisao | Quando | O que o sistema faz |
|---|---|---|
| `valido` | É oportunidade para o terceiro setor (OSC, associação, fundação), aberta ou de fluxo contínuo | Grava os itens e as dispensas; com prazo aberto vai ao Farol; sem prazo aberto, ao arquivo. Não volta à fila. |
| `encerrada` | É oportunidade do terceiro setor, mas as inscrições encerraram (fase de habilitação, resultado, edição anterior sem nova) | Fica no banco, no arquivo |
| `arquivar` | É oportunidade real do terceiro setor, mas fora do perfil: edital privado ou federal restrito a outra região (ex.: só Amazônia, só Nordeste) | Fica no banco, no arquivo |
| `descartar` | NÃO é oportunidade para o terceiro setor | Expurgo: o livro sai do sistema |

Descarte (expurgo) é para: página institucional, menu, transparência ou notícia (gov.br e outros); notícia sem edital;
anexo isolado, áudio, formulário, errata, extrato, lista de classificados ou de suplentes (o livro é o edital-mãe);
licitação, pregão, contrato, termo de colaboração já celebrado, credenciamento de prestador de serviço, concurso público,
compra do PNAE; chamada só para pessoa física, empresa ou pesquisador; edital municipal de outro estado que não é capital;
link quebrado sem edital-mãe encontrável.

## Os 12 itens (os nomes exatos)

Objeto · Prazo de inscrição · Resultado · Prazo de recurso · Valor · Órgão / financiador · Território · Esfera ·
Requisitos · Anexos · Modalidade · Área de atuação

- Cada item comprovado leva o `trecho` copiado do documento oficial, a `pagina` (número inteiro, ou `null`) e a `url`.
- Persiga o edital oficial com todas as regras da oportunidade. No incentivo fiscal por lei (Rouanet, Goyazes, fundos da
  criança e do idoso) não há edital comum: a lei e o chamamento são o documento oficial.
- Os valores e prazos vêm do documento oficial, nunca do replicador (CapitaAI, Observatório e semelhantes erram).
- O NÚCLEO nunca se dispensa: Objeto, Prazo de inscrição, Território.
- Os outros itens só se dispensam com a justificativa de que não se aplicam a este edital, com pelo menos 20 caracteres
  e uma destas expressões: "não se aplica", "não aplicável", "inaplicável", "não há recurso", "não há prazo de recurso",
  "sem seleção competitiva", "fluxo contínuo", "cadastro permanente", "não consta nos documentos oficiais lidos",
  "dispensado pelo …", "regime …".

## O formato do veredito de cada parte (JSON, exatamente assim)

Os `itens` e as `dispensas` são LISTAS (não dicionários).

```json
{
  "lote": "lote-2026-11-04-completo-parte-1",
  "lote_gerado_em": "<o gerado_em do arquivo da parte>",
  "total_livros": 50,
  "vereditos": [
    {
      "livro_id": "L-…",
      "decisao": "valido",
      "motivo": "por que esta decisão, em uma ou duas frases",
      "link_original": "https://… (o endereço do edital oficial)",
      "como_encontrou": "o caminho até o documento oficial",
      "itens": [
        {"item": "Objeto", "valor": "…", "trecho": "…", "pagina": 1, "url": "https://…"}
      ],
      "dispensas": [
        {"item": "Prazo de recurso", "justificativa": "não há recurso previsto: fluxo contínuo de propostas"}
      ],
      "aprendizado": "o que o motor deve fazer da próxima vez para achar este edital"
    }
  ]
}
```

Grave como `verificacao/vereditos/veredito-lote-2026-11-04-completo-parte-N.json` (uma por parte).

## O expurgo dos documentos (junto)

Para cada um dos 16 arquivos `verificacao/expurgo/lote-chrome-documentos-*.json`, entregue um veredito completo (todos os
grupos), com o `lote` copiado do arquivo, em `verificacao/expurgo/vereditos/veredito-<nome do arquivo>.json`:

```json
{"lote": "<o nome do arquivo do lote>", "vereditos": [{"grupo": "G-…", "decisao": "oportunidade | vincular | descartar",
 "motivo": "…", "titulo": "…", "orgao": "…", "link_oficial": "…", "prazo_inscricao": "AAAA-MM-DD", "trecho": "…", "livro_id": "…"}]}
```

## Ao terminar

Uma planilha de controle com o total de cada parte (entregue / não entregue) e os aprendizados que se repetiram. Nada
parcial: a parte que não foi verificada inteira não é entregue.
