#!/usr/bin/env python3
"""
Exercício 2 - Cliente Echo UDP.

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    python3 cliente_udp.py [--host HOST] [--port PORTA] [--timeout SEGUNDOS]
    python3 cliente_udp.py --teste-tamanho 65507     (envia um datagrama de N bytes)
Digite "sair" para encerrar.
"""

import argparse
import socket

# Payload máximo teórico de um datagrama UDP sobre IPv4:
# 65535 (tamanho máximo do pacote IP) - 20 (cabeçalho IP) - 8 (cabeçalho UDP)
MAX_UDP_PAYLOAD = 65507

TAMANHO_BUFFER = 65535


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def timeout_valido(valor: str) -> float:
    """Valida o argumento --timeout (deve ser um número positivo)."""
    try:
        tempo = float(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"timeout inválido: '{valor}'")
    if tempo <= 0:
        raise argparse.ArgumentTypeError("o timeout deve ser maior que zero")
    return tempo


def resumo(texto: str, limite: int = 200) -> str:
    """Encurta textos muito longos para não poluir o console."""
    if len(texto) <= limite:
        return texto
    return f"{texto[:limite]}... [{len(texto)} caracteres]"


def enviar_e_receber(sock: socket.socket, destino: tuple, dados: bytes) -> None:
    """
    Envia um datagrama ao servidor e aguarda o eco.
    Valida o tamanho antes de enviar e trata timeout e erros de comunicação.
    """
    # Validação do tamanho máximo permitido pelo UDP (medido em bytes, não caracteres)
    if len(dados) > MAX_UDP_PAYLOAD:
        print(f"Mensagem muito grande: {len(dados)} bytes "
              f"(máximo permitido pelo UDP: {MAX_UDP_PAYLOAD} bytes).")
        return

    try:
        sock.sendto(dados, destino)
        while True:
            resposta, origem = sock.recvfrom(TAMANHO_BUFFER)
            # Ignora datagramas que não vieram do servidor esperado
            if origem[0] == destino[0] and origem[1] == destino[1]:
                break
        eco = resposta.decode("utf-8", errors="replace")
        status = "íntegro" if resposta == dados else "DIFERENTE do enviado"
        print(f"Eco ({len(resposta)} bytes, {status}): {resumo(eco)}")
    except socket.timeout:
        print("Tempo esgotado: o servidor não respondeu "
              "(UDP não garante entrega; o servidor pode estar fora do ar).")
    except (ConnectionRefusedError, ConnectionResetError):
        print("O servidor recusou o datagrama (porta fechada ou servidor indisponível).")
    except OSError as erro:
        print(f"Erro de comunicação: {erro}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente Echo UDP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--port", type=porta_valida, default=6000,
                        help="porta do servidor (padrão: 6000)")
    parser.add_argument("--timeout", type=timeout_valido, default=3.0,
                        help="tempo limite de resposta em segundos (padrão: 3)")
    parser.add_argument("--teste-tamanho", type=int, metavar="N",
                        help="envia uma mensagem de N bytes e encerra "
                             "(útil para testar o limite de 65507 bytes)")
    args = parser.parse_args()

    if args.teste_tamanho is not None and args.teste_tamanho <= 0:
        parser.error("--teste-tamanho deve ser maior que zero")

    try:
        destino = (socket.gethostbyname(args.host), args.port)
    except socket.gaierror:
        print(f"Endereço inválido ou não resolvido: '{args.host}'.")
        return

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(args.timeout)  # tempo limite para recvfrom()

        # Modo de teste de tamanho: envia N bytes e termina
        if args.teste_tamanho is not None:
            print(f"Enviando mensagem de {args.teste_tamanho} bytes para "
                  f"{destino[0]}:{destino[1]}...")
            enviar_e_receber(sock, destino, b"A" * args.teste_tamanho)
            return

        print(f"Cliente UDP para {destino[0]}:{destino[1]} "
              f"(timeout {args.timeout}s). Digite 'sair' para encerrar.")

        while True:
            mensagem = input("> ").strip()

            # Validação de mensagem vazia
            if not mensagem:
                print("Mensagem vazia não é permitida. Tente novamente.")
                continue

            if mensagem.lower() == "sair":
                print("Encerrando cliente...")
                break

            enviar_e_receber(sock, destino, mensagem.encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        print("\nInterrompido pelo usuário.")
    except OSError as erro:
        print(f"Erro de rede: {erro}")
    finally:
        # Garante o fechamento do socket em qualquer cenário
        if sock is not None:
            sock.close()
            print("Socket fechado.")


if __name__ == "__main__":
    main()
