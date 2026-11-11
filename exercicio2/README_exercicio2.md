# Exercício 2 - Servidor Echo (UDP)

Servidor UDP que devolve (eco) cada mensagem recebida e cliente que envia mensagens e exibe o eco, até o usuário digitar `sair`.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Requisitos

- Python 3.10 ou superior
- Linux
- Nenhuma dependência externa (apenas biblioteca padrão)

## Como executar

Abra um terminal dentro do diretório `exercicio2/`.

### 1. Servidor

```bash
python3 servidor_udp.py --port 6000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço em que o servidor escuta | `0.0.0.0` |
| `--port`  | Porta de escuta (1-65535) | `6000` |

### 2. Cliente (em outro terminal)

```bash
python3 cliente_udp.py --host 127.0.0.1 --port 6000 --timeout 3
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço do servidor | `127.0.0.1` |
| `--port`  | Porta do servidor | `6000` |
| `--timeout` | Tempo limite de resposta, em segundos | `3` |
| `--teste-tamanho N` | Envia uma mensagem de N bytes e encerra (teste do limite) | desativado |

Digite uma mensagem e pressione Enter. Digite `sair` para encerrar.

## Testando o limite de tamanho (65.507 bytes)

O payload máximo de um datagrama UDP sobre IPv4 é 65.535 - 20 (cabeçalho IP) - 8 (cabeçalho UDP) = **65.507 bytes**. O cliente mede o tamanho em bytes (UTF-8) e recusa o envio de mensagens maiores. Como o terminal limita o tamanho do que se digita, use a opção `--teste-tamanho`:

```bash
python3 cliente_udp.py --teste-tamanho 65507   # aceito, eco retornado
python3 cliente_udp.py --teste-tamanho 65508   # recusado pelo cliente
```

## Testando o tempo limite

Com o servidor parado, rode o cliente e envie uma mensagem. Como o UDP não tem conexão, o cliente não sabe que o servidor está fora do ar e só avisa depois do `--timeout`: "Tempo esgotado".

## Exemplo de saída

Servidor:

```
[11/11/2026 09:40:12] Servidor UDP ouvindo em 0.0.0.0:6000 (Ctrl+C para encerrar)
[11/11/2026 09:40:20] [127.0.0.1:48211] (11 bytes) Mensagem: olá servidor
```

Cliente:

```
Cliente UDP para 127.0.0.1:6000 (timeout 3.0s). Digite 'sair' para encerrar.
> olá servidor
Eco (12 bytes, íntegro): olá servidor
> sair
Encerrando cliente...
Socket fechado.
```

## Funcionalidades

- Servidor imprime data/hora, IP:porta do remetente, tamanho e conteúdo de cada mensagem.
- Validação de mensagens vazias e do tamanho máximo (65.507 bytes) no cliente.
- Tempo limite de resposta com `socket.settimeout()`.
- Verificação de integridade do eco e descarte de datagramas de outras origens.
- Tratamento de erros de comunicação, endereço inválido e interrupção pelo usuário.
- Fechamento seguro do socket (`with` no servidor, `try/finally` no cliente).
