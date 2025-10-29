#!/bin/bash
################################################################################
# Script de Build e Deploy Docker
# Servidor Web Sequencial e Concorrente
################################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml não encontrado!"
    print_info "Execute este script do diretório raiz do projeto"
    exit 1
fi

print_header "🐳 BUILD E DEPLOY - DOCKER CONTAINERS"

# Etapa 1: Verificar Docker
print_info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado!"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker não está rodando!"
    print_info "Inicie o Docker Desktop e tente novamente"
    exit 1
fi
print_success "Docker está rodando"

# Etapa 2: Limpar containers anteriores
print_info "Limpando containers anteriores..."
docker-compose down --remove-orphans 2>/dev/null || true
print_success "Containers antigos removidos"

# Etapa 3: Remover imagens antigas (opcional)
if [ "$1" == "--clean" ]; then
    print_info "Removendo imagens antigas..."
    docker-compose rm -f 2>/dev/null || true
    docker rmi trabalho-de-redes-server 2>/dev/null || true
    docker rmi trabalho-de-redes-client1 2>/dev/null || true
    docker rmi trabalho-de-redes-client2 2>/dev/null || true
    docker rmi trabalho-de-redes-client3 2>/dev/null || true
    print_success "Imagens antigas removidas"
fi

# Etapa 4: Build das imagens
print_header "🔨 CONSTRUINDO IMAGENS DOCKER"

print_info "Building server image..."
docker-compose build --no-cache server
print_success "Imagem do servidor construída"

print_info "Building client image..."
docker-compose build --no-cache client1 client2 client3 2>/dev/null || docker-compose build --no-cache client1
print_success "Imagem dos clientes construída"

# Etapa 5: Verificar configurações de rede
print_header "🌐 CONFIGURAÇÕES DE REDE"
print_info "Verificando docker-compose.yml..."
grep "ipv4_address" docker-compose.yml | while read line; do
    echo "  $line"
done

# Etapa 6: Iniciar containers
print_header "🚀 INICIANDO CONTAINERS"

# Opção de servidor (sequencial ou concorrente)
SERVER_TYPE=${2:-"sequential"}

if [ "$SERVER_TYPE" == "sequential" ]; then
    print_info "Iniciando servidor SEQUENCIAL..."
    docker-compose up -d server
elif [ "$SERVER_TYPE" == "concurrent" ]; then
    print_info "Iniciando servidor CONCORRENTE..."
    # Modificar comando no docker-compose temporariamente
    docker-compose up -d server
    # Atualizar para usar concurrent_server.py
    docker exec -d web_server python3 server/concurrent_server.py
else
    print_error "Tipo de servidor inválido: $SERVER_TYPE"
    print_info "Use: sequential ou concurrent"
    exit 1
fi

sleep 3

# Etapa 7: Verificar status dos containers
print_header "📊 STATUS DOS CONTAINERS"
docker-compose ps

# Etapa 8: Verificar logs do servidor
print_info "Verificando logs do servidor..."
docker-compose logs --tail=20 server

# Etapa 9: Testar conectividade
print_header "🧪 TESTANDO CONECTIVIDADE"
print_info "Testando conexão com o servidor..."
sleep 2

# Teste de ping ao container
if docker exec web_server ping -c 1 127.0.0.1 &> /dev/null; then
    print_success "Container está respondendo"
else
    print_warning "Container pode não estar totalmente pronto"
fi

# Informações finais
print_header "✅ DEPLOY CONCLUÍDO"
echo ""
echo "📋 Comandos úteis:"
echo "  • Ver logs:           docker-compose logs -f server"
echo "  • Parar containers:   docker-compose down"
echo "  • Status:             docker-compose ps"
echo "  • Entrar no server:   docker exec -it web_server /bin/bash"
echo ""
echo "🧪 Para executar testes:"
echo "  python3 client/test_client.py light_fast sequential results/test.json"
echo ""
echo "🌐 Endereços:"
echo "  • Servidor: http://localhost:80"
echo "  • Servidor IP: 54.99.12.34:80 (interno Docker)"
echo ""

print_success "Ambiente Docker pronto para testes!"

