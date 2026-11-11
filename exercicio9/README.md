# Exercício 9 - Tráfego DHCP

Análise, com o Wireshark, do processo de negociação DHCP, identificando as quatro mensagens do processo DORA (Discover, Offer, Request e Ack), utilizadas para a obtenção de um endereço IP na rede.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Arquivos deste diretório

| Arquivo | Descrição |
| ------------------- | ---------------------------------------- |
| `exercicio9.pcapng` | Captura do Wireshark com os pacotes DHCP |
| `README.md` | Este arquivo |


## Como reproduzir

1. Abrir o Wireshark e iniciar a captura na interface de rede em uso.
2. Desconectar e reconectar à rede para gerar uma nova negociação DHCP. Caso necessário, forçar a renovação do endereço IP pelo terminal:
   
   `sudo dhclient -r && sudo dhclient`

3. Parar a captura e aplicar o filtro `dhcp` na barra de filtros.
4. Identificar as quatro mensagens do processo DORA: Discover, Offer, Request e Ack.
5. Salvar a captura em formato `.pcapng`.

## O que foi observado

Foi capturado o processo de negociação DHCP entre o computador e o roteador, utilizando o Transaction ID `0xb38e2aba`. A negociação ocorreu em quatro etapas: o cliente enviou um DHCP Discover (pacote 153), o servidor respondeu com DHCP Offer (pacote 265), o cliente solicitou o endereço oferecido por meio de um DHCP Request (pacote 266) e o servidor confirmou a atribuição com DHCP ACK (pacote 269).

O processo demonstra que o computador conseguiu realizar uma nova negociação DHCP com sucesso. Também foram observadas mensagens DHCP Release (pacote 23), indicando a liberação de um endereço, e outra sequência de Request e ACK (pacotes 340 e 341), relacionada a uma solicitação posterior de renovação ou confirmação da configuração DHCP.

## Resumo das mensagens DORA

| Etapa | Pacote | Origem | Destino | Descrição |
| ------------------- | ------- | ---------------- | ----------------- | ---------------------------------------- |
| Discover | 153 | `0.0.0.0` | `255.255.255.255` | Cliente procura um servidor DHCP. |
| Offer | 265 | `192.168.1.1` | `255.255.255.255` | Servidor oferece uma configuração de rede. |
| Request | 266 | `0.0.0.0` | `255.255.255.255` | Cliente solicita a configuração oferecida. |
| ACK | 269 | `192.168.1.1` | `255.255.255.255` | Servidor confirma a atribuição da configuração. |

Todas as quatro mensagens principais apresentam o mesmo identificador de transação (`0xb38e2aba`), permitindo relacioná-las à mesma negociação DHCP.