"""Segundo estágio, deliberadamente separado da coleta do Eldorado.
Reexecução manual: triagem → casos → ranking → Farol IA → painel."""
from __future__ import annotations
import json
from . import casos, farol, farol_ia, painel, triagem

def main():
    triggers=triagem.run(); cases=casos.run(triggers) if triggers else 0; result = farol.run()
    resultado_ia=farol_ia.run()
    painel.run()
    print(json.dumps({**result,"gatilhos":len(triggers),"casos_preparados":cases,"farol_ia":resultado_ia}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
