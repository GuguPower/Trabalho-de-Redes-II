#!/usr/bin/env python3
"""
Exercício 1 - Servidor TCP multi-cliente (uma thread por conexão).

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    python3 servidor.py [--host HOST] [--port PORTA]
"""

import argparse
import socket
import threading
from datetime import datetime

TAMANHO_BUFFER = 4096  # bytes lidos por chamada a recv()


def timestamp() -> str:
    """Retorna a data/hora atual formatada para exibição no console."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def atender_cliente(conn: socket.socket, endereco: tuple) -> None:
    """
    Executada em uma thread dedicada a cada cliente.
    Recebe mensagens, imprime no console e responde com uma confirmação.
    """
    ip, porta = endereco
    origem = f"{ip}:{porta}"
    print(f"[{timestamp()}] [{origem}] Cliente conectado.")

    # 'with' garante que a conexão seja fechada ao final, mesmo com erro
    with conn:
        try:
            while True:
                dados = conn.recv(TAMANHO_BUFFER)
                if not dados:  # b"" => cliente fechou a conexão
                    break

                mensagem = dados.decode("utf-8", errors="replace").strip()

                # Validação de mensagem vazia também no servidor
                if not mensagem:
                    print(f"[{timestamp()}] [{origem}] Mensagem vazia ignorada.")
                    conn.sendall("Mensagem vazia não é permitida".encode("utf-8"))
                    continue

                print(f"[{timestamp()}] [{origem}] Mensagem: {mensagem}")
                conn.sendall("Mensagem recebida".encode("utf-8"))
        except (ConnectionResetError, BrokenPipeError):
            print(f"[{timestamp()}] [{origem}] Conexão interrompida pelo cliente.")
        except OSError as erro:
            print(f"[{timestamp()}] [{origem}] Erro de socket: {erro}")
        finally:
            print(f"[{timestamp()}] [{origem}] Cliente desconectado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor TCP multi-cliente")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço de escuta (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=porta_valida, default=5000,
                        help="porta de escuta (padrão: 5000)")
    args = parser.parse_args()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            # Permite reiniciar o servidor sem esperar o TIME_WAIT da porta
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((args.host, args.port))
            servidor.listen()
            print(f"[{timestamp()}] Servidor ouvindo em {args.host}:{args.port} "
                  "(Ctrl+C para encerrar)")

            while True:
                conn, endereco = servidor.accept()
                # daemon=True: threads não impedem o encerramento do programa
                thread = threading.Thread(target=atender_cliente,
                                          args=(conn, endereco), daemon=True)
                thread.start()
    except OSError as erro:
        print(f"Erro ao iniciar o servidor em {args.host}:{args.port}: {erro}")
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] Servidor encerrado.")


if __name__ == "__main__":
    main()
