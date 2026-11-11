#!/usr/bin/env python3
"""
Exercício 4 - Servidor de hora TCP multithread com contador thread-safe.

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Protocolo (texto, uma linha por mensagem):
    Cliente -> servidor: "HORA\\n"
    Servidor -> cliente: "HH:MM:SS\\n"   (ou "ERRO <motivo>\\n" se o comando for inválido)
    Cada conexão atende uma solicitação e é encerrada em seguida.

Uso:
    python3 servidor_hora.py [--host HOST] [--port PORTA] [--atraso SEGUNDOS]
"""

import argparse
import socket
import threading
import time
from datetime import datetime

TIMEOUT_CLIENTE = 10   # segundos que o servidor espera a solicitação de um cliente
MAX_LINHA = 1024       # bytes lidos da solicitação (proteção contra linhas gigantes)


class ContadorSeguro:
    """
    Contador de clientes atendidos, seguro para uso por várias threads.
    O Lock garante que a operação "ler + somar + guardar" seja atômica; sem ele,
    duas threads poderiam ler o mesmo valor e perder uma contagem (condição de corrida).
    """

    def __init__(self) -> None:
        self._valor = 0
        self._lock = threading.Lock()

    def incrementar(self) -> int:
        """Soma 1 ao contador e devolve o novo valor (operação atômica)."""
        with self._lock:
            self._valor += 1
            return self._valor

    def valor(self) -> int:
        """Devolve o valor atual do contador."""
        with self._lock:
            return self._valor


# Contador global compartilhado por todas as threads de atendimento
atendidos = ContadorSeguro()

# Lock para que as linhas de log de threads diferentes não se misturem no console
lock_log = threading.Lock()


def timestamp() -> str:
    """Retorna a data/hora atual formatada para os logs."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def log(origem: str, texto: str) -> None:
    """
    Registra uma linha de log com data/hora, cliente e contador de atendimentos.
    Todas as linhas incluem o valor atual do contador.
    """
    with lock_log:
        print(f"[{timestamp()}] [{origem}] [atendidos: {atendidos.valor()}] {texto}",
              flush=True)


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def atraso_valido(valor: str) -> float:
    """Valida o argumento --atraso (deve ser um número maior ou igual a zero)."""
    try:
        atraso = float(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"atraso inválido: '{valor}'")
    if atraso < 0:
        raise argparse.ArgumentTypeError("o atraso não pode ser negativo")
    return atraso


def atender_cliente(conn: socket.socket, endereco: tuple, atraso: float) -> None:
    """
    Executada em uma thread por cliente: lê a solicitação, responde com a hora
    atual e atualiza o contador. Qualquer falha fica restrita a esta thread.
    """
    origem = f"{endereco[0]}:{endereco[1]}"
    try:
        # 'with' garante o fechamento da conexão em qualquer saída
        with conn:
            conn.settimeout(TIMEOUT_CLIENTE)  # evita thread presa em cliente mudo

            dados = conn.recv(MAX_LINHA)
            if not dados:
                log(origem, "Conexão encerrada sem enviar solicitação.")
                return

            comando = dados.decode("utf-8", errors="replace").strip()
            log(origem, f"Solicitação recebida: '{comando}'")

            if comando.upper() != "HORA":
                conn.sendall(b"ERRO Comando invalido. Envie HORA\n")
                log(origem, "Solicitação inválida rejeitada.")
                return

            # Atraso opcional: simula processamento lento para evidenciar a concorrência
            if atraso > 0:
                time.sleep(atraso)

            hora = datetime.now().strftime("%H:%M:%S")
            conn.sendall((hora + "\n").encode("utf-8"))

            # Contagem feita só depois que a resposta foi enviada com sucesso
            total = atendidos.incrementar()
            log(origem, f"Solicitação atendida: hora {hora} enviada "
                        f"(cliente nº {total}).")
    except socket.timeout:
        log(origem, "Tempo esgotado aguardando a solicitação do cliente.")
    except (ConnectionResetError, BrokenPipeError):
        log(origem, "Cliente encerrou a conexão abruptamente.")
    except Exception as erro:  # noqa: BLE001 - nenhuma falha pode derrubar o servidor
        log(origem, f"Erro inesperado ao atender cliente: {erro!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de hora TCP multithread")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço de escuta (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=porta_valida, default=7000,
                        help="porta de escuta (padrão: 7000)")
    parser.add_argument("--atraso", type=atraso_valido, default=0.0,
                        help="atraso artificial em segundos antes de responder, "
                             "para demonstrar a concorrência (padrão: 0)")
    args = parser.parse_args()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            # Permite reiniciar o servidor sem esperar o TIME_WAIT da porta
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((args.host, args.port))
            servidor.listen()
            print(f"[{timestamp()}] Servidor de hora ouvindo em "
                  f"{args.host}:{args.port} (Ctrl+C para encerrar)", flush=True)

            while True:
                try:
                    conn, endereco = servidor.accept()
                except OSError as erro:
                    # Falha ao aceitar uma conexão não derruba o servidor
                    print(f"[{timestamp()}] Erro ao aceitar conexão: {erro}", flush=True)
                    continue
                # daemon=True: as threads não impedem o encerramento do programa
                threading.Thread(target=atender_cliente,
                                 args=(conn, endereco, args.atraso),
                                 daemon=True).start()
    except OSError as erro:
        print(f"Erro ao iniciar o servidor em {args.host}:{args.port}: {erro}")
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] Servidor encerrado. "
              f"Total de clientes atendidos: {atendidos.valor()}")


if __name__ == "__main__":
    main()
