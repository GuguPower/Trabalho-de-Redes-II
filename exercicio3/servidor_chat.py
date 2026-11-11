#!/usr/bin/env python3
"""
Exercício 3 - Servidor de chat TCP (broadcast para múltiplos clientes).

Participantes do grupo:
    - Gustavo Henrique Ferreira de Oliveira

Protocolo (texto, uma mensagem por linha terminada em '\\n'):
    1. O cliente envia o nickname desejado; o servidor responde "OK" ou "ERRO ...".
    2. Depois de aceito, cada linha enviada pelo cliente é retransmitida aos demais
       no formato "nickname: mensagem".
    3. A linha "sair" encerra a conexão daquele cliente.

Uso:
    python3 servidor_chat.py [--host HOST] [--port PORTA]
"""

import argparse
import re
import socket
import threading
from datetime import datetime

MAX_LINHA = 2048        # bytes lidos por linha (proteção contra linhas gigantes)
MAX_MENSAGEM = 500      # tamanho máximo de uma mensagem de chat, em caracteres
PADRAO_NICK = re.compile(r"^[\w.\-]{1,20}$")  # letras, números, _ . - (até 20)

# Dicionário compartilhado entre as threads: socket do cliente -> nickname.
# Sempre acessado com 'lock' para evitar condições de corrida.
clientes: dict[socket.socket, str] = {}
lock = threading.Lock()


def timestamp() -> str:
    """Retorna a data/hora atual formatada para os logs do servidor."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def log(texto: str) -> None:
    """Imprime uma linha de log no console do servidor."""
    print(f"[{timestamp()}] {texto}", flush=True)


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def enviar(conn: socket.socket, texto: str) -> None:
    """Envia uma linha de texto a um cliente (adiciona o '\\n' final)."""
    conn.sendall((texto + "\n").encode("utf-8"))


def broadcast(texto: str, excluir: socket.socket | None = None) -> None:
    """
    Retransmite 'texto' a todos os clientes conectados, exceto 'excluir'.
    O lock é mantido durante os envios para que mensagens de threads
    diferentes não se misturem no mesmo socket.
    """
    with lock:
        for conn in list(clientes):
            if conn is excluir:
                continue
            try:
                enviar(conn, texto)
            except OSError:
                # Cliente com problema: a thread dele fará a limpeza ao detectar o erro
                pass


def negociar_nick(conn: socket.socket, leitor) -> str | None:
    """
    Recebe e valida o nickname. Repete até um nome válido e único ser aceito.
    Retorna o nickname registrado ou None se o cliente desconectar antes.
    """
    while True:
        linha = leitor.readline(MAX_LINHA)
        if not linha:  # cliente fechou a conexão
            return None
        nick = linha.strip()

        if not PADRAO_NICK.match(nick):
            enviar(conn, "ERRO Nome inválido: use de 1 a 20 caracteres "
                         "(letras, números, _ . -), sem espaços.")
            continue

        # Verificação de unicidade e registro de forma atômica
        with lock:
            if any(n.lower() == nick.lower() for n in clientes.values()):
                existe = True
            else:
                existe = False
                clientes[conn] = nick
        if existe:
            enviar(conn, f"ERRO O nome '{nick}' já está em uso. Escolha outro.")
            continue

        enviar(conn, "OK")
        return nick


def atender_cliente(conn: socket.socket, endereco: tuple) -> None:
    """Executada em uma thread por cliente: nickname, mensagens e saída."""
    origem = f"{endereco[0]}:{endereco[1]}"
    nick = None
    log(f"[{origem}] Conexão recebida.")

    try:
        # 'with' garante o fechamento do socket e do leitor em qualquer saída
        with conn, conn.makefile("r", encoding="utf-8", errors="replace",
                                 newline="\n") as leitor:
            nick = negociar_nick(conn, leitor)
            if nick is None:
                return

            with lock:
                total = len(clientes)
            log(f"[{origem}] '{nick}' entrou no chat ({total} online).")
            enviar(conn, f"Bem-vindo, {nick}! Há {total} usuário(s) online. "
                         "Digite 'sair' para encerrar.")
            broadcast(f"*** {nick} entrou no chat ***", excluir=conn)

            while True:
                linha = leitor.readline(MAX_LINHA)
                if not linha:  # conexão encerrada pelo cliente
                    break
                mensagem = linha.strip()

                if not mensagem:  # ignora mensagens vazias
                    continue
                if mensagem.lower() == "sair":
                    break

                mensagem = mensagem[:MAX_MENSAGEM]
                log(f"[{origem}] {nick}: {mensagem}")
                broadcast(f"{nick}: {mensagem}", excluir=conn)
    except (ConnectionResetError, BrokenPipeError):
        pass  # queda abrupta do cliente: tratada na limpeza abaixo
    except OSError as erro:
        log(f"[{origem}] Erro de socket: {erro}")
    finally:
        # Limpeza: remove o cliente da sala e avisa os demais
        if nick is not None:
            with lock:
                clientes.pop(conn, None)
                restantes = len(clientes)
            log(f"[{origem}] '{nick}' saiu do chat ({restantes} online).")
            broadcast(f"*** {nick} saiu do chat ***")
        else:
            log(f"[{origem}] Conexão encerrada sem registrar nickname.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de chat TCP")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço de escuta (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=porta_valida, default=7000,
                        help="porta de escuta (padrão: 7000)")
    args = parser.parse_args()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            # Permite reiniciar o servidor sem esperar o TIME_WAIT da porta
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((args.host, args.port))
            servidor.listen()
            log(f"Servidor de chat ouvindo em {args.host}:{args.port} "
                "(Ctrl+C para encerrar)")

            while True:
                conn, endereco = servidor.accept()
                # daemon=True: as threads não impedem o encerramento do programa
                threading.Thread(target=atender_cliente, args=(conn, endereco),
                                 daemon=True).start()
    except OSError as erro:
        print(f"Erro ao iniciar o servidor em {args.host}:{args.port}: {erro}")
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] Servidor encerrado.")


if __name__ == "__main__":
    main()
