# Leia antes de mudar o Eldorado

Este repositório tem **regras da titular** que não podem ser quebradas nem "esquecidas" entre uma conversa e outra.
Elas estão em **`config/regras_titular.json`**, cada uma com a data, o texto, o porquê, onde é cumprida e as **travas**
(testes) que a defendem.

## Como trabalhar
1. **Antes de mudar qualquer parte**, leia `config/regras_titular.json` e veja se a mudança toca alguma regra.
2. **Nenhuma regra muda sem uma decisão da titular registrada** no próprio registro (a data, o texto e o que ela revoga).
   Se um pedido parecer contrariar uma regra, **pergunte antes** e registre a resposta.
3. **Regra nova da titular = entrada nova no registro + pelo menos uma trava** (um teste que falha se a regra for
   quebrada). O teste-mestre (`testes/test_regras_titular.py`) falha se alguma regra ficar sem trava.
4. **Nunca mude uma trava para fazer um teste passar.** Se a trava falhou, quem está errado é o código (ou a regra
   mudou: então a decisão da titular vem primeiro, registrada).
5. `eldorado travas` roda todas as travas. O ciclo permanente roda esse portão antes de começar: **com uma regra
   quebrada, o sistema não trabalha**. O fluxo de qualidade roda a bateria inteira a cada envio.
6. **Cada alteração é enviada ao GitHub na hora** (R00; a regra antiga de não enviar foi revogada pela titular).

## As regras mais lembradas (o registro é a fonte; isto é só um resumo)
- Só dois bancos: a **Biblioteca** (os livros e as empresas) e o **Cérebro** (o aprendizado, nunca livros).
- **Nenhum motor tem banco**: motores são configuração e ferramentas; só leem o Cérebro e entregam por eventos.
- **O site mostra exatamente a Biblioteca**, e nenhum dado do Eldorado0.
- A estrela pela régua da titular; **a dispensa é só pelo Claude no Chrome**; o arquivo é só para encerradas.
- Todo motor novo parte do **motor modelo** (`eldorado/base/motor_modelo/`), e toda ferramenta nova entra nele.
