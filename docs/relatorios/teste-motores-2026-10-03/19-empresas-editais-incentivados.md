# Motor 19 — Editais de empresas para FIA, Idoso, Esporte, Pronas, Pronon e Goyazes (`empresas-editais-incentivados`)

**Veredito:** workflow FALHA em 02/10 (adiado por tempo) · coleta PARCIAL (homes de empresas e busca no DuckDuckGo,
que na nuvem corta na 2ª busca) · resultado FALHA (0 achados em 19 leituras; o antecessor tem 1 ruído) · histórico de
3 anos FALHA.

## Workflow

- **Agenda (`plat-empresas-editais-incentivados`):** todos os dias, às 10:23, na nuvem. Usa o leitor genérico, e as
  rotas vêm de `src/empresas_rotas.py`: cada empresa mapeada pelos motores 20 e 21 vira rota de busca.
- **Testes:** não há teste próprio de leitura.
- **Última leitura:** 01/10, às 12:03. Em 02/10, o motor foi **adiado por tempo**, entre os 49 adiados. A luz está
  **vermelha**, com 2 falhas.
- **Antecessor `empresas-incentivadas`** (inativo): 8 leituras e 24 achados, lendo Saneago, Equatorial e o Observatório.

## Onde coleta

| Endereço | Nuvem |
|---|---|
| `portoitapoa.com/` (modelo de empresa que faz edital próprio) | HTTP 200, 275 KB |
| DuckDuckGo: "GRUPO CASAS BAHIA S.A. site oficial" | HTTP 200. Em seguida corta, como no parecer dos pilotos (2 buscas por máquina) |
| Saneago e Equatorial Goiás (antecessor) | HTTP 200 |

- **O problema:** o motor lê a home das empresas e procura "edital".
- Os editais de renúncia fiscal (FIA, Idoso, Esporte, Rouanet) costumam estar em `/instituto`, `/sustentabilidade`,
  `/editais` ou no site do instituto da empresa. O módulo de rotas já conhece esses padrões, mas a leitura não chega a
  eles.

## Resultado

- 0 achados em 19 leituras.
- O único registro do antecessor, "Edital BNDES de Cinema", é do BNDES e não de empresa incentivadora. É ruído para
  este motor.

## Histórico de 3 anos

- **Nenhum registro.**
- **Recuperação possível:**
  - os editais de empresas como Porto Itapoá, Renner e Maria Emília são anuais e ficam em páginas de arquivo;
  - os projetos que cada empresa já incentivou estão no SALIC (motor 16) e nos portais de transparência dos fundos
    (FIA e Idoso).

## Correções, por prioridade

1. **Corrigir o tempo do passo dos sensores** (ver consolidado): o motor nem rodou em 02/10.
2. **Ler as rotas certas de cada empresa** (`/instituto`, `/editais`, `/investimento-social`, site do instituto),
   geradas por `empresas_rotas.py`, em vez da home.
3. **Busca no Brasil:** a busca do site oficial de empresa é a que mais sofre com o corte do DuckDuckGo na nuvem. Ela
   deve rodar pelo navegador local (pacote dos pilotos) ou por chave de API.

## Conselho de 7 lentes

| Lente | Opinião |
|---|---|
| Extremamente pessimista | 19 dias de zero e, ontem, nem rodou. Os editais de FIA e Idoso das grandes empresas fecham em novembro e dezembro, no fim do ano fiscal. |
| Pessimista | Ler a home de uma empresa e procurar "edital" quase nunca funciona. |
| Levemente pessimista | O antecessor registrou um edital do BNDES como se fosse de empresa. |
| **Neutro** | **O motor tem a ideia certa (empresa → rotas onde ela divulga) e a execução errada. Prioridade: o tempo do passo e a leitura das rotas específicas. Meta, antes de novembro: as 60 empresas do motor 20 com a página do instituto lida.** |
| Levemente otimista | O módulo de rotas já está pronto: falta ligar a leitura a ele. |
| Otimista | Os editais de renúncia (FIA, Idoso) são exatamente o tipo de recurso de uma associação de bairro. |
| Extremamente otimista | Com o histórico de quem destinou, a associação pede direto às empresas que já destinam em Goiás. |
