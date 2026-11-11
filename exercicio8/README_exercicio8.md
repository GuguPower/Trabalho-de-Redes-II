# Exercício 8 - Tráfego ICMP (ping)

Análise, com o Wireshark, do tráfego ICMP gerado pelo comando `ping` para um computador da rede local (o roteador, `192.168.15.1`), identificando o tempo de ida e volta (RTT) de cada pacote.

**Participante:** Gustavo Henrique Ferreira de Oliveira

## Arquivos deste diretório

| Arquivo | Descrição |
|---------|-----------|
| `exercicio8.pcapng` | Captura do Wireshark com os pacotes ICMP |
| `README.md` | Este arquivo |

> Se os arquivos tiverem outros nomes, ajuste a tabela acima e a imagem abaixo.

## Como reproduzir

1. Abrir o Wireshark e iniciar a captura na interface de rede em uso.
2. Executar o ping para um computador da rede (neste caso, o roteador):
   ```bash
   ping 192.168.15.1
   ```
3. Parar a captura e aplicar o filtro `icmp` na barra de filtros.
4. Em cada pacote `Echo (ping) reply`, expandir **Internet Control Message Protocol** e ler o campo `[Response time]`, que é o RTT. Para ver todos de uma vez, usar **Apply as Column** nesse campo.
5. Salvar a captura em formato `.pcapng`.

## O que foi observado

Foram capturados 50 pares de pacotes ICMP entre 192.168.15.17 e o roteador 192.168.15.1, enviados a cada cerca de 1 segundo (seq 1 a 50, id 0x03e8). Cada Echo request (tipo 8) recebeu um Echo reply (tipo 0), sem perda de pacotes. O RTT, obtido pela diferença entre os instantes do request e do reply (campo Response time do Wireshark), variou de 2,04 ms a 44,28 ms, com média de 9,86 ms e mediana de 7,82 ms. A maior parte dos pacotes ficou abaixo de 20 ms, com alguns picos ocasionais, comuns em redes locais por variação de carga.

## Resumo dos RTTs

| Medida | Valor |
|--------|-------|
| Pares requisição/resposta | 50 (seq 1 a 50) |
| Pacotes sem resposta | 0 |
| RTT mínimo | 2,04 ms (seq 39, quadros 650 → 651) |
| RTT máximo | 44,28 ms (seq 45, quadros 676 → 677) |
| RTT médio | 9,86 ms |
| Mediana | 7,82 ms |
| Desvio padrão | 8,66 ms |
| Pings acima de 20 ms | 6 (seq 5, 13, 15, 19, 40 e 45) |
