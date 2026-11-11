# Exercício 7 - Análise de Consultas DNS

Análise de consultas DNS utilizando o Wireshark, identificando as solicitações de resolução de nomes e as respostas contendo os endereços IPv4 e IPv6 associados ao domínio consultado.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Arquivos deste diretório

| Arquivo | Descrição |
| ------------------- | ---------------------------------------- |
| `exercicio7.pcapng` | Captura do Wireshark com os pacotes DNS |
| `README.md` | Este arquivo |


## Como reproduzir

1. Abrir o Wireshark e iniciar a captura na interface de rede em uso.
2. Acessar o domínio `httpforever.com` para gerar consultas DNS.
3. Parar a captura e aplicar o filtro `dns` na barra de filtros.
4. Identificar as consultas do tipo A e AAAA e suas respectivas respostas.
5. Expandir os detalhes dos pacotes para visualizar os endereços retornados pelo servidor DNS.
6. Salvar a captura em formato `.pcapng`.

## O que foi observado

Foram identificadas consultas DNS para o domínio `httpforever.com`, solicitando seus endereços IPv4 (A) e IPv6 (AAAA). As respostas apresentaram dois endereços IPv4 e dois endereços IPv6 associados ao domínio. A comunicação envolveu o cliente `192.168.15.17` e o resolvedor DNS `192.168.15.1`.

## Resumo das consultas DNS

| Pacote | Tipo de consulta | Domínio consultado |
| ------- | ---------------- | ------------------ |
| 300 | A | `httpforever.com` |
| 301 | AAAA | `httpforever.com` |

## Resumo dos endereços retornados

| Tipo | Pacotes de resposta | Endereços retornados |
| ---------------- | ------------------ | ------------------- |
| A (IPv4) | 332 e 333 | `172.67.132.115` e `104.21.4.210` |
| AAAA (IPv6) | 326 e 327 | `2606:4700:3031::6815:4d2` e `2606:4700:3036::ac43:8473` |

