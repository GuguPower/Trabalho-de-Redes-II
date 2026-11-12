#!/usr/bin/env python3
"""
Exercício 10 - Cliente de chat com WebSockets em Python (biblioteca 'websockets').

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Uso:
    pip install websockets
    python3 cliente_ws.py [--host HOST] [--port PORTA]
Digite "sair" para encerrar.

Uma tarefa assíncrona recebe mensagens continuamente enquanto outra envia o que
o usuário digita; o teclado é lido em uma thread à parte para não travar o asyncio.
"""

import argparse
import asyncio
import json
import threading

import websockets
from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidURI

MAX_MENSAGEM = 500   # tamanho máximo de uma mensagem, em caracteres
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


def ler_teclado(loop: asyncio.AbstractEventLoop, fila: asyncio.Queue) -> None:
    """
    Thread que lê linhas do teclado e as entrega ao asyncio por uma fila.
    Envia None ao fim da entrada (Ctrl+D). É daemon, então não impede o encerramento.
    """
    while True:
        try:
            linha = input()
        except EOFError:
            linha = None
        loop.call_soon_threadsafe(fila.put_nowait, linha)
        if linha is None:
            break


def formatar(dados: dict) -> str | None:
    """Converte uma mensagem JSON do servidor em texto para exibição."""
    tipo = dados.get("tipo")
    if tipo == "mensagem":
        return f"[{dados.get('hora', '')}] {dados.get('nome', '?')}: {dados.get('texto', '')}"
    if tipo == "sistema":
        return f"*** {dados.get('texto', '')} ***"
    if tipo == "erro":
        return f"[erro] {dados.get('texto', '')}"
    return None


async def escolher_nome(websocket, fila: asyncio.Queue) -> bool:
    """Pede o nome de usuário e o envia ao servidor, repetindo até ser aceito."""
    while True:
        print("Digite seu nome de usuário: ", end="", flush=True)
        nome = await fila.get()
        if nome is None:
            return False
        nome = nome.strip()
        if not nome:
            print("O nome não pode ser vazio.")
            continue

        await websocket.send(json.dumps({"tipo": "entrar", "nome": nome}))
        resposta = json.loads(await websocket.recv())
        if resposta.get("tipo") == "ok":
            return True
        print(resposta.get("texto", "Nome recusado pelo servidor."))


async def receber(websocket) -> None:
    """Exibe continuamente as mensagens recebidas; termina quando a conexão cai."""
    try:
        async for bruto in websocket:
            try:
                texto = formatar(json.loads(bruto))
            except ValueError:
                continue  # ignora mensagens fora do protocolo
            if texto:
                # '\r' + reimpressão do prompt evita bagunçar o que o usuário digita
                print(f"\r{texto}\n{PROMPT}", end="", flush=True)
    except ConnectionClosed:
        pass


async def enviar(websocket, fila: asyncio.Queue) -> None:
    """Lê o que o usuário digita e envia ao servidor; termina com 'sair'."""
    print(PROMPT, end="", flush=True)
    while True:
        linha = await fila.get()
        if linha is None:  # entrada encerrada (Ctrl+D)
            return
        mensagem = linha.strip()

        if not mensagem:  # validação de mensagem vazia
            print("Mensagem vazia não é permitida.")
            print(PROMPT, end="", flush=True)
            continue
        if mensagem.lower() == "sair":
            return
        if len(mensagem) > MAX_MENSAGEM:
            print(f"Mensagem muito longa ({len(mensagem)} caracteres). "
                  f"O máximo é {MAX_MENSAGEM}.")
            print(PROMPT, end="", flush=True)
            continue

        await websocket.send(json.dumps({"tipo": "mensagem", "texto": mensagem}))
        print(PROMPT, end="", flush=True)


async def main(host: str, porta: int) -> None:
    """Conecta ao servidor, escolhe o nome e executa envio e recebimento em paralelo."""
    uri = f"ws://{host}:{porta}"
    loop = asyncio.get_running_loop()
    fila: asyncio.Queue = asyncio.Queue()
    threading.Thread(target=ler_teclado, args=(loop, fila), daemon=True).start()

    # 'async with' fecha a conexão em qualquer cenário
    async with websockets.connect(uri, open_timeout=5) as websocket:
        if not await escolher_nome(websocket, fila):
            return

        tarefa_receber = asyncio.create_task(receber(websocket))
        tarefa_enviar = asyncio.create_task(enviar(websocket, fila))
        await asyncio.wait({tarefa_receber, tarefa_enviar},
                           return_when=asyncio.FIRST_COMPLETED)

        if tarefa_receber.done() and not tarefa_enviar.done():
            print("\n[Conexão encerrada pelo servidor.]")
        for tarefa in (tarefa_receber, tarefa_enviar):
            tarefa.cancel()
        print("Encerrando conexão...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente de chat com WebSockets")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--port", type=porta_valida, default=8765,
                        help="porta do servidor (padrão: 8765)")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port))
    except ConnectionRefusedError:
        print(f"Conexão recusada: servidor indisponível em {args.host}:{args.port}.")
    except (asyncio.TimeoutError, TimeoutError):
        print(f"Tempo esgotado ao conectar em {args.host}:{args.port}.")
    except (InvalidURI, InvalidHandshake) as erro:
        print(f"Não foi possível estabelecer a conexão WebSocket: {erro}")
    except ConnectionClosed:
        print("Conexão perdida com o servidor.")
    except OSError as erro:
        print(f"Erro de rede: {erro}")
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
