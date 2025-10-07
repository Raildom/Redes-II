# Redes-II - Servidor Web Sequencial vs Concorrente

## Objetivo
Implementar e comparar um servidor web sequencial e um concorrente para avaliar vantagens e desvantagens de cada abordagem.

## Informações do Projeto
- **Matrícula**: 20239057601
- **Subnet Docker**: 76.1.0.0/16 (baseada nos últimos 4 dígitos da matrícula: 7601)
- **Cabeçalho HTTP Customizado**: X-Custom-ID com hash MD5 da matrícula + nome do aluno

## Estrutura do Projeto

```
Redes-II/
├── src/                          # Código fonte
│   ├── config.py                 # Configurações baseadas na matrícula
│   ├── sequential_server.py      # Servidor sequencial (síncrono)
│   ├── concurrent_server.py      # Servidor concorrente (threads)
│   └── client.py                 # Cliente HTTP para testes
├── docker/                       # Configuração Docker
│   ├── Dockerfile                # Imagem Ubuntu com Python
│   └── docker-compose.yml        # Orquestração dos containers
├── tests/                        # Scripts de teste
│   ├── automated_tests.py        # Testes automatizados
│   └── analyze_results.py        # Geração de gráficos e análises
├── results/                      # Resultados dos testes
│   ├── test_results.json         # Dados brutos dos testes
│   ├── performance_report.txt    # Relatório de análise
│   └── plots/                    # Gráficos gerados
├── requirements.txt              # Dependências Python
└── run_project.sh               # Script principal de execução
```

## Tecnologias Utilizadas

- **Python 3**: Desenvolvimento dos servidores e clientes
- **Sockets TCP**: Comunicação de rede de baixo nível
- **Threading**: Implementação de concorrência no servidor
- **Docker & Docker Compose**: Simulação da rede e isolamento
- **Matplotlib/Seaborn**: Geração de gráficos e análises
- **Protocolo HTTP**: Estrutura de mensagens cliente-servidor

## Funcionalidades dos Servidores

### Endpoints Implementados:
- `GET /` - Página inicial
- `GET /status` - Status do servidor
- `GET /fast` - Processamento rápido (sem delay)
- `GET /medium` - Processamento médio (0.5s delay)
- `GET /slow` - Processamento lento (2s delay)
- `POST /data` - Recebimento de dados

### Características:

**Servidor Sequencial**:
- Atende uma requisição por vez
- Fila de conexões limitada
- Menor overhead de gerenciamento
- Melhor para poucos clientes

**Servidor Concorrente**:
- Múltiplas requisições simultâneas usando threads
- Maior throughput para muitos clientes
- Overhead de criação/gerenciamento de threads
- Melhor escalabilidade

## Como Executar

### Pré-requisitos
- Docker instalado e rodando
- Docker Compose
- Sistema Linux/macOS (ou WSL no Windows)

### Execução Rápida (Tudo Automatizado)
```bash
# Torna o script executável
chmod +x run_project.sh

# Executa tudo: inicia containers, testa conectividade, 
# executa testes completos e gera análises
./run_project.sh all
```

### Execução Passo a Passo

1. **Iniciar containers**:
```bash
./run_project.sh start
```

2. **Testar conectividade**:
```bash
./run_project.sh test
```

3. **Executar testes completos** (10-15 minutos):
```bash
./run_project.sh full-test
```

4. **Gerar análises e gráficos**:
```bash
./run_project.sh analyze
```

5. **Parar containers**:
```bash
./run_project.sh stop
```

### Menu Interativo
```bash
./run_project.sh
```

### Comandos Individuais Disponíveis:
- `start` - Iniciar containers
- `test` - Testar conectividade
- `full-test` - Executar testes completos
- `analyze` - Gerar análises e gráficos
- `logs` - Mostrar logs dos containers
- `shell` - Entrar no container de teste
- `stop` - Parar containers
- `clean` - Limpar ambiente Docker
- `all` - Executar tudo

## Configuração de Rede

### IPs dos Containers:
- **Servidor Sequencial**: 76.1.0.10:8080
- **Servidor Concorrente**: 76.1.0.11:8080
- **Cliente de Teste**: 76.1.0.20

### Portas Expostas:
- **8080**: Servidor Sequencial
- **8081**: Servidor Concorrente

## Testes Realizados

### Cenários de Teste:
1. **Processamento Rápido** (`/fast`) - Sem delay
2. **Processamento Médio** (`/medium`) - 0.5s delay
3. **Processamento Lento** (`/slow`) - 2s delay

### Variações de Carga:
- 1, 5, 10, 20, 50 clientes simultâneos
- 2 requisições por cliente
- 10 iterações para cada teste (média e desvio padrão)

### Métricas Coletadas:
- Tempo de resposta médio
- Desvio padrão do tempo de resposta
- Taxa de sucesso
- Throughput (requisições/segundo)
- Número de conexões ativas
- Tempo de conexão, envio e recebimento

## Resultados e Análises

Após executar os testes, os seguintes arquivos são gerados:

### Arquivos de Resultado:
- `results/test_results.json` - Dados brutos em JSON
- `results/performance_report.txt` - Relatório textual com conclusões
- `results/plots/` - Gráficos de análise:
  - `response_time_comparison.png` - Comparação de tempo de resposta
  - `success_rate_comparison.png` - Comparação de taxa de sucesso
  - `scalability_analysis.png` - Análise de escalabilidade
  - `scenario_comparison.png` - Comparação por cenário
  - `statistical_analysis.png` - Análise estatística detalhada

### Análises Incluídas:
1. **Comparação Direta**: Sequencial vs Concorrente por cenário
2. **Escalabilidade**: Como cada servidor se comporta com mais clientes
3. **Eficiência Relativa**: Qual servidor é melhor em cada situação
4. **Variabilidade**: Consistência dos tempos de resposta
5. **Throughput**: Capacidade de processamento

## Cabeçalho HTTP Customizado

Todas as requisições incluem o cabeçalho obrigatório:
```
X-Custom-ID: [hash MD5 da matrícula + nome]
```

Valor calculado automaticamente baseado na matrícula 20239057601.

## Descobertas Esperadas

### Servidor Sequencial é Melhor Para:
- Poucos clientes simultâneos
- Processamento simples e rápido
- Recursos limitados
- Baixa latência para requisições individuais

### Servidor Concorrente é Melhor Para:
- Muitos clientes simultâneos
- Processamento que pode ser paralelizado
- Alto throughput
- Escalabilidade

## Troubleshooting

### Container não inicia:
```bash
# Verificar logs
./run_project.sh logs

# Limpar e tentar novamente
./run_project.sh clean
./run_project.sh start
```

### Erro de conectividade:
```bash
# Verificar se containers estão rodando
docker ps

# Verificar rede Docker
docker network ls
docker network inspect redes2_network
```

### Dependências Python:
```bash
# Entrar no container e verificar
./run_project.sh shell
pip3 list
```

## Estrutura de Resposta HTTP

Exemplo de resposta dos servidores:
```json
{
  "server_type": "sequential",
  "method": "GET",
  "path": "/fast",
  "timestamp": "2024-10-06T15:30:45",
  "request_count": 1,
  "custom_id_received": "abc123...",
  "custom_id_valid": true,
  "processing_time": 0.0023,
  "message": "Resposta do servidor sequencial para GET /fast"
}
```

## Implementação Técnica

### Servidor Sequencial:
- `socket.listen(1)` - Fila de apenas 1 conexão
- Processamento bloqueante
- Uma thread principal

### Servidor Concorrente:
- `socket.listen(100)` - Fila de até 100 conexões
- Thread por conexão
- Thread pool implícito via threading.Thread

### Cliente de Teste:
- Suporte a testes de carga
- Múltiplas threads para simular clientes simultâneos
- Coleta detalhada de métricas de performance

## Contribuição e Extensões

Para estender o projeto:

1. **Novos Endpoints**: Adicionar em `generate_response()` nos servidores
2. **Métricas Adicionais**: Modificar `LoadTester` em `client.py`
3. **Novos Gráficos**: Estender `analyze_results.py`
4. **Diferentes Arquiteturas**: Implementar servidor async/await ou multiprocessing

## Autor

Projeto desenvolvido para a disciplina de Redes II
- Matrícula: 20239057601
- Subnet configurada: 76.1.0.0/16