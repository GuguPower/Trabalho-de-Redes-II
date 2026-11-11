#!/usr/bin/env python3
"""
Exercício 4 - Cliente do servidor de hora TCP.

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    python3 cliente_hora.py [--host HOST] [--port PORTA]
    python3 cliente_hora.py --quantidade 5      (5 clientes simultâneos, para testar)
"""

import argparse
import re
import socket
import threading

TIMEOUT = 5                                # segundos para conectar e para receber a resposta
PADRAO_HORA = re.compile(r"^\d{2}:\d{2}:\d{2}$")  # formato esperado: HH:MM:SS


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def quantidade_valida(valor: str) -> int:
    """Valida o argumento --quantidade (inteiro de 1 a 100)."""
    try:
        n = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"quantidade inválida: '{valor}'")
    if not 1 <= n <= 100:
        raise argparse.ArgumentTypeError("a quantidade deve estar entre 1 e 100")
    return n


def solicitar_hora(host: str, porta: int, rotulo: str = "") -> None:
    """
    Conecta ao servidor, solicita a hora e exibe a resposta no console.
    'rotulo' identifica o cliente quando vários rodam em paralelo.
    """
    prefixo = f"{rotulo} " if rotulo else ""
    try:
        # 'with' garante o fechamento do socket em qualquer cenário
        with socket.create_connection((host, porta), timeout=TIMEOUT) as sock:
            sock.sendall(b"HORA\n")
            resposta = sock.recv(1024).decode("utf-8", errors="replace").strip()

        if not resposta:
            print(f"{prefixo}O servidor encerrou a conexão sem responder.")
        elif PADRAO_HORA.match(resposta):
            print(f"{prefixo}Hora do servidor: {resposta}")
        else:
            # Qualquer outra resposta (ex.: mensagem de erro do servidor)
            print(f"{prefixo}Resposta inesperada do servidor: {resposta}")
    except ConnectionRefusedError:
        print(f"{prefixo}Conexão recusada: servidor indisponível em {host}:{porta}.")
    except socket.timeout:
        print(f"{prefixo}Tempo esgotado: o servidor não respondeu em {TIMEOUT}s.")
    except socket.gaierror:
        print(f"{prefixo}Endereço inválido ou não resolvido: '{host}'.")
    except (ConnectionResetError, BrokenPipeError):
        print(f"{prefixo}Conexão perdida com o servidor.")
    except OSError as erro:
        print(f"{prefixo}Erro de rede: {erro}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente do servidor de hora TCP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--port", type=porta_valida, default=7000,
                        help="porta do servidor (padrão: 7000)")
    parser.add_argument("--quantidade", type=quantidade_valida, default=1,
                        help="número de clientes simultâneos a disparar, "
                             "para testar a concorrência (padrão: 1)")
    args = parser.parse_args()

    try:
        if args.quantidade == 1:
            solicitar_hora(args.host, args.port)
            return

        # Vários clientes ao mesmo tempo: uma thread por solicitação
        threads = [
            threading.Thread(target=solicitar_hora,
                             args=(args.host, args.port, f"[cliente {i}]"))
            for i in range(1, args.quantidade + 1)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")


if __name__ == "__main__":
    main()
