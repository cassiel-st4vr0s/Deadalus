import subprocess
import time
#import os

def run_node(port):
    return subprocess.Popen(
        ["uvicorn", "app.main:app", "--reload", "--port", str(port)],
        cwd="backend", #Localização do App
    )

if __name__ == "__main__":
    ports = [8000, 8001, 8002]
    processes = []

    for port in ports:
        print(f"Iniciando nó na porta {port}...")
        p = run_node(port)
        processes.append(p)
        time.sleep(1)  # pequena pausa entre os lançamentos

    print("Todos os nós foram iniciados. Pressione Ctrl+C para encerrar.")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("Encerrando nós...")
        for p in processes:
            p.terminate()