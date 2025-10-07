#!/bin/bash

# Script principal para executar o projeto Redes II

set -e  # Para em caso de erro

echo "=== Projeto Redes II - Servidor Web Sequencial vs Concorrente ==="
echo "Matrícula: 20239057601"
echo "Subnet configurada: 76.1.0.0/16"
echo ""

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "Erro: Docker não está rodando ou não está instalado"
        exit 1
    fi
}

# Função para construir e iniciar os containers
start_containers() {
    echo "=== Construindo e iniciando containers ==="
    
    cd docker
    
    # Para containers existentes se estiverem rodando
    docker-compose down 2>/dev/null || true
    
    # Constrói e inicia os containers
    docker-compose up --build -d
    
    echo "Aguardando containers iniciarem..."
    sleep 10
    
    # Verifica se os containers estão rodando
    if docker-compose ps | grep -q "Up"; then
        echo "✓ Containers iniciados com sucesso"
        docker-compose ps
    else
        echo "✗ Erro ao iniciar containers"
        docker-compose logs
        exit 1
    fi
    
    cd ..
}

# Função para executar testes de conectividade
test_connectivity() {
    echo ""
    echo "=== Testando conectividade dos servidores ==="
    
    docker exec cliente_teste python3 testes/testes_automatizados.py
}

# Função para executar testes completos
run_full_tests() {
    echo ""
    echo "=== Executando testes completos ==="
    echo "Isso pode demorar alguns minutos..."
    
    docker exec cliente_teste python3 testes/testes_automatizados.py --full
}

# Função para gerar análises e gráficos
generate_analysis() {
    echo ""
    echo "=== Gerando análises e gráficos ==="
    
    docker exec cliente_teste python3 testes/analisar_resultados.py
}

# Função para parar containers
stop_containers() {
    echo ""
    echo "=== Parando containers ==="
    
    cd docker
    docker-compose down
    cd ..
    
    echo "✓ Containers parados"
}

# Função para limpar tudo
cleanup() {
    echo ""
    echo "=== Limpando ambiente ==="
    
    cd docker
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    cd ..
    
    echo "✓ Ambiente limpo"
}

# Função para mostrar logs
show_logs() {
    echo ""
    echo "=== Logs dos containers ==="
    
    cd docker
    docker-compose logs
    cd ..
}

# Função para entrar no container de teste
enter_test_container() {
    echo ""
    echo "=== Entrando no container de teste ==="
    echo "Para sair, digite 'exit'"
    
    docker exec -it test_client bash
}

# Menu principal
show_menu() {
    echo ""
    echo "=== MENU PRINCIPAL ==="
    echo "1) Iniciar containers"
    echo "2) Testar conectividade"
    echo "3) Executar testes completos"
    echo "4) Gerar análises e gráficos"
    echo "5) Mostrar logs"
    echo "6) Entrar no container de teste"
    echo "7) Parar containers"
    echo "8) Limpar ambiente"
    echo "9) Executar tudo (inicio ao fim)"
    echo "0) Sair"
    echo ""
}

# Verifica Docker
check_docker

# Se há argumentos, executa diretamente
if [ $# -gt 0 ]; then
    case $1 in
        "start")
            start_containers
            ;;
        "test")
            test_connectivity
            ;;
        "full-test")
            run_full_tests
            ;;
        "analyze")
            generate_analysis
            ;;
        "stop")
            stop_containers
            ;;
        "clean")
            cleanup
            ;;
        "logs")
            show_logs
            ;;
        "shell")
            enter_test_container
            ;;
        "all")
            start_containers
            test_connectivity
            echo ""
            read -p "Executar testes completos? (pode demorar 10-15 minutos) [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_full_tests
                generate_analysis
                echo ""
                echo "=== Projeto concluído! ==="
                echo "Resultados disponíveis em ./results/"
            fi
            ;;
        *)
            echo "Opção inválida: $1"
            echo "Opções: start, test, full-test, analyze, stop, clean, logs, shell, all"
            exit 1
            ;;
    esac
    exit 0
fi

# Menu interativo
while true; do
    show_menu
    read -p "Escolha uma opção: " choice
    
    case $choice in
        1)
            start_containers
            ;;
        2)
            test_connectivity
            ;;
        3)
            run_full_tests
            ;;
        4)
            generate_analysis
            ;;
        5)
            show_logs
            ;;
        6)
            enter_test_container
            ;;
        7)
            stop_containers
            ;;
        8)
            cleanup
            ;;
        9)
            start_containers
            test_connectivity
            echo ""
            read -p "Executar testes completos? (pode demorar 10-15 minutos) [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_full_tests
                generate_analysis
                echo ""
                echo "=== Projeto concluído! ==="
                echo "Resultados disponíveis em ./results/"
            fi
            ;;
        0)
            echo "Saindo..."
            break
            ;;
        *)
            echo "Opção inválida"
            ;;
    esac
done
