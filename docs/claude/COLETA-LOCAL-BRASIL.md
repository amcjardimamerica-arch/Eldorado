# Coleta local (Brasil) — sem custo, sem servidor, só quando a sua máquina está ligada

O robô do GitHub sai dos EUA e alguns portais goianos recusam IP estrangeiro (TJGO, Câmara e Prefeitura de Goiânia, goias.gov.br,
MPGO, Diário de Goiás). Não existe forma gratuita e confiável de fazer o GitHub parecer brasileiro; por isso esses portais são lidos
pela SUA conexão, quando você quiser — a "VPN" é o seu próprio acesso.

## Uma vez só (10 minutos)
1. Instale o Python 3.12 (python.org/downloads — marque "Add python to PATH") e o Git (git-scm.com).
2. Abra o Prompt de Comando e rode:  git clone https://github.com/amcjardimamerica-arch/Eldorado  (na pasta Documentos, por exemplo).
3. Na primeira vez que o script enviar dados, o Git pedirá usuário e senha: use o seu usuário do GitHub e um token como senha
   (GitHub → Settings → Developer settings → Personal access tokens → Fine-grained → só este repositório, permissão Contents: write).
   O Windows guarda a credencial; não pede de novo.

## Sempre que quiser (1 clique)
Clique duas vezes em  Eldorado\scripts\coleta_brasil.bat  (ou rode  python scripts/coleta_brasil.py).
O script: atualiza o repositório → lê só os portais que exigem Brasil → extrai texto dos editais → atualiza o monitor → envia ao GitHub.
Leva de 3 a 8 minutos. O painel é publicado automaticamente em até 6 horas.

No monitor da Bússola, esses motores aparecem com 🇧🇷 "aguardando coleta local (Brasil)" enquanto você não roda; após rodar, mostram
a leitura com origem "coleta local (Brasil)".

## Alternativa com o Claude Desktop (mesma coisa, sem clicar no .bat)
Na tarefa agendada do Cowork, inclua o passo: "rode python scripts/coleta_brasil.py na pasta do repositório". Ela só executa quando
o computador está ligado — o que é exatamente a sua condição.
