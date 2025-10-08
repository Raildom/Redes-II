# 🧪 Pasta de Testes - Projeto Redes II

Esta pasta contém todos os arquivos relacionados a testes do projeto.

## 📁 Estrutura de Arquivos

### 🎯 **Testes Principais**
- **`teste_cliente.py`** - Testador completo e modular (NOVO)
- **`testes_automatizados.py`** - Bateria completa de testes automatizados
- **`analisar_resultados.py`** - Geração de gráficos e análises estatísticas

### 📖 **Exemplos e Documentação**
- **`exemplos_teste.sh`** - Exemplos de uso do teste_cliente.py
- **`exemplos_uso.py`** - Exemplos de uso das classes (antigo)

## 🚀 **Como Usar**

### Teste Rápido (Recomendado)
```bash
# Do diretório raiz do projeto
python3 testes/teste_cliente.py --conectividade
```

### Teste Completo
```bash
# Do diretório raiz do projeto
python3 testes/teste_cliente.py
```

### Testes Específicos
```bash
python3 testes/teste_cliente.py --endpoints      # Testar endpoints
python3 testes/teste_cliente.py --cabecalho      # Validação de cabeçalhos
python3 testes/teste_cliente.py --concorrencia   # Teste de concorrência
```

### Execução no Docker
```bash
docker exec -it cliente_teste python3 /app/testes/teste_cliente.py
```

### Testes Automatizados (Sistema Antigo)
```bash
docker exec -it cliente_teste python3 /app/testes/testes_automatizados.py
```

### Análises Estatísticas
```bash
docker exec -it cliente_teste python3 /app/testes/analisar_resultados.py
```

## 🎯 **Diferenças entre os Testadores**

### `teste_cliente.py` (NOVO)
- ✅ Detecção automática de ambiente (Docker/Local)
- ✅ Testes modulares e específicos
- ✅ Relatórios comparativos
- ✅ Execução rápida e flexível
- ✅ Interface simples

### `testes_automatizados.py` (Antigo)
- ✅ Bateria completa de testes estatísticos
- ✅ Múltiplas iterações para análise
- ✅ Geração de arquivos JSON de resultados
- ✅ Integração com analisar_resultados.py

## 📊 **Fluxo Recomendado**

1. **Teste rápido**: `python3 testes/teste_cliente.py --conectividade`
2. **Teste completo**: `python3 testes/teste_cliente.py`
3. **Análise estatística**: `python3 testes/testes_automatizados.py`
4. **Gráficos**: `python3 testes/analisar_resultados.py`

## 🆔 **Configuração**

Todos os testes usam automaticamente:
- **Matrícula**: 20239057601
- **X-Custom-ID**: 40093cb61c18ade519baca198537dd16
- **Sub-rede Docker**: 76.1.0.0/16
- **IPs**: 76.1.0.10 (sequencial), 76.1.0.11 (concorrente)
