from __future__ import annotations
import json
from . import dossies, eldorado, painel, verificacao_social

def main():
    coleta=eldorado.run(); social=verificacao_social.run(); financiadores=dossies.run(); painel.run()
    print(json.dumps({"coleta":coleta,"verificacao_social":social,"financiadores":financiadores,"farol":"não executado; segundo estágio separado"},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
