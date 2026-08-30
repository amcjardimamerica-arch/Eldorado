# Eldorado + Farol de Alexandria

Sistema nacional, auditável e econômico para localizar recursos destinados a organizações da sociedade civil e transformar oportunidades verificadas em decisões, planos de trabalho e trilhas de prestação de contas.

## As duas partes

| Módulo | Função | Resultado |
|---|---|---|
| **Eldorado** | Monitora fontes públicas, privadas e plataformas de editais; deduplica; registra evidências; acompanha cinco anos de histórico por financiador | oportunidades verificadas e dossiês individualizados |
| **Farol de Alexandria** | Aplica requisitos eliminatórios, pontua aderência de cada associação, consulta leis/procedimentos e prepara pacotes de trabalho | ranking explicável, checklist, plano de trabalho e prestação de contas |

As partes usam um identificador imutável de oportunidade, mas não misturam associações. Cada perfil fica em diretório próprio e os perfis reais são ignorados pelo Git por padrão, porque este repositório é público.

## Operação automática

- Todos os dias, às **6h de Brasília**, o GitHub Actions executa a coleta, validação, classificação, dossiês e painel.
- Aos domingos, a rotina histórica revisita uma janela móvel de cinco anos e mantém achados de busca como pistas até validação primária. Um cursor limita a carga e avança a cobertura a cada execução.
- Mensalmente, o Farol confere a vigência e a integridade do catálogo jurídico; alterações normativas ficam marcadas para revisão humana.
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
4. Cadastre cada associação copiando `dados/associacoes/EXEMPLO/perfil.json` para `dados/associacoes/SLUG/perfil_publico.json`. Inclua apenas critérios de elegibilidade não sensíveis; contatos, CNPJ, documentos, certidões e dados bancários ficam fora do Git.
5. Execute localmente: `python -m src.executar_diario`.

## Estrutura

```text
config/                       fontes e regras de pontuação
src/                          coleta, normalização, dossiês, matching e painel
dados/oportunidades/          banco JSONL deduplicado
dados/financiadores/          um dossiê por organização financiadora
dados/associacoes/            isolamento estrito por associação
biblioteca/leis/              catálogo jurídico e vigência
biblioteca/procedimentos/     procedimentos e checklists reutilizáveis
biblioteca/modelos/           modelos versionados
acervo_importado/             índice verificável do anexo fornecido
docs/                         painel estático e dados filtráveis
estado/                       hashes, cache HTTP e auditoria
```

Consulte também [ARQUITETURA.md](ARQUITETURA.md), [SEGURANCA.md](SEGURANCA.md) e [OPERACAO.md](OPERACAO.md).
