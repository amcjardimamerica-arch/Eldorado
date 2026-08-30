# Preparação para Google Drive

A integração está deliberadamente inativa. Quando for autorizada:

1. Crie uma pasta exclusiva no Drive para cada associação.
2. Compartilhe cada pasta somente com a conta de serviço ou conector aprovado.
3. Configure o ID em variável de ambiente específica, nunca no repositório.
4. Ative individualmente a associação em `config/integracoes.json`.
5. Execute a ingestão em modo somente leitura.
6. Confira o manifesto, a remoção de dados pessoais e as autorizações de imagem antes de publicar qualquer derivado.

O sistema rejeita o mesmo ID de pasta para duas associações. A integração futura deverá entregar os arquivos à mesma rotina `scripts/ingestao_associacao.py`, preservando hash, categoria e isolamento.
