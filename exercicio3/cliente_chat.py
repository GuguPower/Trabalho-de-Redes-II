#!/usr/bin/env python3
"""
Exercício 3 - Cliente de chat TCP.

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    python3 cliente_chat.py [--host HOST] [--port PORTA]
Digite "sair" para encerrar.

A thread principal lê o teclado e envia mensagens; uma segunda thread lê
continuamente o socket e exibe as mensagens dos outros usuários.
"""

import argparse
import socket
import threading

MAX_LINHA = 4096       # bytes lidos por linha vinda do servidor
MAX_MENSAGEM = 500     # tamanho máximo de uma mensagem, em caracteres
PROMPT = "> "


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def escolher_nick(sock: socket.socket, leitor) -> bool:
    """
    Pede o nickname ao usuário e o envia ao servidor, repetindo até ser aceito.
    Retorna True se o nickname foi aceito, False se a conexão caiu.
    """
    while True:
        nick = input("Digite seu nome de usuário: ").strip()
        if not nick:
            print("O nome não pode ser vazio.")
            continue

        sock.sendall((nick + "\n").encode("utf-8"))
        resposta = leitor.readline(MAX_LINHA)
        if not resposta:
            print("O servidor encerrou a conexão.")
            return False

        resposta = resposta.strip()
        if resposta == "OK":
            return True
        # Resposta de erro do servidor (nome inválido ou já em uso)
        print(resposta.removeprefix("ERRO").strip())


def receber(leitor, parar: threading.Event, saindo: threading.Event) -> None:
    """
    Thread de leitura: exibe continuamente as mensagens recebidas do servidor.
    Termina quando a conexão é encerrada (pelo servidor ou pelo próprio cliente).
    """
    try:
        for linha in leitor:
            # '\r' + reimpressão do prompt evita bagunçar o que o usuário digita
            print(f"\r{linha.rstrip()}\n{PROMPT}", end="", flush=True)
    except (OSError, ValueError):
        pass  # socket fechado enquanto a thread lia
    finally:
        parar.set()
        if not saindo.is_set():
            print("\n[Conexão encerrada pelo servidor. Pressione Enter para sair.]",
                  flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente de chat TCP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--port", type=porta_valida, default=7000,
                        help="porta do servidor (padrão: 7000)")
    args = parser.parse_args()

    sock = None
    parar = threading.Event()    # sinaliza que a conexão acabou
    saindo = threading.Event()   # sinaliza que o próprio usuário pediu para sair
    try:
        sock = socket.create_connection((args.host, args.port), timeout=5)
        sock.settimeout(None)  # remove o timeout após conectar
        leitor = sock.makefile("r", encoding="utf-8", errors="replace", newline="\n")

        if not escolher_nick(sock, leitor):
            return

        # Thread separada para receber mensagens enquanto o usuário digita
        thread = threading.Thread(target=receber, args=(leitor, parar, saindo),
                                  daemon=True)
        thread.start()

        while not parar.is_set():
            try:
                mensagem = input(PROMPT).strip()
            except EOFError:  # entrada encerrada (ex.: Ctrl+D)
                mensagem = "sair"

            if parar.is_set():  # servidor caiu enquanto o usuário digitava
                break

            # Validação de mensagem vazia
            if not mensagem:
                print("Mensagem vazia não é permitida.")
                continue

            if len(mensagem) > MAX_MENSAGEM:
                print(f"Mensagem muito longa ({len(mensagem)} caracteres). "
                      f"O máximo é {MAX_MENSAGEM}.")
                continue

            if mensagem.lower() == "sair":
                saindo.set()
                sock.sendall(b"sair\n")
                break

            sock.sendall((mensagem + "\n").encode("utf-8"))

    except ConnectionRefusedError:
        print(f"Conexão recusada: servidor indisponível em {args.host}:{args.port}.")
    except socket.timeout:
        print(f"Tempo esgotado ao conectar em {args.host}:{args.port}.")
    except socket.gaierror:
        print(f"Endereço inválido ou não resolvido: '{args.host}'.")
    except (ConnectionResetError, BrokenPipeError):
        print("Conexão perdida com o servidor.")
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
        saindo.set()
        try:
            if sock is not None:
                sock.sendall(b"sair\n")
        except OSError:
            pass
    except OSError as erro:
        print(f"Erro de rede: {erro}")
    finally:
        # Fecha a conexão em qualquer cenário (o servidor e os demais seguem ativos)
        if sock is not None:
            saindo.set()
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
            print("Conexão encerrada.")


if __name__ == "__main__":
    main()
