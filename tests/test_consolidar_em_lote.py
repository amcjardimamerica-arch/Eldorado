"""17/10/2026 — consolidar() gravava o catálogo de livros UMA VEZ POR ITEM do Interceptador.

Medido: 621 itens × ~1,1 s (ler + regravar biblioteca_alexandria/fontes/motores.json, 32 MB) = mais de 11 minutos
por chamada. Era isso que travava tests/test_validacao_mapa.py (duas chamadas) e o comando de produção.
Correção: um lote só. Estes testes garantem (1) uma única gravação e (2) resultado IDÊNTICO ao das chamadas avulsas.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import banco_livros as BL

LIVROS = [
    {"id": "op-existente", "programa": "Edital Fundo Estadual de Cultura Goiás Audiovisual", "orgao": "Secretaria de Cultura de Goiás",
     "uf": "GO", "pagina": "https://goias.gov.br/cultura/fundo", "historico": []},
]
ACHADOS = [
    # entra no livro existente pela chave (mesma página)
    {"id": "a1", "titulo": "Fundo Estadual", "url": "https://goias.gov.br/cultura/fundo", "orgao": "Secult GO"},
    # cria livro novo
    {"id": "a2", "titulo": "Premio Mestres da Cultura Popular Tradicional", "url": "https://cultura.gov.br/premio-mestres-2026",
     "orgao": "Ministério da Cultura"},
    # outro link do MESMO programa: deve cair no livro criado logo acima, no mesmo lote (via índice)
    {"id": "a3", "titulo": "Premio Mestres da Cultura Popular Tradicional", "url": "https://cultura.gov.br/premio-mestres-2026/inscricoes",
     "orgao": "Ministério da Cultura"},
    # releitura do mesmo achado: só anota quem releu
    {"id": "a2", "titulo": "Premio Mestres da Cultura Popular Tradicional", "url": "https://cultura.gov.br/premio-mestres-2026",
     "orgao": "Ministério da Cultura", "sensor": "outro"},
]


def _sem_relogio(doc: dict) -> dict:
    doc = json.loads(json.dumps(doc))
    doc.pop("gerado_em", None)
    for lv in doc["motores"]:
        lv.pop("criado_em", None)
    return doc


class TesteLoteIgualAvulso(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._cat = BL.CAT

    def tearDown(self):
        BL.CAT = self._cat
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _rodar(self, nome: str, lote: bool) -> dict:
        BL.CAT = self.tmp / f"{nome}.json"
        BL.CAT.write_text(json.dumps({"motores": json.loads(json.dumps(LIVROS))}), encoding="utf-8")
        if lote:
            BL.registrar_achados([dict(a) for a in ACHADOS], motor="piloto-interceptador")
        else:
            for a in ACHADOS:
                BL.registrar_achados([dict(a)], motor="piloto-interceptador")
        return json.loads(BL.CAT.read_text(encoding="utf-8"))

    def test_lote_da_o_mesmo_catalogo_que_chamadas_avulsas(self):
        avulso, lote = self._rodar("avulso", False), self._rodar("lote", True)
        self.assertEqual(_sem_relogio(lote), _sem_relogio(avulso))

    def test_link_novo_do_mesmo_programa_entra_no_livro_criado_no_mesmo_lote(self):
        doc = self._rodar("lote", True)
        dono = {aid: lv["id"] for lv in doc["motores"] for aid in (lv.get("coleta") or {})}
        self.assertEqual(dono["a1"], "op-existente")
        self.assertEqual(dono["a2"], dono["a3"], "o segundo link do mesmo programa abriu outro livro")
        self.assertEqual(len(doc["motores"]), 2)


class TesteConsolidarGravaUmaVez(unittest.TestCase):
    def test_interceptador_vai_ao_livro_numa_unica_gravacao(self):
        from src import fluxo_oportunidades as F
        pasta = Path(tempfile.mkdtemp())
        try:
            for i in range(3):
                (pasta / f"cat-{i:03d}.json").write_text(json.dumps({
                    "titulo": f"Edital de Chamamento Público {i}/2026 para Organizações da Sociedade Civil",
                    "url": f"https://www.exemplo-oficial.go.gov.br/editais/chamamento-{i}-2026",
                    "orgao": "Secretaria de Estado", "uf": "GO", "investigacao_ia": {"em": "2026-10-16"}}), encoding="utf-8")
            chamadas = []
            with mock.patch.object(F, "EXT", pasta), \
                 mock.patch("src.banco_livros.registrar_achados", side_effect=lambda ach, **k: chamadas.append(len(ach)) or {}):
                F.consolidar()
            self.assertEqual(len(chamadas), 1, f"gravou o catálogo {len(chamadas)} vezes; deve ser uma só")
            self.assertGreaterEqual(chamadas[0], 1)
        finally:
            shutil.rmtree(pasta, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
