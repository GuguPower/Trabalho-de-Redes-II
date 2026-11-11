#!/usr/bin/env python3
"""
Exercício 2 - Servidor Echo UDP.

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    python3 servidor_udp.py [--host HOST] [--port PORTA]
"""

import argparse
import socket
from datetime import datetime

# Payload máximo teórico de um datagrama UDP sobre IPv4:
# 65535 (tamanho máximo do pacote IP) - 20 (cabeçalho IP) - 8 (cabeçalho UDP)
MAX_UDP_PAYLOAD = 65507

# Buffer de recepção: um pouco maior que o máximo para detectar excessos
TAMANHO_BUFFER = 65535


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


def resumo(texto: str, limite: int = 200) -> str:
    """Encurta textos muito longos para não poluir o console."""
    if len(texto) <= limite:
        return texto
    return f"{texto[:limite]}... [{len(texto)} caracteres]"


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor Echo UDP")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço de escuta (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=porta_valida, default=6000,
                        help="porta de escuta (padrão: 6000)")
    args = parser.parse_args()

    try:
        # SOCK_DGRAM = UDP (sem conexão: cada datagrama é independente)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor:
            servidor.bind((args.host, args.port))
            print(f"[{timestamp()}] Servidor UDP ouvindo em {args.host}:{args.port} "
                  "(Ctrl+C para encerrar)")

            while True:
                try:
                    dados, remetente = servidor.recvfrom(TAMANHO_BUFFER)
                except ConnectionResetError:
                    # Ocorre no Windows quando um cliente some; ignora e continua
                    continue

                ip, porta = remetente
                texto = dados.decode("utf-8", errors="replace")
                print(f"[{timestamp()}] [{ip}:{porta}] ({len(dados)} bytes) "
                      f"Mensagem: {resumo(texto)}")

                try:
                    # Eco: devolve exatamente os mesmos bytes ao remetente
                    servidor.sendto(dados, remetente)
                except OSError as erro:
                    print(f"[{timestamp()}] [{ip}:{porta}] Erro ao enviar eco: {erro}")
    except OSError as erro:
        print(f"Erro ao iniciar o servidor em {args.host}:{args.port}: {erro}")
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] Servidor encerrado.")


if __name__ == "__main__":
    main()
