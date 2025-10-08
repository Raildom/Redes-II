# Makefile para o projeto Redes II
# Facilita a execução dos comandos principais

.PHONY: ajuda iniciar testar teste-completo analisar parar limpar logs shell tudo status verificar configurar help start test full-test analyze stop clean all check setup

# Comando padrão
all: ajuda
ajuda:
	@echo "=== Projeto Redes II - Servidor Web Sequencial vs Concorrente ==="
	@echo "Matrícula: 20239057601"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make iniciar         - Iniciar contêineres Docker"
	@echo "  make testar          - Testar conectividade dos servidores"
	@echo "  make teste-completo  - Executar testes completos (10-15 min)"
	@echo "  make analisar        - Gerar gráficos e análises"
	@echo "  make logs            - Mostrar logs dos contêineres"
	@echo "  make shell           - Entrar no contêiner de teste"
	@echo "  make status          - Estado dos contêineres"
	@echo "  make parar           - Parar contêineres"
	@echo "  make limpar          - Limpar ambiente Docker"
	@echo "  make tudo            - Executar tudo (completo)"
	@echo ""
	@echo "Para execução interativa: ./run_project.sh"

# Comandos principais
iniciar:
	./run_project.sh iniciar

testar:
	./run_project.sh testar

teste-completo:
	./run_project.sh teste-completo

analisar:
	./run_project.sh analisar

logs:
	./run_project.sh logs

shell:
	./run_project.sh shell

parar:
	./run_project.sh parar

limpar:
	./run_project.sh limpar

tudo:
	./run_project.sh tudo

# Comando adicional para verificar status
status:
	@echo "=== Estado dos Contêineres ==="
	@cd docker && docker-compose ps || echo "Contêineres não estão rodando"
	@echo ""
	@echo "=== Redes Docker ==="
	@docker network ls | grep rede_redes2 || echo "Rede não encontrada"

# Comando para verificar pré-requisitos
verificar:
	@echo "=== Verificando Pré-requisitos ==="
	@command -v docker >/dev/null 2>&1 && echo "✓ Docker instalado" || echo "✗ Docker não encontrado"
	@command -v docker-compose >/dev/null 2>&1 && echo "✓ Docker Compose instalado" || echo "✗ Docker Compose não encontrado"
	@docker info >/dev/null 2>&1 && echo "✓ Docker rodando" || echo "✗ Docker não está rodando"

# Comando para configuração inicial
configurar: verificar
	@echo "=== Configuração Inicial ==="
	@echo "Projeto configurado e pronto para uso!"
	@echo "Execute 'make iniciar' para iniciar os contêineres"

# Mantém compatibilidade com comandos em inglês
help: ajuda
start: iniciar
test: testar
full-test: teste-completo
analyze: analisar
stop: parar
clean: limpar
all: tudo
check: verificar
setup: configurar
