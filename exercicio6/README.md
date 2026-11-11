# Exercício 6 – Estabelecimento e Encerramento de Conexão TCP

**Participante**: Gustavo Henrique Ferreira de Oliveira

## 1. Objetivo

Analisar o processo de estabelecimento e encerramento de uma conexão TCP, identificando os pacotes responsáveis pelo three-way handshake e pela finalização da comunicação entre cliente e servidor.

## 2. Procedimentos realizados

Foi iniciada uma captura de tráfego utilizando o Wireshark. Em seguida, por meio do terminal WSL, foi estabelecida uma conexão com o servidor `example.com`, utilizando Telnet na porta 80. Após o estabelecimento da conexão, foi enviada uma requisição HTTP GET para solicitar a página inicial do servidor.

## 3. Estabelecimento da conexão TCP

O estabelecimento da conexão foi identificado por meio do three-way handshake, composto por três pacotes:

| Número do pacote | Flag TCP | Descrição |
|---|---|---|
| 605 | SYN | Cliente solicita o estabelecimento da conexão. |
| 606 | SYN, ACK | Servidor confirma o recebimento da solicitação. |
| 607 | ACK | Cliente confirma a resposta do servidor. |

Essa sequência demonstra que a conexão TCP foi estabelecida com sucesso entre o cliente (`192.168.15.17`) e o servidor (`172.66.147.243`).

## 4. Encerramento da conexão TCP

O encerramento da conexão foi identificado nos pacotes 777 a 781, por meio das flags FIN e ACK. O servidor iniciou o encerramento enviando um pacote FIN, ACK, que foi confirmado pelo cliente. Em seguida, o cliente também enviou um FIN, ACK, recebendo a confirmação final do servidor.

| Número do pacote | Flag TCP | Descrição |
|---|---|---|
| 777 | FIN, ACK | Servidor inicia o encerramento da conexão. |
| 778 | ACK | Cliente confirma o recebimento. |
| 780 | FIN, ACK | Cliente inicia o encerramento da sua parte. |
| 781 | ACK | Servidor confirma o encerramento. |

O pacote 779 também apresenta uma confirmação ACK adicional durante esse processo.

## 5. Observações

Durante a captura, também foi identificado um pacote RST, ACK (pacote 551), indicando uma tentativa anterior de encerramento abrupto de conexão. Entretanto, a sequência principal analisada demonstra o encerramento normal por meio de FIN e ACK.

## 6. Arquivo

- `exercicio6.pcapng`: arquivo contendo a captura do tráfego de rede.
