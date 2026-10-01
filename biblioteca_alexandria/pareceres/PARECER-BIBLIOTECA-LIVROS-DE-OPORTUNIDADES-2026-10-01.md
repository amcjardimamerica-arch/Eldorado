# Parecer do conselho — Livros de Oportunidades da Biblioteca · 01/10/2026

Conferência de cada livro pelos parâmetros do titular (agora em `config/parametros_biblioteca.json`), feita sobre a
cópia de segurança `backup/antes-da-conferencia-dos-livros-2026-10-01`.

## O que a conferência encontrou e fez

| | antes | depois |
|---|---:|---:|
| Registros na Biblioteca | 1.022 | **539 livros** + 53 fontes de busca |
| Públicos municipais de outros estados | 422 | **0** (arquivados, sem perda) |
| Empresas sem edital por concorrência | 53 como livros | **53 fontes de busca** (vigiadas, não são livros) |
| Duplicatas | 14 livros repetidos | **juntados** no livro sobrevivente |
| Livros de Goiás | 135 | **183** |

- **Abrangência.** Livros públicos de órgãos municipais (prefeitura, secretaria, conselho e fundo municipais, CMDCA,
  CMAS…) ficam **só para Goiás**. De outros estados, só estaduais ou regionais — por exemplo, o edital de Pontos e
  Pontões de Cultura da Secult do Ceará continua. Os 422 arquivados (SC 48, RS 46, MG 43, SP 43, PR 41, CE 35, BA 35…,
  e 52 que estavam sem estado) estão em `biblioteca_alexandria/livros/arquivo_fora_da_abrangencia.jsonl.xz`; 5 deles
  tinham a pesquisa dos 12 parâmetros, preservada no arquivo.
- **Estado pelo endereço oficial.** Livros sem estado identificado ganharam o estado pelo domínio oficial
  (`paracuru.ce.gov.br` é prefeitura do Ceará; `secult.ce.gov.br` é o estado) — Goiás passou de 135 para 183 livros.
- **Empresas.** Empresa só é livro como **edital** (programa por concorrência), em qualquer região. "Fundação Itaú",
  "Instituto Coca-Cola Brasil", "Instituto Neoenergia" e outras 50 viraram fontes de busca: os motores continuam
  vigiando esses sites, e o edital, quando sair, vira livro. A pesquisa de 26 delas foi preservada.
- **Duplicatas** juntadas: Edital Ambev 2026, Programa Goyazes, PNAB Goiás - Pontos de Cultura, Edital Cultura
  Goiatuba, Secult Goiás (Ocupa Goiás), Goiás Social, Sonhar o Mundo, GIFE, entre outros. O livro que fica é o
  pesquisado, o que está em leitura ou o original do catálogo; o histórico, o checklist e os ids dos outros vão para ele.

## As 293 oportunidades da alimentação inicial

**214 têm livro · 42 são fontes de busca (empresas) · 18 arquivadas (municipais de outros estados) · 19 sem livro
próprio** — todas modalidades de emenda parlamentar (municipal, estadual e federal, por área), cobertas pelos 3 livros
de emenda e pela configuração de emendas.

## O parâmetro contra duplicidade

Dois livros são a **mesma oportunidade** quando estão no mesmo lugar (estado e cidade) e o nome — sem anos, números e
palavras genéricas — coincide por inteiro (não basta um conter o outro), com o mesmo financiador ou a mesma página.
Título genérico só é duplicata com a mesma página. O parâmetro vale **na criação** (o repositório e o Espião consultam
antes de criar) e **na conferência de cada ciclo**; os limites estão em `config/parametros_biblioteca.json`.

Dois erros evitados no caminho: a primeira versão juntava os três programas da SEMASDH Goiânia (estão na mesma página
da prefeitura) e editais distintos do PNAB Goiânia (Dança × Obras e Reformas). As regras foram endurecidas antes de
aplicar.

## O conselho

**Extremamente pessimista — chief engineer.** A Biblioteca tinha 40% de registros fora da regra. Sem conferência
permanente, ela voltaria a inchar a cada coleta do PNCP e do Querido Diário — que trazem prefeituras do país inteiro.

**Pessimista — staff engineer.** O nome não basta para dizer que duas coisas são iguais: a primeira versão juntou
programas diferentes da mesma prefeitura. Duplicata tem de exigir nome inteiro, mesmo lugar e mesmo financiador ou
página.

**Levemente pessimista — professor.** Livros sem estado identificado ainda existem (um blog sobre edital de Sobral
ficou como nacional). Vale cobrar o estado na origem, nos motores.

**Neutro — CTO (ponderador).** A Biblioteca ficou do tamanho certo: 539 livros, Goiás com 183, nada perdido —
arquivo para o que saiu, fonte de busca para as empresas e junção para as repetições. Parâmetros de qualidade:
nenhum público municipal fora de Goiás; nenhum livro de empresa sem edital; nenhuma duplicata pelo parâmetro;
conferência a cada ciclo; revisão mensal dos limites de duplicidade pelo conselho.

**Levemente otimista — professor.** Separar fonte de busca de livro deixa claro o que é oportunidade e o que é lugar
onde procurar — os motores continuam vigiando as empresas sem poluir a Biblioteca.

**Otimista — staff engineer.** Goiás ganhou 48 livros só por ler o estado no endereço oficial — informação que estava
lá e não era usada.

**Extremamente otimista — CTO.** Com abrangência, empresas e duplicidade vigiadas a cada ciclo, a Biblioteca passa a
ser uma base confiável — cada livro, uma oportunidade.
