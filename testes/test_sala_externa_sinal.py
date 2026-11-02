"""02/11/2026 (titular): o sinal de cada etapa da Sala vem dos instrumentos que o detalhe mostra — nenhuma etapa acende
alerta por uma regra escondida (a Verificação externa ficava amarela com qualquer livro na fila do Chrome, sem motivo visível)."""
from pathlib import Path


def test_a_verificacao_externa_acende_pelos_seus_instrumentos():
    p = Path("eldorado/base/painel/pagina/dashboard.html").read_text(encoding="utf-8")
    assert 'et.id==="externa"?((M[6]' not in p
    assert ':pior(L.length?L:[{estado:"cinza"}]);' in p
