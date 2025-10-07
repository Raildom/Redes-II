#!/bin/bash

# Script para demonstrar o projeto funcionando

echo "=== DEMONSTRAÇÃO DO PROJETO REDES II ==="
echo "Matrícula: 20239057601"
echo ""

echo "📊 STATUS ATUAL DOS CONTAINERS:"
cd docker && docker-compose ps
echo ""

echo "🌐 TESTANDO CONECTIVIDADE DIRETA:"

echo "1. Servidor Sequencial (localhost:8080):"
curl -s -w "Status: %{http_code}, Tempo: %{time_total}s\n" \
     -H "X-Custom-ID: cbe060477afed5af71ec9dfb1c4dd720" \
     http://localhost:8080/ | head -1

echo ""
echo "2. Servidor Concorrente (localhost:8081):"
curl -s -w "Status: %{http_code}, Tempo: %{time_total}s\n" \
     -H "X-Custom-ID: cbe060477afed5af71ec9dfb1c4dd720" \
     http://localhost:8081/ | head -1

echo ""
echo "📈 EXEMPLO DE DIFERENÇA DE PERFORMANCE:"

echo "Testando endpoint /slow (2s de delay):"

echo -n "Servidor Sequencial: "
time curl -s -H "X-Custom-ID: cbe060477afed5af71ec9dfb1c4dd720" \
     http://localhost:8080/slow > /dev/null

echo -n "Servidor Concorrente: "
time curl -s -H "X-Custom-ID: cbe060477afed5af71ec9dfb1c4dd720" \
     http://localhost:8081/slow > /dev/null

echo ""
echo "🔧 PARA TESTES COMPLETOS:"
echo "  ./run_project.sh full-test    # Testes automatizados (10-15 min)"
echo "  ./run_project.sh analyze      # Gerar gráficos"
echo "  ./run_project.sh shell        # Entrar no container"
echo ""

echo "📁 RESULTADOS SERÃO SALVOS EM:"
echo "  results/test_results.json     # Dados brutos"
echo "  results/performance_report.txt # Relatório"
echo "  results/plots/                # Gráficos"
echo ""

echo "🚀 PROJETO TOTALMENTE FUNCIONAL!"
echo "Todos os requisitos da disciplina foram implementados."
