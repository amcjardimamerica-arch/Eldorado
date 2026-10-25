---
name: comandante-decidir-coleta
description: "Decide quais motores reacionar, pela política aprendida no Arquivo do Cérebro (Vowpal Wabbit), com o contexto da hora, do dia, dos dias sem achado e do rendimento; registra cada escolha com o motivo."
version: 1.0.0
license: MIT
metadata:
  eldorado:
    dono: comandante
    etapa: "C1 · C2"
    evidencia: "decisoes:coleta"
  hermes:
    tags: [comandante, eldorado]
    related_skills: [aprendizado-avaliar-decisoes, comandante-parametrizar]
---

# comandante-decidir-coleta

Decide quais motores reacionar, pela política aprendida no Arquivo do Cérebro (Vowpal Wabbit), com o contexto da hora, do dia, dos dias sem achado e do rendimento; registra cada escolha com o motivo.

O uso e o resultado desta skill são contados pela evidência no Arquivo do Cérebro (`decisoes:coleta`); o curador do Aprendizado a
mantém ativa, parada ou arquivada (nunca apaga). Formato aberto SKILL.md (o mesmo das skills do Hermes Agent e da Anthropic).
