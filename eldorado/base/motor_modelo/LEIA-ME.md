# O motor modelo do Eldorado

**A fórmula dos motores modulares.** Este motor **não roda** e **não aparece** em nenhum relatório, painel ou inventário
de motores: ele fica no sistema base só como **plataforma de desenvolvimento** de motores novos.

## O que ele é
`modelo.toml` é uma configuração completa do motor genérico, com **todas as ferramentas do sistema** (os 10 tipos de rota,
os 4 formatos de elo da cadeia, os 7 degraus da escada, a leitura completa, o léxico, o canivete de cada achado, a
extração própria, a legislação, o programa permanente, o destino especial, o aprendizado e a métrica), cada opção
explicada. Os marcadores `«...»` são preenchidos pela fábrica a partir do estudo da titular.

## Como criar um motor a partir dele
1. `eldorado motor ficha <id>`: o que o estudo definiu e o aprendizado do Eldorado0.
2. `eldorado motor criar <id>`: copia o modelo para `eldorado/motores/canal/config/<id>.toml`, com a identidade, os
   alvos, as lições e os bloqueios preenchidos, e as rotas candidatas comentadas.
3. Grave as páginas reais (o fluxo **Gravar páginas**, inclusive pelo navegador) e escolha as rotas que responderam.
4. Ajuste o léxico próprio da fonte; desligue no canivete o que não fizer sentido.
5. `eldorado motor validar <id>`; o teste nas páginas gravadas; o fluxo **Experimentar motor** (a internet de verdade).
6. Registre em `config/modulos.toml` e dê o ponto de partida em `config/agenda.toml`.

## A regra da ferramenta nova
Toda ferramenta implantada no sistema (um campo novo na configuração, um tipo de rota, um formato de elo, um degrau, uma
habilidade do canivete) **entra também no modelo**, com a explicação. O teste `testes/test_motor_modelo.py` confere isso
contra a configuração do motor genérico e **falha enquanto faltar**.

A orientação completa: `eldorado/motores/skills/criar-motor/SKILL.md`.
