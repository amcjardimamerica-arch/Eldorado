from __future__ import annotations
import json
from . import casos, dossies, eldorado, painel, triagem, verificacao_social

def main():
    coleta=eldorado.run(); social=verificacao_social.run(); financiadores=dossies.run(); gatilhos=triagem.run(); casos_criados=casos.run(gatilhos) if gatilhos else 0; painel.run()
    print(json.dumps({"coleta":coleta,"verificacao_social":social,"financiadores":financiadores,"gatilhos_farol":len(gatilhos),"casos_farol_criados":casos_criados},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
