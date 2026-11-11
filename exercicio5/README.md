# Exercício 5 – Análise de Tráfego HTTP com Wireshark

**Participante:** Gustavo Henrique Ferreira de Oliveira

## 1. Objetivo

Analisar o tráfego HTTP capturado pelo Wireshark, identificando o método de requisição, a URL acessada, o código de status da resposta e os cabeçalhos HTTP.

## 2. Procedimentos realizados

Foi realizada uma captura de tráfego utilizando o Wireshark durante o acesso a uma página web. Após a captura, foi aplicado o filtro `http` para visualizar as comunicações realizadas pelo protocolo HTTP e identificar as requisições e respostas do servidor.

## 3. Análise dos pacotes

Foram identificadas requisições HTTP do tipo **GET**, utilizadas para solicitar a página inicial e arquivos complementares, como CSS e JavaScript. A resposta do servidor apresentou o código **200 OK**, indicando que a solicitação foi processada com sucesso.

Os principais campos identificados foram:

| Campo | Valor |
|---|---|
| Método HTTP | GET |
| URL acessada | `/` |
| Código de status | 200 OK |
| Content-Type | text/html |
| Server | cloudflare |

Também foram observadas respostas com código **304 Not Modified**, relacionadas ao aproveitamento de arquivos armazenados no cache do navegador.

## 4. Evidências

A captura de tela dentro do repositório apresenta os pacotes HTTP identificados e os cabeçalhos da resposta do servidor.

## 5. Arquivos

- `exercicio.pcapng`: arquivo contendo a captura do tráfego de rede.
- `captura.png`: evidência visual da análise realizada.