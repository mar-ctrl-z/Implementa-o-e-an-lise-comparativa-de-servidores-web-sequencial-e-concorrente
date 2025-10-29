#!/bin/bash
################################################################################
# Script de Gerenciamento de Containers Docker
# Facilita iniciar servidores sequencial e concorrente
################################################################################

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start-sequential   - Iniciar apenas servidor sequencial (porta 80)"
    echo "  start-concurrent   - Iniciar apenas servidor concorrente (porta 8080)"
    echo "  start-both         - Iniciar ambos os servidores"
    echo "  stop               - Parar todos os containers"
    echo "  logs-sequential    - Ver logs do servidor sequencial"
    echo "  logs-concurrent    - Ver logs do servidor concorrente"
    echo "  status             - Ver status dos containers"
    echo "  restart            - Reiniciar todos os containers"
    echo ""
}

case "$1" in
    start-sequential)
        echo -e "${BLUE}🚀 Iniciando servidor SEQUENCIAL...${NC}"
        docker-compose up -d server
        sleep 2
        echo -e "${GREEN}✓ Servidor sequencial rodando em http://localhost:80${NC}"
        docker-compose logs server --tail=10
        ;;
    
    start-concurrent)
        echo -e "${BLUE}🚀 Iniciando servidor CONCORRENTE...${NC}"
        docker-compose up -d server_concurrent
        sleep 2
        echo -e "${GREEN}✓ Servidor concorrente rodando em http://localhost:8080${NC}"
        docker-compose logs server_concurrent --tail=10
        ;;
    
    start-both)
        echo -e "${BLUE}🚀 Iniciando AMBOS os servidores...${NC}"
        docker-compose up -d server server_concurrent
        sleep 2
        echo -e "${GREEN}✓ Servidor sequencial: http://localhost:80${NC}"
        echo -e "${GREEN}✓ Servidor concorrente: http://localhost:8080${NC}"
        docker-compose ps
        ;;
    
    stop)
        echo -e "${YELLOW}⏹️  Parando todos os containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Containers parados${NC}"
        ;;
    
    logs-sequential)
        echo -e "${BLUE}📋 Logs do servidor SEQUENCIAL:${NC}"
        docker-compose logs -f server
        ;;
    
    logs-concurrent)
        echo -e "${BLUE}📋 Logs do servidor CONCORRENTE:${NC}"
        docker-compose logs -f server_concurrent
        ;;
    
    status)
        echo -e "${BLUE}📊 Status dos containers:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}Serviços disponíveis:${NC}"
        echo "  • Servidor Sequencial: http://localhost:80"
        echo "  • Servidor Concorrente: http://localhost:8080"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Reiniciando containers...${NC}"
        docker-compose down
        docker-compose up -d server server_concurrent
        sleep 2
        echo -e "${GREEN}✓ Containers reiniciados${NC}"
        docker-compose ps
        ;;
    
    *)
        print_usage
        exit 1
        ;;
esac

