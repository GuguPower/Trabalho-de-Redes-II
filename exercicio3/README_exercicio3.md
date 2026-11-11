# Exercício 3 - Chat em Rede (TCP)

Sistema de chat em tempo real: um servidor central aceita vários clientes (uma thread por cliente) e retransmite (broadcast) cada mensagem aos demais, precedida do nome do remetente. Cada cliente usa uma thread para ler mensagens e outra (a principal) para enviar.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Requisitos

- Python 3.10 ou superior
- Linux
- Nenhuma dependência externa (apenas biblioteca padrão)

## Como executar

Abra um terminal dentro do diretório `exercicio3/`.

### 1. Servidor

```bash
python3 servidor_chat.py --port 7000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço em que o servidor escuta | `0.0.0.0` |
| `--port`  | Porta de escuta (1-65535) | `7000` |

### 2. Clientes (um terminal para cada usuário)

```bash
python3 cliente_chat.py --host 127.0.0.1 --port 7000
```

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--host`  | Endereço do servidor | `127.0.0.1` |
| `--port`  | Porta do servidor | `7000` |

Ao conectar, informe um nome de usuário e comece a conversar. Digite `sair` para encerrar apenas o seu cliente.

## Exemplo de uso

Terminal da Ana:

```
Digite seu nome de usuário: ana
Bem-vindo, ana! Há 1 usuário(s) online. Digite 'sair' para encerrar.
> *** bruno entrou no chat ***
> oi, bruno!
> bruno: olá, ana!
> *** bruno saiu do chat ***
```

## Regras do nome de usuário

- De 1 a 20 caracteres: letras, números, `_`, `.` e `-` (sem espaços).
- Não pode repetir um nome já em uso (sem diferenciar maiúsculas de minúsculas). Se for recusado, o cliente pede outro.

## Funcionalidades

- Vários clientes simultâneos, uma thread por conexão no servidor.
- Broadcast das mensagens a todos os outros clientes, com o nome do remetente.
- Aviso aos demais quando um usuário entra ou sai da sala.
- Cliente com duas threads: leitura contínua do socket e envio pelo teclado, em paralelo.
- Comando `sair` encerra só aquele cliente, sem derrubar o servidor nem os outros.
- Mensagens delimitadas por `\n` (evita problemas de fragmentação do TCP).
- Validação de mensagens vazias, de mensagens acima de 500 caracteres e do nome de usuário.
- Acesso à lista de clientes protegido por `threading.Lock`.
- Tratamento de conexão recusada, timeout de conexão, endereço inválido, queda do servidor e quedas abruptas de clientes.
- Encerramento seguro dos sockets (`with` no servidor, `try/finally` no cliente).
