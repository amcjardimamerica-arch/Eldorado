from __future__ import annotations
import json
from . import dossies, eldorado, farol, painel

def main():
    coleta=eldorado.run(); financiadores=dossies.run(); matching=farol.run(); painel.run()
    print(json.dumps({"coleta":coleta,"financiadores":financiadores,"associacoes":len(matching["associacoes"])},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()

