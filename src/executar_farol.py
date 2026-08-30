"""Segundo estágio, deliberadamente separado da coleta do Eldorado."""
from __future__ import annotations
import json
from . import farol, painel

def main():
    result = farol.run()
    painel.run()
    print(json.dumps({"associacoes": len(result["associacoes"])}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
