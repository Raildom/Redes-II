# Makefile para o projeto Redes II
# Facilita a execução dos comandos principais

.PHONY: help start test full-test analyze stop clean logs shell all status

# Comando padrão
help:
	@echo "=== Projeto Redes II - Servidor Web Sequencial vs Concorrente ==="
	@echo "Matrícula: 20239057601"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make start      - Iniciar containers Docker"
	@echo "  make test       - Testar conectividade dos servidores"
	@echo "  make full-test  - Executar testes completos (10-15 min)"
	@echo "  make analyze    - Gerar gráficos e análises"
	@echo "  make logs       - Mostrar logs dos containers"
	@echo "  make shell      - Entrar no container de teste"
	@echo "  make status     - Status dos containers"
	@echo "  make stop       - Parar containers"
	@echo "  make clean      - Limpar ambiente Docker"
	@echo "  make all        - Executar tudo (completo)"
	@echo ""
	@echo "Para execução interativa: ./run_project.sh"

# Comandos principais
start:
	./run_project.sh start

test:
	./run_project.sh test

full-test:
	./run_project.sh full-test

analyze:
	./run_project.sh analyze

logs:
	./run_project.sh logs

shell:
	./run_project.sh shell

stop:
	./run_project.sh stop

clean:
	./run_project.sh clean

all:
	./run_project.sh all

# Comando adicional para verificar status
status:
	@echo "=== Status dos Containers ==="
	@cd docker && docker-compose ps || echo "Containers não estão rodando"
	@echo ""
	@echo "=== Redes Docker ==="
	@docker network ls | grep redes2 || echo "Rede não encontrada"

# Comando para verificar pré-requisitos
check:
	@echo "=== Verificando Pré-requisitos ==="
	@command -v docker >/dev/null 2>&1 && echo "✓ Docker instalado" || echo "✗ Docker não encontrado"
	@command -v docker-compose >/dev/null 2>&1 && echo "✓ Docker Compose instalado" || echo "✗ Docker Compose não encontrado"
	@docker info >/dev/null 2>&1 && echo "✓ Docker rodando" || echo "✗ Docker não está rodando"

# Comando para setup inicial
setup: check
	@echo "=== Setup Inicial ==="
	@echo "Projeto configurado e pronto para uso!"
	@echo "Execute 'make start' para iniciar os containers"
