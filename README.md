# Exercício 1 - Cliente e Servidor TCP

Servidor TCP que atende múltiplos clientes simultaneamente (uma thread por conexão) e cliente que envia mensagens até o usuário digitar `sair`.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Requisitos

- Python 3.10 ou superior
- Linux
- Nenhuma dependência externa (apenas biblioteca padrão)

## Como executar

Abra um terminal dentro do diretório `exercicio1/`.

### 1. Servidor

```bash
python3 servidor.py --port 5000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço em que o servidor escuta | `0.0.0.0` |
| `--port`  | Porta de escuta (1-65535) | `5000` |

### 2. Cliente (em outro terminal; abra vários para testar a concorrência)

```bash
python3 cliente.py --host 127.0.0.1 --port 5000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço do servidor | `127.0.0.1` |
| `--port`  | Porta do servidor | `5000` |

Digite uma mensagem e pressione Enter. Digite `sair` para encerrar.

## Exemplo de saída

Servidor:

```
[11/11/2026 08:40:12] Servidor ouvindo em 0.0.0.0:5000 (Ctrl+C para encerrar)
[11/11/2026 08:40:20] [127.0.0.1:51234] Cliente conectado.
[11/11/2026 08:40:25] [127.0.0.1:51234] Mensagem: olá servidor
```

Cliente:

```
Conectado a 127.0.0.1:5000. Digite 'sair' para encerrar.
> olá servidor
Servidor: Mensagem recebida
> sair
Encerrando conexão...
Conexão encerrada.
```

## Funcionalidades

- Uma thread por cliente no servidor.
- Log no servidor com data/hora e `IP:porta` do cliente.
- Validação de mensagens vazias (no cliente e no servidor).
- Encerramento seguro do socket (`with` no servidor, `try/finally` no cliente).
- Tratamento de conexão recusada (servidor indisponível), timeout, endereço inválido e queda de conexão.
- Validação do número da porta (1-65535).
