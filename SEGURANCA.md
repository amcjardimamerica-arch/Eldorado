# Segurança

- Use somente fontes HTTPS incluídas em `config/fontes.json`.
- Não armazene chaves no código. Segredos futuros devem ficar em GitHub Actions Secrets.
- O token automático recebe apenas `contents: write` e `issues: write` no fluxo diário.
- O DOCX original da associação não é publicado quando contém PII. A camada pública usa texto/tabelas compactados e sanitizados; imagens são apenas catalogadas por hash até autorização.
- Integrações com Google Drive começam inativas, em modo somente leitura e com uma pasta exclusiva por associação.
- Nenhum conselheiro recebe a resposta de outro. O parecer final só é liberado após sete arquivos válidos e uma nova inspeção de prompt injection.
- Downloads têm limite de tamanho, timeout, validação de tipo e bloqueio de redes privadas.
- HTML, PDF, RSS e texto coletados são conteúdo não confiável. Frases de controle de modelo geram `quarentena_prompt_injection`.
- Evidências são identificadas por SHA-256; mudanças silenciosas criam nova versão.
- Não há execução de arquivos coletados, macros, JavaScript remoto ou comandos encontrados em documentos.
- Perfis reais de associações, documentos pessoais e dados bancários não devem ser versionados em repositório público.
- Uma saída de IA é rascunho: prazo, valor, vigência, elegibilidade e dispositivo legal exigem conferência na fonte primária.

## Resposta a incidentes

Desative o workflow, preserve `estado/auditoria.jsonl`, remova ou revogue o segredo afetado, registre o evento e só retome depois de validar hashes e permissões. Nunca reescreva o histórico para esconder um incidente.
