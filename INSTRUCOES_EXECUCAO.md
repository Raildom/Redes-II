# 🎯 INSTRUÇÕES DE EXECUÇÃO E TESTES - PROJETO REDES II

## 📖 Visão Geral
Este documento contém as instruções essenciais para executar o projeto e realizar todos### 🤖 TESTES AUTOMATIZADOS

### Teste Rápido com o Novo Testador
```bash
# Executar teste completo com o arquivo dedicado
python3 testes/teste_cliente.py

# Ou executar dentro do Docker
docker exec -it cliente_teste python3 /app/testes/teste_cliente.py
```

### Testes Específicos
```bash
# Apenas conectividade
python3 testes/teste_cliente.py --conectividade

# Apenas endpoints
python3 testes/teste_cliente.py --endpoints

# Apenas validação de cabeçalho
python3 testes/teste_cliente.py --cabecalho

# Apenas concorrência
python3 testes/teste_cliente.py --concorrencia
```

### Teste Completo Automatizado (Antigo)
```bash
# Executar bateria completa de testes
echo "Iniciando testes automatizados..."
docker exec -it cliente_teste python3 /app/testes/testes_automatizados.py

# Verificar se o arquivo de resultados foi criado
docker exec -it cliente_teste ls -la /app/resultados/test_results.json
```necessários.

**Matrícula:** 20239057601  
**Aluno:** Raildom  
**Sub-rede:** 76.1.0.0/16  
**ID Personalizado:** Baseado em MD5 da matrícula + nome

---

## EXECUÇÃO RÁPIDA (Iniciantes)

### 1. Preparar e Executar
```bash
# 1. Navegar para o diretório do projeto
cd Redes-II

# 2. Iniciar containers Docker
docker-compose -f docker/docker-compose.yml up -d

# 3. Aguardar inicialização (30 segundos)
sleep 30

# 4. Verificar se os servidores estão funcionando
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" http://localhost:8080/
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" http://localhost:8081/
```

### 2. Executar Testes Automatizados
```bash
# Executar todos os testes automatizados
docker exec -it docker_cliente python3 /app/testes/testes_automatizados.py

# Gerar análises e gráficos
docker exec -it docker_cliente python3 /app/testes/analisar_resultados.py
```

### 3. Parar o Projeto
```bash
# Parar todos os containers
docker-compose -f docker/docker-compose.yml down
```

---

## 🔧 EXECUÇÃO DETALHADA

### Passo 1: Verificar Pré-requisitos
```bash
# Verificar Docker
docker --version
docker-compose --version

# Se não estiver instalado no Ubuntu/Debian:
# sudo apt update
# sudo apt install docker.io docker-compose
# sudo usermod -aG docker $USER
# logout e login novamente
```

### Passo 2: Preparar o Ambiente
```bash
# Clonar o repositório (se ainda não clonou)
git clone https://github.com/Raildom/Redes-II.git
cd Redes-II

# Verificar estrutura do projeto
ls -la
```

### Passo 3: Configurar e Iniciar Docker
```bash
# Limpar ambiente anterior (se existir)
docker-compose -f docker/docker-compose.yml down
docker system prune -f

# Construir e iniciar containers
docker-compose -f docker/docker-compose.yml up -d --build

# Verificar status dos containers
docker-compose -f docker/docker-compose.yml ps
```

### Passo 4: Verificar Configuração de Rede
```bash
# Verificar a rede criada
docker network inspect docker_rede_redes2

# Verificar IPs dos containers
echo "Servidor Sequencial: $(docker inspect docker_servidor_sequencial | grep -o '76\.1\.0\.[0-9]*' | head -1)"
echo "Servidor Concorrente: $(docker inspect docker_servidor_concorrente | grep -o '76\.1\.0\.[0-9]*' | head -1)"
echo "Cliente: $(docker inspect docker_cliente | grep -o '76\.1\.0\.[0-9]*' | head -1)"
```

---

## 🧪 TESTES MANUAIS

### Teste 1: Funcionamento Básico dos Servidores
```bash
# Servidor Sequencial (porta 8080)
echo "=== Testando Servidor Sequencial ==="
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" \
     -w "Status: %{http_code} | Tempo: %{time_total}s\n" \
     http://localhost:8080/

# Servidor Concorrente (porta 8081)  
echo "=== Testando Servidor Concorrente ==="
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" \
     -w "Status: %{http_code} | Tempo: %{time_total}s\n" \
     http://localhost:8081/
```

### Teste 2: Endpoints Diferentes
```bash
# Testar endpoints com diferentes tempos de processamento
for endpoint in "/" "/status" "/rapido" "/medio" "/lento"; do
    echo "Testando endpoint: $endpoint"
    curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" \
         -s -w "Tempo: %{time_total}s\n" \
         "http://localhost:8080$endpoint" | head -1
done
```

### Teste 3: Validação do Cabeçalho Personalizado
```bash
# Teste com cabeçalho correto (deve funcionar)
echo "=== Cabeçalho Correto ==="
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" \
     http://localhost:8080/ | grep -o '"id_customizado_valido":[^,]*'

# Teste com cabeçalho incorreto (deve falhar)
echo "=== Cabeçalho Incorreto ==="
curl -H "X-Custom-ID: INVALIDO" \
     http://localhost:8080/ | grep -o '"id_customizado_valido":[^,]*'
```

### Teste 4: Comparação de Concorrência
```bash
echo "=== Teste de Concorrência - Servidor Sequencial ==="
time {
    for i in {1..3}; do
        curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" \
             -s http://localhost:8080/medio &
    done
    wait
}

echo "=== Teste de Concorrência - Servidor Concorrente ==="
time {
    for i in {1..3}; do
        curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" \
             -s http://localhost:8081/medio &
    done
    wait
}
```

---

## 🤖 TESTES AUTOMATIZADOS

### Teste Completo Automatizado
```bash
# Executar bateria completa de testes
echo "Iniciando testes automatizados..."
docker exec -it docker_cliente python3 /app/testes/testes_automatizados.py

# Verificar se o arquivo de resultados foi criado
docker exec -it docker_cliente ls -la /app/resultados/test_results.json
```

### Gerar Análises Estatísticas
```bash
# Gerar gráficos e análises
echo "Gerando análises estatísticas..."
docker exec -it docker_cliente python3 /app/testes/analisar_resultados.py

# Verificar arquivos gerados
docker exec -it docker_cliente ls -la /app/resultados/plots/
```

### Copiar Resultados para o Host
```bash
# Copiar resultados para o sistema local
docker cp docker_cliente:/app/resultados ./resultados_locais
echo "Resultados copiados para ./resultados_locais"
```

---

## 🐍 EXECUÇÃO LOCAL (SEM DOCKER)

### Preparar Ambiente Python
```bash
# Instalar dependências
pip3 install -r requisitos.txt

# Ou usando ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requisitos.txt
```

### Executar Servidores Localmente
```bash
# Terminal 1: Servidor Sequencial
cd src
python3 servidor_sequencial.py

# Terminal 2: Servidor Concorrente (nova janela/terminal)
cd src
python3 servidor_concorrente.py

# Terminal 3: Testes (nova janela/terminal)
cd src
python3 cliente.py
```

### Testes Locais
```bash
# Testar servidores locais
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" http://localhost:8080/
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" http://localhost:8081/

# Executar testes automatizados localmente
cd testes
python3 testes_automatizados.py
```

---

## 📊 MONITORAMENTO E LOGS

### Visualizar Logs em Tempo Real
```bash
# Logs de todos os containers
docker-compose -f docker/docker-compose.yml logs -f

# Logs específicos
docker logs -f docker_servidor_sequencial
docker logs -f docker_servidor_concorrente
```

### Monitorar Performance
```bash
# Status dos containers
docker-compose -f docker/docker-compose.yml ps

# Uso de recursos
docker stats docker_servidor_sequencial docker_servidor_concorrente
```

---

## 🔍 SOLUÇÃO DE PROBLEMAS

### Problema: Containers não iniciam
```bash
# Solução 1: Limpar e reconstruir
docker-compose -f docker/docker-compose.yml down
docker system prune -f
docker-compose -f docker/docker-compose.yml up -d --build

# Solução 2: Verificar portas
sudo lsof -i :8080
sudo lsof -i :8081
# Se estiverem em uso, matar os processos
```

### Problema: Erro de conexão
```bash
# Verificar se containers estão rodando
docker ps

# Testar conectividade interna
docker exec -it docker_cliente ping 76.1.0.10
docker exec -it docker_cliente ping 76.1.0.11

# Verificar logs de erro
docker logs docker_servidor_sequencial
docker logs docker_servidor_concorrente
```

### Problema: Testes falhando
```bash
# Aguardar mais tempo para inicialização
sleep 60

# Verificar se servidores respondem manualmente
curl -v http://localhost:8080/

# Executar testes com mais detalhes
docker exec -it docker_cliente python3 -v /app/testes/testes_automatizados.py
```

---

## ✅ VALIDAÇÃO FINAL

### Checklist de Funcionalidades
Execute cada comando e verifique se retorna sucesso:

```bash
# ✅ 1. Servidores respondem
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -q "200" && echo "✅ Sequencial OK" || echo "❌ Sequencial FALHA"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/ | grep -q "200" && echo "✅ Concorrente OK" || echo "❌ Concorrente FALHA"

# ✅ 2. Validação de cabeçalho funciona
curl -s -H "X-Custom-ID: INVALIDO" http://localhost:8080/ | grep -q "false" && echo "✅ Validação OK" || echo "❌ Validação FALHA"

# ✅ 3. Diferentes endpoints funcionam
curl -s http://localhost:8080/status | grep -q "sequencial" && echo "✅ Endpoints OK" || echo "❌ Endpoints FALHA"

# ✅ 4. Testes automatizados executam
docker exec docker_cliente python3 /app/testes/testes_automatizados.py >/dev/null 2>&1 && echo "✅ Testes OK" || echo "❌ Testes FALHA"
```

---

## 🧹 LIMPEZA DO AMBIENTE

### Parar e Limpar Completamente
```bash
# Parar containers
docker-compose -f docker/docker-compose.yml down

# Limpar imagens e volumes do projeto
docker rmi $(docker images "docker_*" -q) 2>/dev/null || true
docker volume prune -f
docker network prune -f

# Backup dos resultados antes de limpar
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
docker cp docker_cliente:/app/resultados backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
```

---

## 📋 RESUMO DOS COMANDOS ESSENCIAIS

Para executar o projeto completo, use esta sequência:

```bash
# 1. Iniciar
docker-compose -f docker/docker-compose.yml up -d
sleep 30

# 2. Testar manualmente
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" http://localhost:8080/
curl -H "X-Custom-ID: 40093cb61c18ade519baca198537dd16" http://localhost:8081/

# 3. Executar testes rápidos (novo testador)
python3 testes/teste_cliente.py --conectividade

# 4. Executar testes completos
python3 testes/teste_cliente.py

# 5. Executar testes automatizados (antigo sistema)
docker exec -it cliente_teste python3 /app/testes/testes_automatizados.py

# 6. Gerar análises
docker exec -it cliente_teste python3 /app/testes/analisar_resultados.py

# 7. Parar
docker-compose -f docker/docker-compose.yml down
```

**🎯 Pronto! Seu projeto está funcionando e testado.**

---

## 📞 Ajuda Adicional

- **Logs detalhados:** `docker-compose -f docker/docker-compose.yml logs -f`
- **Status dos containers:** `docker-compose -f docker/docker-compose.yml ps`
- **Reiniciar tudo:** `docker-compose -f docker/docker-compose.yml restart`
- **Entrar no container:** `docker exec -it docker_cliente bash`
