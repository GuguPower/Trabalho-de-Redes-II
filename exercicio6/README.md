# Exercício 6 - Estabelecimento e Encerramento de Conexão TCP

Análise do estabelecimento e encerramento de uma conexão TCP utilizando o Wireshark, identificando o handshake de três vias e a troca de segmentos responsável pelo encerramento da comunicação.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Arquivos deste diretório

| Arquivo | Descrição |
| ------------------- | ---------------------------------------- |
| `exercicio6.pcapng` | Captura do Wireshark com os pacotes TCP |
| `README.md` | Este arquivo |


## Como reproduzir

1. Abrir o Wireshark e iniciar a captura na interface de rede em uso.
2. Executar o comando `telnet example.com 80` para estabelecer uma conexão com o servidor.
3. Após a conexão, enviar uma requisição HTTP digitando:
   
   `GET / HTTP/1.1`

   `Host: example.com`

   `Connection: close`

   Pressionar Enter duas vezes para finalizar a requisição.
4. Parar a captura e aplicar o filtro `tcp.port == 80`.
5. Identificar os pacotes responsáveis pelo estabelecimento e encerramento da conexão.
6. Salvar a captura em formato `.pcapng`.

## O que foi observado

Foi analisada uma conexão TCP entre o cliente `192.168.15.17` e o servidor `172.66.147.243`, utilizando a porta 80. O estabelecimento ocorreu por meio do handshake de três vias (SYN, SYN/ACK e ACK). No encerramento, foram identificados segmentos FIN/ACK e ACK, demonstrando a finalização da conexão TCP.

## Estabelecimento da conexão TCP

| Etapa | Pacote | Origem | Destino | Descrição |
| ------------------- | ------- | ---------------- | ---------------- | ---------------------------------------- |
| SYN | 605 | `192.168.15.17` | `172.66.147.243` | Cliente solicita o início da conexão. |
| SYN/ACK | 606 | `172.66.147.243` | `192.168.15.17` | Servidor aceita a conexão e responde. |
| ACK | 607 | `192.168.15.17` | `172.66.147.243` | Cliente confirma o recebimento. |

## Encerramento da conexão TCP

| Etapa | Pacote | Origem | Destino | Descrição |
| ------------------- | ------- | ---------------- | ---------------- | ---------------------------------------- |
| FIN/ACK | 777 | `172.66.147.243` | `192.168.15.17` | Servidor inicia o encerramento. |
| ACK | 778 | `192.168.15.17` | `172.66.147.243` | Cliente confirma o recebimento. |
| FIN/ACK | 780 | `192.168.15.17` | `172.66.147.243` | Cliente solicita o encerramento de sua direção da conexão. |
| ACK | 781 | `172.66.147.243` | `192.168.15.17` | Servidor confirma o encerramento. |

Também foi observado um pacote RST/ACK no pacote 551, referente a outra comunicação. Ele não faz parte da sequência principal de encerramento apresentada na tabela.

