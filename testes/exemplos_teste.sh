#!/bin/bash

# Script de exemplo para usar o teste_cliente.py

echo "🧪 EXEMPLOS DE USO DO TESTE_CLIENTE.PY"
echo "====================================="
echo ""

echo "📋 COMANDOS DISPONÍVEIS:"
echo ""

echo "[NUMERO] EXECUÇÃO COMPLETA (recomendado):"
echo "   python3 testes/teste_cliente.py"
echo ""

echo "[NUMERO] ESPECIFICAR AMBIENTE:"
echo "   python3 testes/teste_cliente.py --ambiente docker"
echo "   python3 testes/teste_cliente.py --ambiente local"
echo ""

echo "[NUMERO] TESTES ESPECÍFICOS:"
echo "   python3 testes/teste_cliente.py --conectividade"
echo "   python3 testes/teste_cliente.py --endpoints"
echo "   python3 testes/teste_cliente.py --cabecalho"
echo "   python3 testes/teste_cliente.py --concorrencia"
echo ""

echo "[NUMERO] COMBINAÇÕES:"
echo "   python3 testes/teste_cliente.py --ambiente docker --endpoints"
echo "   python3 testes/teste_cliente.py --ambiente local --conectividade --cabecalho"
echo ""

echo "[NUMERO] EXECUÇÃO NO DOCKER:"
echo "   docker exec -it cliente_teste python3 /app/testes/teste_cliente.py"
echo ""

echo "[NUMERO] HELP:"
echo "   python3 testes/teste_cliente.py --help"
echo ""

echo "[META] EXEMPLO PRÁTICO:"
echo "Para testar rapidamente se tudo está funcionando:"
echo "   python3 testes/teste_cliente.py --conectividade"
echo ""
