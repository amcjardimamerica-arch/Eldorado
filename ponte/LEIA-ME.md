# Ponte Brasil — para os portais que recusam IP estrangeiro

Alguns portais só abrem para endereço brasileiro. Exemplos: TJGO, Câmara e Prefeitura de Goiânia, Diário de Goiás e
MPGO. O GitHub roda nos EUA. A ponte empresta um endereço brasileiro, e o motor continua igual: o mesmo leitor, as
mesmas regras e o robots.txt respeitado.

## Escada de rotas

Cada site desce a escada abaixo sozinho, e toda semana tenta de novo a rota mais barata. Nada se perde por bloqueio.

| Degrau | Quando | Quem lê |
|---|---|---|
| nuvem | sempre que o site aceita | GitHub |
| ponte | o portal recusa IP estrangeiro, ou deu 2 falhas seguidas pela nuvem | ponte HTTP, VM no Brasil ou computador do titular |
| assistida | o robots.txt proíbe robôs, a página exige JavaScript ou nem o IP brasileiro passa | titular ou Claude no Chrome (`docs/coleta-assistida.html`) |

## Três jeitos de ter a ponte

Use um, ou mais de um.

### 1. Computador do titular

- **Custo:** grátis.
- **Como funciona:** `scripts/coleta_brasil.py` já lê, com a sua conexão, os portais que exigem Brasil. Agora também
  lê os indexadores da rota "ponte".
- **Agendamento:** para rodar sozinho a cada 3 horas, das 6h às 22h, com o computador ligado, clique duas vezes em
  `scripts/agendar_coleta_brasil.bat` uma vez. O agendador do Windows faz o resto. O Claude no aplicativo de
  desktop, ligado ao seu computador, pode fazer isso por você.
- **Limite:** só lê com o computador ligado.

### 2. Máquina virtual no Brasil

- **Custo:** grátis ou de R$ 30 a 60 por mês.
- **Opções:**
  - Oracle Cloud Always Free, nas regiões São Paulo ou Vinhedo. É grátis, mas a disponibilidade depende da conta.
  - VM paga no Brasil: Magalu Cloud, Locaweb, AWS São Paulo ou outras.
- **Instalação:** rode uma vez `bash scripts/instalar_vm_brasil.sh`. A VM passa a rodar o repositório pelo cron, a cada
  3 horas, 24 horas por dia.
- **Opcional:** em vez de rodar o repositório, a VM pode servir só como ponte. Para isso, use `ponte/ponte_vm.py`.

### 3. Ponte HTTP numa hospedagem brasileira

- **Custo:** o da hospedagem que você já tiver (Hostgator, Locaweb, KingHost...).
- **Como funciona:** `ponte/ponte.php` recebe o pedido assinado do GitHub, lê o portal com o IP da hospedagem e
  devolve a página. O GitHub continua fazendo todo o trabalho, 6 vezes por dia.
- **Instalação:**
  1. Envie `ponte.php` para `public_html/ponte/`.
  2. Troque a `CHAVE` no início do arquivo por uma frase longa.
  3. Crie dois segredos no GitHub (Settings → Secrets and variables → Actions):
     - `ELDORADO_PONTE_URL` = `https://SEU-DOMINIO/ponte/ponte.php`
     - `ELDORADO_PONTE_CHAVE` = a mesma frase da `CHAVE`
- **Segurança:** a ponte não é um proxy aberto. Ela só aceita pedido assinado com menos de 5 minutos, só abre os
  domínios da lista (`python -m src.indexadores ponte-dominios`) e só destinos públicos. O limite é de 120 pedidos por
  minuto e 6 MB por página.
- **Limite:** um portal pode bloquear também IP de datacenter brasileiro. Nesse caso, o site sobe para a coleta
  assistida.

## Segredos

Nenhum segredo vai para arquivo do repositório nem para o chat:

- a chave da ponte fica no `ponte.php`, na sua hospedagem, e nos segredos do GitHub;
- o acesso da VM ao GitHub é um token criado por você, digitado só na própria VM.
