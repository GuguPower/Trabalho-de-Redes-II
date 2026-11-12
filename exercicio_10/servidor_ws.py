#!/usr/bin/env python3
"""
Exercício 10 - Servidor de chat com WebSockets (biblioteca 'websockets').

Participante:
    - Gustavo Henrique Ferreira de Oliveira

Protocolo (mensagens JSON em texto):
    Cliente -> servidor:
        {"tipo": "entrar",   "nome": "ana"}          (primeira mensagem obrigatória)
        {"tipo": "mensagem", "texto": "olá"}
    Servidor -> cliente:
        {"tipo": "ok"}                                (nome aceito)
        {"tipo": "erro",     "texto": "..."}          (nome inválido, mensagem vazia...)
        {"tipo": "sistema",  "texto": "..."}          (entrada/saída de usuários)
        {"tipo": "mensagem", "nome": "ana", "texto": "olá", "hora": "10:30:00"}

Uso:
    pip install websockets
    python3 servidor_ws.py [--host HOST] [--port PORTA]
"""

import argparse
import asyncio
import json
import re
from datetime import datetime

import websockets
from websockets.exceptions import ConnectionClosed, ConnectionClosedError

MAX_MENSAGEM = 500                              # tamanho máximo de uma mensagem, em caracteres
MAX_BYTES = 16 * 1024                           # tamanho máximo de um frame recebido
PADRAO_NOME = re.compile(r"^[\w.\-]{1,20}$")    # letras, números, _ . - (até 20)

# Clientes já identificados: conexão -> nome de usuário.
# O asyncio roda em uma única thread, então não é preciso usar Lock aqui.
clientes: dict = {}


def agora() -> str:
    """Retorna a data/hora atual formatada para os logs do servidor."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def log(texto: str) -> None:
    """Imprime uma linha de log no console do servidor."""
    print(f"[{agora()}] {texto}", flush=True)


def porta_valida(valor: str) -> int:
    """Valida o argumento --port (deve estar entre 1 e 65535)."""
    try:
        porta = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"porta inválida: '{valor}'")
    if not 1 <= porta <= 65535:
        raise argparse.ArgumentTypeError("a porta deve estar entre 1 e 65535")
    return porta


def origem_de(websocket) -> str:
    """Devolve 'IP:porta' do cliente, para uso nos logs."""
    endereco = websocket.remote_address
    if isinstance(endereco, tuple) and len(endereco) >= 2:
        return f"{endereco[0]}:{endereco[1]}"
    return "desconhecido"


def interpretar(bruto) -> dict | None:
    """Converte o texto recebido em dicionário JSON; devolve None se for inválido."""
    try:
        dados = json.loads(bruto)
    except (ValueError, TypeError):
        return None
    return dados if isinstance(dados, dict) else None


async def enviar_json(websocket, objeto: dict) -> None:
    """Envia um objeto JSON a um cliente."""
    await websocket.send(json.dumps(objeto, ensure_ascii=False))


async def enviar_seguro(websocket, texto: str) -> None:
    """Envia a um cliente ignorando falhas: um cliente com problema não afeta os demais."""
    try:
        await websocket.send(texto)
    except (ConnectionClosed, OSError):
        pass  # a tarefa desse cliente fará a limpeza ao detectar a desconexão


async def broadcast(objeto: dict, excluir=None) -> None:
    """Retransmite 'objeto' a todos os clientes conectados, exceto 'excluir'."""
    texto = json.dumps(objeto, ensure_ascii=False)
    destinos = [ws for ws in list(clientes) if ws is not excluir]
    if destinos:
        await asyncio.gather(*(enviar_seguro(ws, texto) for ws in destinos))


async def negociar_nome(websocket) -> str:
    """
    Espera a mensagem 'entrar' e valida o nome de usuário, repetindo até ser aceito.
    Levanta ConnectionClosed se o cliente desconectar antes.
    """
    while True:
        dados = interpretar(await websocket.recv())

        if dados is None or dados.get("tipo") != "entrar":
            await enviar_json(websocket, {"tipo": "erro",
                                          "texto": "Envie seu nome de usuário para entrar."})
            continue

        nome = str(dados.get("nome", "")).strip()
        if not PADRAO_NOME.match(nome):
            await enviar_json(websocket, {
                "tipo": "erro",
                "texto": "Nome inválido: use de 1 a 20 caracteres "
                         "(letras, números, _ . -), sem espaços."})
            continue

        if any(n.lower() == nome.lower() for n in clientes.values()):
            await enviar_json(websocket, {"tipo": "erro",
                                          "texto": f"O nome '{nome}' já está em uso."})
            continue

        clientes[websocket] = nome
        await enviar_json(websocket, {"tipo": "ok"})
        return nome


async def atender(websocket) -> None:
    """Tarefa executada para cada conexão: nome, mensagens e desconexão."""
    origem = origem_de(websocket)
    nome = None
    log(f"[{origem}] Conexão recebida.")

    try:
        nome = await negociar_nome(websocket)
        log(f"[{origem}] '{nome}' entrou no chat ({len(clientes)} online).")
        await enviar_json(websocket, {
            "tipo": "sistema",
            "texto": f"Bem-vindo, {nome}! Há {len(clientes)} usuário(s) online."})
        await broadcast({"tipo": "sistema", "texto": f"{nome} entrou no chat"},
                        excluir=websocket)

        async for bruto in websocket:
            dados = interpretar(bruto)
            if dados is None or dados.get("tipo") != "mensagem":
                await enviar_json(websocket, {"tipo": "erro", "texto": "Mensagem inválida."})
                continue

            texto = str(dados.get("texto", "")).strip()
            if not texto:  # validação de mensagem vazia
                await enviar_json(websocket, {"tipo": "erro",
                                              "texto": "Mensagem vazia não é permitida."})
                continue
            if len(texto) > MAX_MENSAGEM:
                await enviar_json(websocket, {
                    "tipo": "erro",
                    "texto": f"Mensagem muito longa (máximo {MAX_MENSAGEM} caracteres)."})
                continue

            log(f"[{origem}] {nome}: {texto}")
            await broadcast({"tipo": "mensagem", "nome": nome, "texto": texto,
                             "hora": datetime.now().strftime("%H:%M:%S")},
                            excluir=websocket)
    except ConnectionClosedError:
        log(f"[{origem}] Desconexão inesperada de '{nome or 'sem nome'}'.")
    except ConnectionClosed:
        pass  # encerramento normal pelo cliente
    except Exception as erro:  # noqa: BLE001 - nenhuma falha pode derrubar o servidor
        log(f"[{origem}] Erro inesperado: {erro!r}")
    finally:
        # Limpeza: remove o cliente da sala e avisa os demais
        if nome is not None:
            clientes.pop(websocket, None)
            log(f"[{origem}] '{nome}' saiu do chat ({len(clientes)} online).")
            await broadcast({"tipo": "sistema", "texto": f"{nome} saiu do chat"})
        else:
            log(f"[{origem}] Conexão encerrada sem registrar nome.")


async def main(host: str, porta: int) -> None:
    """Inicia o servidor WebSocket e o mantém ativo até ser interrompido."""
    async with websockets.serve(atender, host, porta, max_size=MAX_BYTES):
        log(f"Servidor WebSocket ouvindo em ws://{host}:{porta} (Ctrl+C para encerrar)")
        await asyncio.Future()  # roda para sempre


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de chat com WebSockets")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço de escuta (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=porta_valida, default=8765,
                        help="porta de escuta (padrão: 8765)")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port))
    except OSError as erro:
        print(f"Erro ao iniciar o servidor em {args.host}:{args.port}: {erro}")
    except KeyboardInterrupt:
        print(f"\n[{agora()}] Servidor encerrado.")
