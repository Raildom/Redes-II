#!/bin/bash
# Script principal para executar o projeto Redes II

echo "=== Projeto Redes II - Servidor Web Sequencial vs Concorrente ==="
echo "Matrícula: 20239057601"
echo "Subnet configurada: 76.1.0.0/16"
echo ""

# Função para verificar se o Docker está rodando
verificar_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "[ERRO] Docker não está rodando ou não está instalado"
        echo "Por favor, inicie o Docker e tente novamente"
        return 1
    fi
    return 0
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
    sleep 5
    
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
    
    # Verifica se o contêiner está rodando
    if ! docker ps | grep -q "cliente_teste"; then
        echo "[ERRO] Contêiner de teste não está rodando."
        echo "Execute primeiro a opção 1 (Iniciar contêineres)"
        return 1
    fi
    
    # Executa os testes com tratamento de erro
    if docker exec cliente_teste python3 testes/teste_completo.py --conectividade; then
        echo "[SUCESSO] Testes de conectividade concluídos"
    else
        echo "[ERRO] Falha nos testes de conectividade"
        echo "Verifique se os servidores estão funcionando corretamente"
        return 1
    fi
}

# Função para executar testes completos
executar_testes_completos() {
    echo ""
    echo "=== Executando testes completos ==="
    echo "Isso pode demorar alguns minutos..."
    
    # Verifica se o contêiner está rodando
    if ! docker ps | grep -q "cliente_teste"; then
        echo "[ERRO] Contêiner de teste não está rodando."
        echo "Execute primeiro a opção 1 (Iniciar contêineres)"
        return 1
    fi
    
    # Executa os testes completos com tratamento de erro
    if docker exec cliente_teste python3 testes/teste_completo.py --completo; then
        echo "[SUCESSO] Testes completos concluídos"
    else
        echo "[ERRO] Falha nos testes completos"
        echo "Verifique os logs para mais detalhes"
        return 1
    fi
}

# Função para gerar análises e gráficos
gerar_analises() {
    echo ""
    echo "=== Gerando análises e gráficos ==="
    
    # Verifica se existem resultados para analisar
    if docker exec cliente_teste test -f /app/results/test_results.json; then
        echo "Analisando resultados existentes..."
        docker exec cliente_teste python3 testes/analisar_resultados.py
    else
        echo "[AVISO] Nenhum resultado encontrado para análise."
        echo "Execute primeiro os testes com a opção 3 (Executar testes completos)"
        echo "ou use a opção 9 (Executar tudo) para executar testes e análises automaticamente."
    fi
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
limpar_ambiente() {
    echo ""
    echo "=== Limpando ambiente ==="
    
    cd docker
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    cd ..
    
    echo "[SUCESSO] Ambiente limpo"
}

# Função para mostrar logs
mostrar_logs() {
    echo ""
    echo "=== Logs dos contêineres ==="
    
    # Verifica se os contêineres estão rodando
    if ! docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
        echo "[AVISO] Contêineres não estão rodando."
        echo "Execute primeiro a opção 1 (Iniciar contêineres)"
        return 1
    fi
    
    cd docker
    docker-compose logs
    cd ..
}

# Função para entrar no contêiner de teste
entrar_conteiner_teste() {
    echo ""
    echo "=== Entrando no contêiner de teste ==="
    echo "Bem vindo ao contêiner do cliente!"
    echo "Para sair, digite 'exit'"
    
    # Verifica se o contêiner está rodando
    if ! docker ps | grep -q "cliente_teste"; then
        echo "[ERRO] Contêiner de teste não está rodando."
        echo "Execute primeiro a opção 1 (Iniciar contêineres)"
        return 1
    fi
    
    docker exec -it cliente_teste bash
}

# Menu principal
mostrar_menu() {
    echo ""
    echo "==== MENU PRINCIPAL ===="
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
if ! verificar_docker; then
    echo "Não é possível continuar sem Docker funcionando"
    if [ $# -gt 0 ]; then
        exit 1
    else
        echo "Pressione Enter para tentar novamente ou Ctrl+C para sair"
        read
    fi
fi

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
            limpar_ambiente
            ;;
        "logs")
            mostrar_logs
            ;;
        "shell")
            entrar_conteiner_teste
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
            mostrar_logs
            ;;
        6)
            entrar_conteiner_teste
            ;;
        7)
            parar_conteineres
            ;;
        8)
            limpar_ambiente
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
            parar_conteineres
            echo "Saindo..."
            break
            ;;
        *)
            echo "Opção inválida"
            ;;
    esac
done