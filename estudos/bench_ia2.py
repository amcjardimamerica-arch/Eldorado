"""O estudo das IAs, parte 2 (titular, 25/10/2026): uma IA exclusiva do Comandante e uma dos pilotos (os dois pilotos em
paralelo); e as ferramentas de contexto (o reaproveitamento do contexto e a decodificação especulativa). Fora do funcionamento."""
import json, sys, threading, time, urllib.request
sys.path.insert(0, "estudos")
from bench_ia import TAREFAS, EDITAL, amostrar, memoria

INSTR = {"interceptador": "Você é o Interceptador do Eldorado. Extraia do edital os 12 itens (objeto, prazo de inscrição, resultado, "
         "prazo de recurso, valor, órgão, território, esfera, requisitos, anexos, modalidade, área) em JSON, com o trecho de prova. " * 6,
         "comandante": "Você é o Comandante do Eldorado: coordena os motores, os pilotos, o Cartório e o Chrome, e apresenta à titular "
         "o que decidir. Responda em português claro, com prioridades e motivos. " * 8}

def pedir(porta, prompt, n, cache=False):
    corpo = json.dumps({"prompt": prompt, "n_predict": n, "temperature": 0, "ignore_eos": True, "cache_prompt": cache}).encode()
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{porta}/completion", data=corpo,
                                                                 headers={"Content-Type": "application/json"}), timeout=1800).read())
    tm = r.get("timings", {})
    return round(time.time() - t0, 1), round(tm.get("predicted_per_second", 0), 2), tm.get("prompt_n"), round(tm.get("prompt_per_second", 0), 1)

def notice(t, m): print(f"::notice title={t}::{m}"); print(t, m)

modo = sys.argv[1]
if modo == "decidido":                      # o Comandante (porta 9001) responde enquanto os dois pilotos (porta 9002, 2 vagas) trabalham
    memoria.clear(); parar = threading.Event(); threading.Thread(target=amostrar, args=(parar,), daemon=True).start()
    res = {}
    def piloto(t): res[t] = pedir(9002, *TAREFAS[t])
    fios = [threading.Thread(target=piloto, args=(t,)) for t in ("interceptador", "espiao")]
    [f.start() for f in fios]; time.sleep(5)
    res["comandante"] = pedir(9001, *TAREFAS["comandante"])
    [f.join() for f in fios]; parar.set()
    notice(f"decidido ({sys.argv[2]})", f"memória no pico {max(memoria or [0])} MB · " + " · ".join(f"{k} {v[0]} s (gera {v[1]} tok/s)" for k, v in res.items()))
elif modo == "contexto":                    # as instruções fixas de cada função reaproveitadas entre pedidos (cache_prompt)
    p1 = INSTR["interceptador"] + "\n" + EDITAL + "\nJSON:"
    p2 = INSTR["interceptador"] + "\n" + EDITAL.replace("07/2026", "08/2026").replace("Cultura", "Assistência Social") + "\nJSON:"
    sem = pedir(9001, p2, 50, cache=False)
    pedir(9001, p1, 10, cache=True); com = pedir(9001, p2, 50, cache=True)
    notice("reaproveitamento do contexto", f"sem: {sem[0]} s (leu {sem[2]} tokens) · com: {com[0]} s (leu {com[2]} tokens novos)")
elif modo == "especulativa":
    r = pedir(9001, *TAREFAS["comandante"])
    notice(f"geração ({sys.argv[2]})", f"Comandante {r[0]} s · gera {r[1]} tok/s")
