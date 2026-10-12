# Eldorado · Piloto Espião: território de Goiás · 12/10/2026

## Finalidade
O Espião estava trazendo editais e empresas de outros estados e municípios. Regra nova: ele prospecta **empresas e
oportunidades de Goiás**. Exceções: oportunidades de empresas e sites de **abrangência nacional** (todo o Brasil) e
**oportunidades internacionais** (chamadas abertas a OSC brasileiras). **Não prospecta empresas internacionais.**

## Regra
1. **O que procurar (consultas):** a região de toda consulta é Goiás — o estado, Goiânia ou um dos 246 municípios
   (lista do IBGE em `config/territorio_goias.json`) — ou "nacional / todo o Brasil". Sai "Centro-Oeste" (mistura
   outros estados). As famílias internacionais continuam (financiadores, chamadas em inglês e espanhol).
2. **O que aceitar (resultados):** cada resultado ganha um território, lido no título e no texto da página:
   - `goias` — menciona Goiás, Goiânia, um município de Goiás ou a sigla GO;
   - `nacional` — abrangência nacional ("todo o Brasil", "todo o território nacional", "em todo o país"…);
   - `internacional` — chamada de financiador internacional (frente internacional);
   - `outro_estado` — menciona outro estado ou capital, sem Goiás e sem abrangência nacional → **descartado**,
     com o motivo "fora de Goiás (UF)";
   - `indefinido` — sem nenhum sinal: aceito como candidata (a consulta já foi feita para Goiás/Brasil).
3. **Empresas:** só entram no banco de empresas as de Goiás ou de atuação nacional. **Empresa internacional não entra**
   (financiador estrangeiro é oportunidade, não empresa a prospectar): achados da frente internacional e organizações
   com site fora do domínio .br e sem menção ao Brasil não viram empresa.
4. Cada candidata e cada empresa leva o território; os descartes por território entram nos motivos do voo.

## Verificação
Testes com casos reais de cada território; simulação sobre os achados já registrados (quantos teriam sido barrados);
comparação com a main.
