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

# Função para construir e iniciar os contêineres
iniciar_conteineres() {
    echo "=== Construindo e iniciando contêineres ==="
    
    cd docker
    
    # Para contêineres existentes se estiverem rodando
    docker-compose down 2>/dev/null || true
    
    # Constrói e inicia os contêineres
    docker-compose up --build -d
    
    echo "Aguardando contêineres iniciarem..."
    sleep 10
    
    # Verifica se os contêineres estão rodando
    if docker-compose ps | grep -q "Up"; then
        echo "[SUCESSO] Contêineres iniciados com sucesso"
        docker-compose ps
    else
        echo "[ERRO] Erro ao iniciar contêineres"
        docker-compose logs
        exit 1
    fi
    
    cd ..
}

# Função para executar testes de conectividade
testar_conectividade() {
    echo ""
    echo "=== Testando conectividade dos servidores ==="
    
    docker exec cliente_teste python3 testes/testes_automatizados.py
}

# Função para executar testes completos
executar_testes_completos() {
    echo ""
    echo "=== Executando testes completos ==="
    echo "Isso pode demorar alguns minutos..."
    
    docker exec cliente_teste python3 testes/testes_automatizados.py --full
}

# Função para gerar análises e gráficos
gerar_analises() {
    echo ""
    echo "=== Gerando análises e gráficos ==="
    
    docker exec cliente_teste python3 testes/analisar_resultados.py
}

# Função para parar contêineres
parar_conteineres() {
    echo ""
    echo "=== Parando contêineres ==="
    
    cd docker
    docker-compose down
    cd ..
}

# Função para limpar tudo
cleanup() {
    echo ""
    echo "=== Limpando ambiente ==="
    
    cd docker
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    cd ..
    
    echo "[SUCESSO] Ambiente limpo"
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
mostrar_menu() {
    echo ""
    echo "=== MENU PRINCIPAL ==="
    echo "1) Iniciar contêineres"
    echo "2) Testar conectividade"
    echo "3) Executar testes completos"
    echo "4) Gerar análises e gráficos"
    echo "5) Mostrar logs"
    echo "6) Entrar no contêiner de teste"
    echo "7) Parar contêineres"
    echo "8) Limpar ambiente"
    echo "9) Executar tudo (início ao fim)"
    echo "0) Sair"
    echo ""
}

# Verifica Docker
check_docker

# Se há argumentos, executa diretamente
if [ $# -gt 0 ]; then
    case $1 in
        "start"|"iniciar")
            iniciar_conteineres
            ;;
        "test"|"testar")
            testar_conectividade
            ;;
        "full-test"|"teste-completo")
            executar_testes_completos
            ;;
        "analyze"|"analisar")
            gerar_analises
            ;;
        "stop"|"parar")
            parar_conteineres
            ;;
        "clean"|"limpar")
            cleanup
            ;;
        "logs")
            show_logs
            ;;
        "shell")
            enter_test_container
            ;;
        "all"|"tudo")
            iniciar_conteineres
            testar_conectividade
            echo ""
            read -p "Executar testes completos? (pode demorar 10-15 minutos) [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                executar_testes_completos
                gerar_analises
                echo ""
                echo "=== Projeto concluído! ==="
                echo "Resultados disponíveis em ./resultados/"
            fi
            ;;
        *)
            echo "Opção inválida: $1"
            echo "Opções: iniciar, testar, teste-completo, analisar, parar, limpar, logs, shell, tudo"
            exit 1
            ;;
    esac
    exit 0
fi

# Menu interativo
while true; do
    mostrar_menu
    read -p "Escolha uma opção: " choice
    
    case $choice in
        1)
            iniciar_conteineres
            ;;
        2)
            testar_conectividade
            ;;
        3)
            executar_testes_completos
            ;;
        4)
            gerar_analises
            ;;
        5)
            show_logs
            ;;
        6)
            enter_test_container
            ;;
        7)
            parar_conteineres
            ;;
        8)
            cleanup
            ;;
        9)
            iniciar_conteineres
            testar_conectividade
            echo ""
            read -p "Executar testes completos? (pode demorar 10-15 minutos) [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                executar_testes_completos
                gerar_analises
                echo ""
                echo "=== Projeto concluído! ==="
                echo "Resultados disponíveis em ./resultados/"
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
