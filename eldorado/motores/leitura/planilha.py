"""Planilhas XLSX, XLS, XLSB e ODS (python-calamine, 13× mais rápido que o openpyxl, medido). Uma página por aba."""
from __future__ import annotations

from python_calamine import CalamineWorkbook

from .leitores import Leitura, Pagina, Registro, sha256


def _celula(v) -> str:
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return "" if v is None else str(v)


class LeitorPlanilha:
    nome = "planilha (calamine)"
    tipos = ("xlsx", "xls", "ods")

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        r = Leitura(tipo="planilha", leitor=self.nome, sha256=sha256(conteudo))
        wb = CalamineWorkbook.from_filelike(__import__("io").BytesIO(conteudo))
        for i, aba in enumerate(wb.sheet_names, 1):
            linhas = [[_celula(c) for c in lin] for lin in wb.get_sheet_by_name(aba).to_python()]
            linhas = [lin for lin in linhas if any(c.strip() for c in lin)]
            r.tabelas.append(linhas)
            r.paginas.append(Pagina(i, f"[{aba}]\n" + "\n".join("\t".join(lin) for lin in linhas)))
        r.dados["abas"] = wb.sheet_names
        return r
