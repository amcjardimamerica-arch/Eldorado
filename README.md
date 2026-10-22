# Eldorado

Plataforma modular de busca de dados na internet. A missão atual é encontrar **oportunidades de recursos para organizações da sociedade civil**: cada oportunidade vira um **livro**, com os dados validados no documento oficial, a história de como foi encontrada e a previsão da próxima edição.

## As três partes

| Parte | O que é | Natureza |
| --- | --- | --- |
| **Base** (`eldorado/base`) | O Cérebro (Regência, Pertinência e aprendizado), o Cartório, as etapas, a missão, a análise e o painel | Fixa |
| **Motores** (`eldorado/motores`) | Os 45 motores de canal, os 2 pilotos e as ferramentas de acesso, leitura e descoberta | Modular |
| **Banco de dados** (`eldorado/banco`) | A Biblioteca, o Especial (empresas) e o banco do Cérebro, em SQLite | Modular |

A mecânica é única: a Regência planeja e aciona; cada módulo **só grava eventos**; o **gravador único** aplica os eventos aos bancos; a Pertinência mede e o Cérebro aprende; o painel mostra as visões geradas dos bancos. Nada se apaga nem se sobrescreve, e nenhum PDF ou imagem fica dentro do sistema (os originais vão ao Drive; o banco guarda o texto literal comprimido).

## Estado da criação

| Fase | Situação |
| --- | --- |
| **F1 · Fundação** (contratos, configuração, eventos, alarmes, os três bancos, o gravador) | **concluída** |
| **F2 · Execução** (workflow, executor durável, fila, agenda, governador de carga, comandos) | **concluída** |
| **F3 · Cérebro** (indicadores, regras, Pertinência, Regência, aprendizado, rede, completude) | **concluída** |
| **F4 · Cartório e missão** (portão com os casos de ouro, 12 itens, chave, índice, passaporte, certificação, selos, site oficial, passagem real) | **concluída** |
| **F5.1 · Leitura** (o canivete suíço: PDF, página, planilha, documento, compactado, expurgo, normalização, OCR e universal como reserva) | **concluída** |
| **F5.2 · Acesso** (a escada de 9 degraus, o aprendizado por domínio, o robots como informação, o computador da titular) | **concluída** |
| **F5.3 · Descoberta e motor genérico** (as 5 formas; o motor de canal feito só de configuração; o estado de cada motor) | **concluída** |
| F6 · Migração do Eldorado0 | a fazer |
| F7 · Primeiros motores (com API) | a fazer |
| F8 · Etapas e pilotos | a fazer |
| F9 · Análise e painel | a fazer |
| F10 · Demais motores e desligamento do Eldorado0 | a fazer |

Cada fase só começa quando a anterior cumpre o seu critério de pronto, com os testes verdes.

## Comandos

```bash
pip install -e ".[testes,leitura,acesso,descoberta]"   # opcionais: navegador, tor, metabusca, ocr, universal, idioma, leitura_completa

eldorado iniciar                        # cria (ou confere) os três bancos
eldorado executar workflows/passagem.toml    # a passagem completa
eldorado executar workflows/manutencao.toml
eldorado retomar <workflow> <execucao>  # retoma do passo em que parou
eldorado aplicar                        # aplica aos bancos os eventos pendentes (sem duplicar)
eldorado maquina                        # uso da máquina, folga até 85% e tamanho de cada parte
eldorado devidos                        # módulos devidos agora (uma passagem por janela)
eldorado pausar | despausar
eldorado trabalhar                      # consumidor da fila, sob o governador
```

Códigos de saída: 0 deu certo · 1 falhou · 75 adiado (sistema pausado ou sem folga na máquina).

## Testes

```bash
pytest
```

O fluxo **Qualidade** (`.github/workflows/qualidade.yml`) roda o verificador e a bateria inteira a cada gravação.

## Documentação

- `docs/01-MOTORES-NOVO-ELDORADO.md` — os motores, motor por motor, e as ferramentas compartilhadas
- `docs/02-SISTEMA-NOVO-ELDORADO.md` — a arquitetura, o workflow, a ordem de criação, as dependências e cada arquivo da base
- `docs/03-BIBLIOTECA-E-ESPECIAL-NOVO-ELDORADO.md` — os três bancos, o livro, as visões e os esquemas SQL
- `docs/A-WORKFLOW-NOVO-ELDORADO.html` — o desenho do workflow
- `docs/B-ARQUIVOS-E-VINCULOS-NOVO-ELDORADO.html` — o mapa dos arquivos e das ligações
- `docs/C-SUGESTOES-GITHUB-NOVO-ELDORADO.html` — o estudo dos 195 projetos do GitHub

## Licença

AGPL-3.0-or-later. Uso aberto; quem modificar e oferecer o sistema deve abrir o código.
