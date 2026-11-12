# Exercício 10 - Chat em Rede com WebSockets

Chat em tempo real com WebSockets: um servidor assíncrono (`asyncio` + biblioteca `websockets`) aceita vários clientes simultâneos e retransmite (broadcast) cada mensagem aos demais, identificada pelo nome de usuário. Há dois clientes à escolha: um em Python e outro em HTML/JavaScript (WebSocket API nativa do navegador).

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Requisitos

- Python 3.10 ou superior
- Linux
- Biblioteca `websockets`
- Navegador atual (apenas para o cliente HTML)

## Instalação

```bash
pip install websockets
```

Em distribuições recentes (Ubuntu 23.04+, incluindo o WSL) o `pip` pode recusar a instalação global com o erro `externally-managed-environment`. Nesse caso, use um ambiente virtual dentro de `exercicio10/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install websockets
```

Se o comando `python3 -m venv` falhar, instale o pacote com `sudo apt install python3-venv`.

## Como executar

Abra um terminal dentro do diretório `exercicio10/` (com o ambiente virtual ativado, se o criou).

### 1. Servidor

```bash
python3 servidor_ws.py --port 8765
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço em que o servidor escuta | `0.0.0.0` |
| `--port`  | Porta de escuta (1-65535) | `8765` |

### 2a. Cliente em Python (um terminal para cada usuário)

```bash
python3 cliente_ws.py --host 127.0.0.1 --port 8765
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço do servidor | `127.0.0.1` |
| `--port`  | Porta do servidor | `8765` |

Informe um nome de usuário e converse. Digite `sair` para encerrar apenas o seu cliente.

### 2b. Cliente em HTML

Abra o arquivo `cliente_ws.html` no navegador (duplo clique, ou `xdg-open cliente_ws.html` no Linux). Confirme o campo do servidor (padrão `localhost:8765`), informe o nome e clique em **Entrar**. Abra o arquivo em outras abas para simular mais usuários. Se o servidor estiver no WSL e o navegador no Windows, `localhost:8765` normalmente funciona.

Os dois tipos de cliente conversam entre si na mesma sala.

## Protocolo

Mensagens JSON em texto:

| Sentido | Mensagem | Função |
|---------|----------|--------|
| Cliente → servidor | `{"tipo": "entrar", "nome": "ana"}` | Primeira mensagem; informa o nome |
| Cliente → servidor | `{"tipo": "mensagem", "texto": "olá"}` | Mensagem de chat |
| Servidor → cliente | `{"tipo": "ok"}` | Nome aceito |
| Servidor → cliente | `{"tipo": "erro", "texto": "..."}` | Nome inválido ou repetido, mensagem vazia ou longa |
| Servidor → cliente | `{"tipo": "sistema", "texto": "..."}` | Entrada e saída de usuários |
| Servidor → cliente | `{"tipo": "mensagem", "nome": "ana", "texto": "olá", "hora": "10:30:00"}` | Mensagem retransmitida |

## Regras do nome de usuário

- De 1 a 20 caracteres: letras, números, `_`, `.` e `-` (sem espaços).
- Não pode repetir um nome já em uso (sem diferenciar maiúsculas de minúsculas).

## Funcionalidades

- Servidor com `websockets` e `asyncio`, várias conexões simultâneas.
- Broadcast das mensagens a todos os demais clientes, com o nome do remetente.
- Aviso aos demais quando um usuário entra ou sai.
- Desconexões inesperadas tratadas sem derrubar o servidor: a falha de envio a um cliente não afeta os outros, e a limpeza ocorre sempre em `finally`.
- Validação do nome, de mensagens vazias, de mensagens acima de 500 caracteres, de JSON inválido e do tamanho máximo do frame (16 KB).
- Cliente Python com recebimento e envio em paralelo (tarefas `asyncio`, teclado lido em thread separada).
- Cliente HTML com a WebSocket API nativa e exibição segura do texto (`textContent`).
- Tratamento de conexão recusada, tempo esgotado, falha de handshake e queda do servidor no cliente.
