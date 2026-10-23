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


class LeitorCSV:
    """Planilhas CSV (plano C: polars): rápido também nas grandes; o separador (; ou ,) é detectado; 500 linhas por página."""
    nome = "planilha CSV (polars)"
    tipos = ("csv",)

    def ler(self, conteudo: bytes, nome: str | None, registro: Registro) -> Leitura:
        import io

        import polars as pl
        try:                                           # tudo em UTF-8 antes: as planilhas brasileiras são UTF-8 ou Windows-1252
            conteudo.decode("utf-8")
        except UnicodeDecodeError:
            try:
                conteudo = conteudo.decode("cp1252").encode("utf-8")
            except UnicodeDecodeError:                 # só por último o detector automático (erra em textos curtos)
                from charset_normalizer import from_bytes
                melhor = from_bytes(conteudo).best()
                conteudo = str(melhor).encode("utf-8") if melhor else conteudo.decode("latin-1").encode("utf-8")
        amostra = conteudo[:4000].decode("utf-8", errors="replace")
        sep = ";" if amostra.count(";") > amostra.count(",") else ","
        df = pl.read_csv(io.BytesIO(conteudo), separator=sep, infer_schema=False, ignore_errors=True, truncate_ragged_lines=True)
        linhas = [list(df.columns)] + [["" if v is None else str(v) for v in lin] for lin in df.iter_rows()]
        r = Leitura(tipo="planilha", leitor=self.nome, sha256=sha256(conteudo))
        r.tabelas.append(linhas)
        for i in range(0, len(linhas), 500):
            r.paginas.append(Pagina(i // 500 + 1, "\n".join("\t".join(lin) for lin in linhas[i:i + 500])))
        r.dados["linhas"] = len(linhas) - 1
        return r
