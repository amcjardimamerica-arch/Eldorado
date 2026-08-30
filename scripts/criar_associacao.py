"""Cria um universo isolado para uma associação."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.nucleo import ROOT, slug

FOLDERS={
    "conhecimento":"Perfil, capacidades, territórios, projetos e eventos comprováveis.",
    "documentos":"Somente manifestos e versões públicas sanitizadas. Originais ficam fora do Git.",
    "imagens":"Manifestos de imagens; fotografias identificáveis exigem autorização antes da publicação.",
    "editais":"Editais encaminhados exclusivamente a esta associação.",
    "planos_trabalho":"Planos de trabalho e respectivas versões.",
    "prestacoes_contas":"Manuais, evidências e prestações de contas desta associação.",
    "farol/casos":"Um diretório por oportunidade elegível, sem acesso a outras associações.",
}

def create(identifier: str, name: str) -> Path:
    aid=slug(identifier); root=(ROOT/"dados/associacoes"/aid).resolve(); base=(ROOT/"dados/associacoes").resolve()
    if root.parent!=base: raise ValueError("identificador inválido")
    root.mkdir(parents=True,exist_ok=True)
    profile=root/"perfil_publico.json"
    if not profile.exists():
        profile.write_text(json.dumps({"id":aid,"nome":name,"territorios":[],"areas":[],"anos_existencia":None,"natureza_juridica":"associacao_privada_sem_fins_lucrativos","certificacoes":[],"documentos_validos":[],"experiencias":[],"capacidade_execucao":None,"status_revisao":"rascunho"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for rel,description in FOLDERS.items():
        folder=root/rel; folder.mkdir(parents=True,exist_ok=True)
        readme=folder/"README.md"
        if not readme.exists(): readme.write_text(f"# {rel.split('/')[-1].replace('_',' ').title()}\n\n{description}\n",encoding="utf-8")
    return root

if __name__=="__main__":
    if len(sys.argv)<3: raise SystemExit("uso: criar_associacao.py IDENTIFICADOR NOME")
    print(create(sys.argv[1]," ".join(sys.argv[2:])))
