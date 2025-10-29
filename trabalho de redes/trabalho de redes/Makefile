# Makefile para Projeto de Servidor Web Sequencial e Concorrente
# Aluno: Marina Conrado Moreira Santos
# Matrícula: 20229035217

.PHONY: help test test-all test-seq test-conc analyze report clean start stop status logs

PYTHON=python3
DOCKER_COMPOSE=docker-compose

help: ## Mostra ajuda
	@echo ""
	@echo "╔════════════════════════════════════════════════╗"
	@echo "║     MAKEFILE - Servidor Web Sequencial        ║"
	@echo "║     Marina Santos - 20229035217               ║"
	@echo "╚════════════════════════════════════════════════╝"
	@echo ""
	@echo "🔧 CONFIGURAÇÃO INICIAL:"
	@echo "  make setup      - Configura ambiente (primeira vez)"
	@echo "  make build      - Builda imagens Docker"
	@echo "  make rebuild    - Rebuild completo (limpa + build)"
	@echo ""
	@echo "🐋 GERENCIAMENTO DOCKER:"
	@echo "  make start      - Inicia servidores"
	@echo "  make stop       - Para servidores"
	@echo "  make restart    - Reinicia servidores"
	@echo "  make status     - Status dos containers"
	@echo "  make logs       - Ver logs"
	@echo ""
	@echo "🧪 TESTES:"
	@echo "  make test       - Teste rápido"
	@echo "  make test-all   - Bateria completa de testes"
	@echo "  make test-seq   - Testa servidor sequencial"
	@echo "  make test-conc  - Testa servidor concorrente"
	@echo ""
	@echo "📊 ANÁLISE:"
	@echo "  make analyze    - Gera análise estatística"
	@echo "  make report     - Gera template relatório"
	@echo "  make info       - Informações do projeto"
	@echo "  make check      - Verifica conectividade"
	@echo ""
	@echo "🧹 LIMPEZA:"
	@echo "  make clean      - Limpa arquivos temporários"
	@echo "  make clean-all  - Limpa tudo (incluindo Docker)"
	@echo ""

setup: ## Configura ambiente (primeira vez)
	@echo "🔧 Configurando ambiente..."
	@echo ""
	@echo "📋 Verificando Docker..."
	@docker --version || (echo "❌ Docker não instalado!" && exit 1)
	@$(DOCKER_COMPOSE) --version || (echo "❌ Docker Compose não instalado!" && exit 1)
	@echo "✅ Docker OK"
	@echo ""
	@echo "📋 Verificando Python..."
	@$(PYTHON) --version || (echo "❌ Python 3 não instalado!" && exit 1)
	@echo "✅ Python OK"
	@echo ""
	@echo "📋 Criando diretórios..."
	@mkdir -p results logs docs/relatorio
	@echo "✅ Diretórios criados"
	@echo ""
	@echo "✅ Setup completo! Próximo passo: make build"

build: ## Builda imagens Docker
	@echo "🔨 Construindo imagens Docker..."
	@echo ""
	@$(DOCKER_COMPOSE) build --no-cache
	@echo ""
	@echo "✅ Imagens construídas com sucesso!"
	@echo "💡 Próximo passo: make start"

rebuild: stop clean-docker build ## Rebuild completo

clean-docker: ## Limpa recursos Docker
	@echo "🐋 Limpando recursos Docker..."
	@$(DOCKER_COMPOSE) down -v --remove-orphans 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@echo "✅ Docker limpo!"

test: ## Teste rápido
	@echo "🧪 Testando servidor SEQUENCIAL..."
	@$(PYTHON) client/test_client.py light_fast sequential
	@echo ""
	@echo "🧪 Testando servidor CONCORRENTE..."
	@$(PYTHON) client/test_client.py light_fast concurrent

test-seq: ## Testa servidor sequencial
	@$(PYTHON) client/test_client.py light_fast sequential

test-conc: ## Testa servidor concorrente
	@$(PYTHON) client/test_client.py light_fast concurrent

test-all: ## Bateria completa de testes
	@echo "╔════════════════════════════════════════════════╗"
	@echo "║  🧪 BATERIA COMPLETA DE TESTES                ║"
	@echo "╚════════════════════════════════════════════════╝"
	@echo ""
	@mkdir -p results
	@echo "📊 Executando testes no servidor SEQUENCIAL..."
	@for scenario in light_fast light_slow medium_mixed heavy_fast heavy_slow; do \
		echo "  → Cenário: $$scenario"; \
		$(PYTHON) client/test_client.py $$scenario sequential results/seq_$$scenario.json || true; \
	done
	@echo ""
	@echo "📊 Executando testes no servidor CONCORRENTE..."
	@for scenario in light_fast light_slow medium_mixed heavy_fast heavy_slow; do \
		echo "  → Cenário: $$scenario"; \
		$(PYTHON) client/test_client.py $$scenario concurrent results/conc_$$scenario.json || true; \
	done
	@echo ""
	@echo "✅ Bateria de testes concluída!"
	@echo "💡 Use 'make analyze' para gerar análise"

analyze: ## Gera análise estatística
	@echo "📈 Gerando análise estatística..."
	@$(PYTHON) scripts/analyze_results.py
	@echo "✅ Análise concluída! Verifique results/"

report: ## Gera template do relatório SBC
	@echo "📄 Gerando template do relatório..."
	@$(PYTHON) scripts/generate_report_template.py
	@echo "✅ Template gerado em docs/relatorio/"

start: ## Inicia servidores
	@echo "▶️  Iniciando servidores..."
	@$(DOCKER_COMPOSE) up -d server server_concurrent
	@sleep 2
	@make status

stop: ## Para servidores
	@echo "⏹️  Parando servidores..."
	@$(DOCKER_COMPOSE) down

restart: stop start ## Reinicia servidores

status: ## Status dos containers
	@echo ""
	@echo "📊 STATUS DOS CONTAINERS:"
	@$(DOCKER_COMPOSE) ps
	@echo ""

logs: ## Ver logs
	@$(DOCKER_COMPOSE) logs -f server server_concurrent

logs-seq: ## Logs sequencial
	@$(DOCKER_COMPOSE) logs -f server

logs-conc: ## Logs concorrente
	@$(DOCKER_COMPOSE) logs -f server_concurrent

clean: ## Limpa arquivos temporários
	@echo "🧹 Limpando..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Limpeza concluída!"

clean-results: ## Remove resultados
	@echo "🗑️  Removendo resultados..."
	@rm -rf results/*.json results/*.csv results/*.png 2>/dev/null || true
	@echo "✅ Resultados removidos!"

clean-all: clean clean-docker ## Limpa tudo (arquivos + Docker)
	@echo "✅ Limpeza completa concluída!"

info: ## Informações do projeto
	@echo ""
	@echo "╔════════════════════════════════════════════════╗"
	@echo "║  ℹ️  INFORMAÇÕES DO PROJETO                   ║"
	@echo "╚════════════════════════════════════════════════╝"
	@echo ""
	@$(PYTHON) -c "from config import MATRICULA, NOME_ALUNO; print(f'👤 Aluno: {NOME_ALUNO}'); print(f'🎓 Matrícula: {MATRICULA}')"
	@echo ""
	@$(PYTHON) -c "from core.crypto_utils import gerar_custom_id; print(f'🔐 X-Custom-ID: {gerar_custom_id()}')"
	@echo ""
	@echo "📊 Portas:"
	@echo "  • Servidor Sequencial: 80"
	@echo "  • Servidor Concorrente: 8080"
	@echo ""

check: ## Verifica conectividade
	@echo "✅ Verificando servidores..."
	@echo ""
	@echo "🔍 Servidor SEQUENCIAL (porta 80):"
	@curl -s http://localhost:80/ -H "X-Custom-ID: $$($(PYTHON) -c 'from core.crypto_utils import gerar_custom_id; print(gerar_custom_id())')" | head -5 || echo "❌ Não respondeu"
	@echo ""
	@echo "🔍 Servidor CONCORRENTE (porta 8080):"
	@curl -s http://localhost:8080/ -H "X-Custom-ID: $$($(PYTHON) -c 'from core.crypto_utils import gerar_custom_id; print(gerar_custom_id())')" | head -5 || echo "❌ Não respondeu"
	@echo ""

.DEFAULT_GOAL := help

