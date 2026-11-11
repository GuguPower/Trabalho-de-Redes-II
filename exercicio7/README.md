# Exercício 7 – Análise de Consultas DNS com Wireshark

**Participante**: Gustavo Henrique Ferreira de Oliveira

## 1. Objetivo
Analisar o processo de resolução de nomes por meio do protocolo DNS, identificando os tipos de registros solicitados, o servidor DNS utilizado e os endereços retornados nas respostas.

## 2. Procedimentos realizados
Foi realizada uma captura de tráfego utilizando o Wireshark durante o acesso ao endereço `http://httpforever.com/`. Após a captura, foi aplicado o filtro `dns` para visualizar as consultas e respostas relacionadas à resolução do domínio.

## 3. Análise dos pacotes
Foram identificadas consultas DNS dos tipos **A** e **AAAA**, utilizadas para obter, respectivamente, os endereços IPv4 e IPv6 associados ao domínio `httpforever.com`.

O servidor DNS identificado na comunicação com o computador foi `192.168.15.1`. As respostas retornaram os seguintes endereços:

| Campo | Valor |
|---|---|
| Domínio consultado | httpforever.com |
| Tipos de registros | A e AAAA |
| Servidor DNS | 192.168.15.1 |
| Endereços IPv4 | 172.67.132.115 e 104.21.4.210 |
| Endereços IPv6 | 2606:4700:3031::6815:4d2 e 2606:4700:3036::ac43:8473 |

Os pacotes 300 e 301 representam as consultas DNS, enquanto os pacotes 332 e 333 apresentam as respostas com os endereços IPv4. As respostas referentes aos endereços IPv6 podem ser observadas nos pacotes 326 e 327.

## 4. Arquivos
- `exercicio7.pcapng`: arquivo contendo a captura do tráfego de rede.
