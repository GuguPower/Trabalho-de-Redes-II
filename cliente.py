#!/usr/bin/env python3
"""
Exercício 1 - Cliente TCP.

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    python3 cliente.py [--host HOST] [--port PORTA]
Digite "sair" para encerrar.
"""

import argparse
import socket

TAMANHO_BUFFER = 4096  # bytes lidos por chamada a recv()


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente TCP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--port", type=porta_valida, default=5000,
                        help="porta do servidor (padrão: 5000)")
    args = parser.parse_args()

    sock = None
    try:
        sock = socket.create_connection((args.host, args.port), timeout=5)
        sock.settimeout(None)  # remove o timeout após conectar
        print(f"Conectado a {args.host}:{args.port}. Digite 'sair' para encerrar.")

        while True:
            mensagem = input("> ").strip()

            # Validação de mensagem vazia
            if not mensagem:
                print("Mensagem vazia não é permitida. Tente novamente.")
                continue

            if mensagem.lower() == "sair":
                print("Encerrando conexão...")
                break

            sock.sendall(mensagem.encode("utf-8"))
            resposta = sock.recv(TAMANHO_BUFFER)
            if not resposta:  # servidor fechou a conexão
                print("O servidor encerrou a conexão.")
                break
            print(f"Servidor: {resposta.decode('utf-8', errors='replace')}")

    except ConnectionRefusedError:
        print(f"Conexão recusada: servidor indisponível em {args.host}:{args.port}.")
    except socket.timeout:
        print(f"Tempo esgotado ao conectar em {args.host}:{args.port}.")
    except socket.gaierror:
        print(f"Endereço inválido ou não resolvido: '{args.host}'.")
    except (ConnectionResetError, BrokenPipeError):
        print("Conexão perdida com o servidor.")
    except (KeyboardInterrupt, EOFError):
        print("\nInterrompido pelo usuário.")
    except OSError as erro:
        print(f"Erro de rede: {erro}")
    finally:
        # Garante o fechamento do socket em qualquer cenário
        if sock is not None:
            sock.close()
            print("Conexão encerrada.")


if __name__ == "__main__":
    main()
