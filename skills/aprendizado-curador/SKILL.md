---
name: aprendizado-curador
description: "Mantém as skills pelo uso e pelo resultado (ativa, parada, arquivada; nunca apaga), monta o grafo do aprendizado e propõe as melhorias das skills que rendem pouco."
version: 1.0.0
license: MIT
metadata:
  eldorado:
    dono: aprendizado
    etapa: "A5"
    evidencia: "passo:curar"
  hermes:
    tags: [aprendizado, eldorado]
    related_skills: [aprendizado-memoria]
---

# aprendizado-curador

Mantém as skills pelo uso e pelo resultado (ativa, parada, arquivada; nunca apaga), monta o grafo do aprendizado e propõe as melhorias das skills que rendem pouco.

O uso e o resultado desta skill são contados pela evidência no Arquivo do Cérebro (`passo:curar`); o curador do Aprendizado a
mantém ativa, parada ou arquivada (nunca apaga). Formato aberto SKILL.md (o mesmo das skills do Hermes Agent e da Anthropic).
