"""29/09: um erro de recuo em src/investigador.py derrubou TODOS os voos do Interceptador por horas. Todo arquivo
Python do sistema precisa compilar — este teste pega o erro antes da publicação."""
import glob, py_compile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


class TesteCodigoCompila(unittest.TestCase):
    def test_todo_arquivo_python_compila(self):
        erros = []
        for f in sorted(glob.glob(str(ROOT / "src/**/*.py"), recursive=True) + glob.glob(str(ROOT / "scripts/**/*.py"), recursive=True)):
            try:
                py_compile.compile(f, doraise=True)
            except py_compile.PyCompileError as e:
                erros.append(f"{Path(f).relative_to(ROOT)}: {str(e).splitlines()[-1]}")
        self.assertEqual(erros, [], "arquivo com erro de sintaxe")

    def test_pilotos_importam(self):
        import importlib, sys
        sys.path.insert(0, str(ROOT))
        for m in ("src.interceptador", "src.investigador", "src.piloto", "src.fluxo_oportunidades", "src.motores"):
            importlib.import_module(m)


if __name__ == "__main__":
    unittest.main()
