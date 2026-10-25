"""O estudo das IAs (titular, 25/10/2026): uma Qwen3-8B para as três funções (o Interceptador, o Espião e o Comandante)
ou uma para cada? Mede, na máquina da produção, as três tarefas reais nos três arranjos. Não faz parte do funcionamento."""
import json, subprocess, sys, threading, time, urllib.request

EDITAL = ("EDITAL DE CHAMAMENTO PÚBLICO Nº 07/2026. A Secretaria de Estado da Cultura de Goiás torna público o chamamento de "
          "organizações da sociedade civil para fomento a projetos culturais. Inscrições de 01/11/2026 a 30/11/2026, pelo "
          "sistema Mapa Cultural. Valor total: R$ 3.000.000,00, em 30 projetos de até R$ 100.000,00. Requisitos: OSC com sede "
          "em Goiás há mais de 2 anos, CNPJ ativo, certidões negativas. Resultado preliminar em 15/12/2026; recurso em 5 dias úteis. ") * 6
TAREFAS = {
    "interceptador": (f"Extraia em JSON os itens do edital (objeto, prazo, valor, requisitos, resultado, recurso):\n{EDITAL}\nJSON:", 200),
    "espiao": ("Crie 5 consultas de busca na web para encontrar editais abertos para associações de Goiás em 2026, "
               "na área de assistência social e cultura. Uma por linha:\n", 150),
    "comandante": ("Resuma para a titular, em português claro, as decisões do dia: 45 motores leram, 12 achados aceitos, "
                   "3 livros chegaram ao ouro, 2 editais fecham em 7 dias, o Espião fez 40 missões e o Interceptador "
                   "completou 5 livros. Diga o que ela deve decidir primeiro e por quê:\n", 300),
}
memoria = []

def amostrar(parar):
    while not parar.is_set():
        try:
            usado = int(subprocess.run(["free", "-m"], capture_output=True, text=True).stdout.split("\n")[1].split()[2])
            memoria.append(usado)
        except Exception:
            pass
        time.sleep(1)

def pedir(porta, tarefa):
    prompt, n = TAREFAS[tarefa]
    corpo = json.dumps({"prompt": prompt, "n_predict": n, "temperature": 0, "ignore_eos": True, "cache_prompt": False}).encode()
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{porta}/completion", data=corpo,
                                                                 headers={"Content-Type": "application/json"}), timeout=1800).read())
    tm = r.get("timings", {})
    return {"tarefa": tarefa, "segundos": round(time.time() - t0, 1), "leitura_tok_s": round(tm.get("prompt_per_second", 0), 1),
            "geracao_tok_s": round(tm.get("predicted_per_second", 0), 2), "tokens_entrada": tm.get("prompt_n"), "tokens_saida": tm.get("predicted_n")}

def cenario(nome, portas, simultaneo):
    memoria.clear(); parar = threading.Event(); threading.Thread(target=amostrar, args=(parar,), daemon=True).start()
    t0 = time.time(); res = []
    if simultaneo:
        fios = [threading.Thread(target=lambda t=t, p=p: res.append(pedir(p, t))) for t, p in zip(TAREFAS, portas)]
        [f.start() for f in fios]; [f.join() for f in fios]
    else:
        for t in TAREFAS: res.append(pedir(portas[0], t))
    parar.set()
    total = round(time.time() - t0, 1)
    print(json.dumps({"cenario": nome, "total_s": total, "memoria_pico_mb": max(memoria or [0]), "tarefas": res}, ensure_ascii=False))
    print(f"::notice title={nome}::total {total} s · memória no pico {max(memoria or [0])} MB · " +
          " · ".join(f"{r['tarefa']} {r['segundos']} s (gera {r['geracao_tok_s']} tok/s)" for r in res))

if __name__ == "__main__":
    nome, simult, *portas = sys.argv[1:]
    cenario(nome, [int(p) for p in portas], simult == "sim")
