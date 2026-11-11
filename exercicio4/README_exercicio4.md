# Exercício 4 - Servidor de Hora com Threads (TCP)

Servidor TCP multithread que informa a hora atual (`HH:MM:SS`) a vários clientes ao mesmo tempo e mantém um contador thread-safe (`threading.Lock`) de clientes atendidos, exibido em todas as linhas de log.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Requisitos

- Python 3.10 ou superior
- Linux
- Nenhuma dependência externa (apenas biblioteca padrão)

## Como executar

Abra um terminal dentro do diretório `exercicio4/`.

### 1. Servidor

```bash
python3 servidor_hora.py --port 7000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço em que o servidor escuta | `0.0.0.0` |
| `--port`  | Porta de escuta (1-65535) | `7000` |
| `--atraso` | Atraso artificial (segundos) antes de responder, para evidenciar a concorrência | `0` |

> Se a porta 7000 estiver em uso (por exemplo, pelo servidor de chat do exercício 3), use outra, como `--port 7100`, no servidor e no cliente.

### 2. Cliente (em outro terminal)

```bash
python3 cliente_hora.py --host 127.0.0.1 --port 7000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço do servidor | `127.0.0.1` |
| `--port`  | Porta do servidor | `7000` |
| `--quantidade N` | Dispara N clientes simultâneos (1-100), para testar a concorrência | `1` |

## Testando a concorrência

Inicie o servidor com um atraso de 2 segundos e dispare 5 clientes ao mesmo tempo:

```bash
python3 servidor_hora.py --port 7000 --atraso 2
python3 cliente_hora.py --port 7000 --quantidade 5
```

Se o servidor atendesse um cliente por vez, o total seria de cerca de 10 segundos. Com threads, os 5 clientes recebem a resposta em cerca de 2 segundos, e o contador chega a 5 sem perder nenhuma contagem.

## Exemplo de saída

Servidor:

```
[11/11/2026 10:40:12] Servidor de hora ouvindo em 0.0.0.0:7000 (Ctrl+C para encerrar)
[11/11/2026 10:40:20] [127.0.0.1:50122] [atendidos: 0] Solicitação recebida: 'HORA'
[11/11/2026 10:40:20] [127.0.0.1:50122] [atendidos: 1] Solicitação atendida: hora 10:40:20 enviada (cliente nº 1).
```

Cliente:

```
Hora do servidor: 10:40:20
```

## Protocolo

- Cliente envia `HORA\n`; o servidor responde `HH:MM:SS\n` e encerra a conexão.
- Qualquer outro comando recebe `ERRO ...`.

## Funcionalidades

- Uma thread por cliente no servidor.
- Contador de clientes atendidos protegido por `threading.Lock` (classe `ContadorSeguro`).
- Logs com data/hora, `IP:porta` do cliente e valor do contador, para cada solicitação recebida e atendida.
- O servidor continua ativo mesmo se um cliente falhar (timeout de 10 s para clientes mudos, tratamento de queda abrupta e captura de erros inesperados por thread).
- Lock também nos logs, para que linhas de threads diferentes não se misturem no console.
- Cliente com tratamento de conexão recusada, timeout, endereço inválido e queda de conexão.
- Argumentos de linha de comando validados (porta, atraso e quantidade).
