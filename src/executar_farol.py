"""Segundo estágio, deliberadamente separado da coleta do Eldorado."""
from __future__ import annotations
import json
from . import casos, farol, painel, triagem

def main():
    triggers=triagem.run(); cases=casos.run(triggers) if triggers else 0; result = farol.run()
    painel.run()
    print(json.dumps({**result,"gatilhos":len(triggers),"casos_preparados":cases}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
