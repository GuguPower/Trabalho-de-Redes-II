# Exercício 5 - Análise de Tráfego HTTP

Análise de uma comunicação HTTP utilizando o Wireshark, identificando a requisição enviada pelo cliente e a resposta recebida do servidor, incluindo o método HTTP, o código de status e os cabeçalhos da resposta.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Arquivos deste diretório

| Arquivo | Descrição |
| ------------------- | ---------------------------------------- |
| `exercicio.pcapng` | Captura do Wireshark com os pacotes HTTP |
| `README.md` | Este arquivo |


## Como reproduzir

1. Abrir o Wireshark e iniciar a captura na interface de rede em uso.
2. Acessar a página HTTP utilizada no teste para gerar tráfego.
3. Parar a captura e aplicar o filtro `http` na barra de filtros.
4. Localizar a requisição HTTP enviada pelo cliente e a resposta correspondente do servidor.
5. Expandir os detalhes dos pacotes para visualizar o método, o código de status e os cabeçalhos HTTP.
6. Salvar a captura em formato `.pcapng`.

## O que foi observado

Foi identificada uma requisição HTTP do tipo GET, enviada pelo cliente `192.168.15.17` ao servidor `104.21.4.210`, solicitando o recurso `/`. O servidor respondeu com o código `200 OK`, indicando sucesso na requisição. A resposta apresentou o tipo de conteúdo `text/html` e o servidor foi identificado como `cloudflare`.

## Resumo da comunicação HTTP

| Informação | Valor |
| ------------------- | ------------------- |
| Método HTTP | `GET` |
| Recurso solicitado | `/` |
| IP de origem | `192.168.15.17` |
| IP de destino | `104.21.4.210` |
| Código de status | `200 OK` |
| Content-Type | `text/html` |
| Server | `cloudflare` |

