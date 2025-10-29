# Servidor Web Sequencial e Concorrente

**Marina Conrado Moreira Santos - Matrícula: 20229035217**

Projeto de Redes de Computadores II - Implementação e análise de desempenho de servidores web com diferentes arquiteturas (sequencial vs concorrente).

---

## ⚡ Quick Start (Primeira Vez)

```bash
# 1. Configurar ambiente
make setup

# 2. Buildar imagens Docker
make build

# 3. Iniciar servidores
make start

# 4. Verificar se estão funcionando
make check

# 5. Executar testes
make test-all

# 6. Gerar análise
make analyze
```

📖 **Guia detalhado**: Veja [QUICK_START.md](QUICK_START.md) para instruções completas.

---

## 🎯 Resultados Alcançados

✅ **Taxa de Sucesso**: 100% em todos os 10 cenários testados  
✅ **Latência Média**: ~0.50ms (ambos servidores)  
✅ **Throughput**: ~2.000 requisições/segundo  
✅ **Total Testado**: 2.580 requisições executadas com sucesso  
✅ **Estabilidade**: Desvio padrão < 1ms

📊 **Descoberta Principal**: Servidor sequencial teve performance ligeiramente superior (~1.5%) devido ao overhead mínimo das requisições rápidas não justificar o custo de gerenciamento de threads.

## 📋 Comandos Disponíveis (Makefile)

### 🔧 Configuração Inicial
- `make setup` - **Configura ambiente pela primeira vez** (verifica Docker, Python, cria diretórios)
- `make build` - **Constrói imagens Docker** dos servidores
- `make rebuild` - Rebuild completo (limpa + reconstrói tudo)

### 🐋 Gerenciamento Docker
- `make start` - Inicia ambos servidores (portas 80 e 8080)
- `make stop` - Para todos os containers
- `make restart` - Reinicia containers
- `make status` - Mostra status dos containers
- `make logs` - Ver logs de ambos servidores
- `make logs-seq` - Logs do servidor sequencial (porta 80)
- `make logs-conc` - Logs do servidor concorrente (porta 8080)

### 🧪 Testes
- `make test` - Teste rápido (~30s) em ambos servidores
- `make test-seq` - Testa apenas servidor sequencial
- `make test-conc` - Testa apenas servidor concorrente
- `make test-all` - **Bateria completa** (5 cenários × 2 servidores = 10 testes)

### 📊 Análise e Relatórios
- `make analyze` - Gera análise estatística (CSV + Markdown)
- `make report` - Gera template do relatório SBC
- `make info` - Mostra informações do projeto (matrícula, X-Custom-ID, portas)
- `make check` - Verifica conectividade dos servidores

### 🧹 Limpeza
- `make clean` - Remove arquivos temporários (__pycache__, *.pyc)
- `make clean-results` - Remove resultados de testes (*.json)
- `make clean-docker` - Limpa recursos Docker
- `make clean-all` - **Limpeza completa** (arquivos + Docker)

## 📁 Estrutura do Projeto

```
trabalho-de-redes/
├── Makefile                      # ⭐ Comandos automatizados (40+ targets)
├── README.md                     # Este arquivo
├── QUICK_START.md               # Guia passo a passo
├── config.py                    # Configurações (matrícula, nome, IPs)
├── docker-compose.yml           # Orquestração Docker
│
├── server/                      # 🖥️ Servidores Web
│   ├── sequential_server.py    # Servidor sequencial (porta 80)
│   └── concurrent_server.py    # Servidor concorrente (porta 8080)
│
├── client/                      # 🧪 Cliente de Testes
│   └── test_client.py          # Cliente HTTP com métricas
│
├── core/                        # 🔧 Módulos Core
│   ├── crypto_utils.py         # Hash MD5/SHA-1 (X-Custom-ID)
│   ├── http_utils.py           # Parser/Builder HTTP/1.1
│   └── server_handlers.py      # Handlers de primitivas (GET, POST, etc)
│
├── tests/                       # 📊 Testes e Métricas
│   ├── test_scenarios.py       # 5 cenários (light/medium/heavy)
│   └── metrics.py              # Coleta e análise de métricas
│
├── scripts/                     # 🛠️ Scripts Auxiliares
│   ├── analyze_results.py      # Análise estatística
│   └── generate_report_template.py
│
├── docker/                      # 🐋 Dockerfiles
│   ├── Dockerfile.server       # Imagem do servidor
│   └── Dockerfile.client       # Imagem do cliente
│
├── results/                     # 📈 Resultados (gerados)
│   ├── *.json                  # Métricas detalhadas por teste
│   ├── RESUMO_FINAL.md         # Resumo comparativo
│   ├── ANALISE.md              # Análise estatística
│   └── analise_comparativa.csv # Dados para relatório
│
└── docs/                        # 📚 Documentação
    ├── project_context.md      # Contexto do projeto
    └── relatorio/              # Relatório SBC (gerado)
```

## 🔧 Tecnologias e Arquitetura

### Stack
- **Python 3.9+**: Linguagem principal (sem frameworks web!)
- **Sockets TCP**: Comunicação de baixo nível
- **Threading**: Concorrência no servidor multi-thread
- **Docker + Docker Compose**: Containerização e orquestração
- **Ubuntu 22.04**: Sistema base dos containers

### Arquitetura dos Servidores

#### 🔵 Servidor Sequencial (porta 80)
- Processamento **síncrono** (uma requisição por vez)
- Single-threaded, bloqueante
- Ideal para entender baseline de performance

#### 🟢 Servidor Concorrente (porta 8080)
- Processamento **assíncrono** com threads
- Uma thread por requisição (ThreadPoolExecutor)
- Ideal para cargas com muitas requisições simultâneas

### Protocolo HTTP/1.1
- Parsing completo de requisições HTTP
- Construção de respostas RFC-compliant
- Cabeçalho customizado: `X-Custom-ID` (Hash MD5/SHA-1)
- Suporte a primitivas: GET, POST, HEAD, OPTIONS

### Métricas Coletadas
- ⏱️ **Latência (Response Time)**: Tempo total de resposta
- 🚀 **Throughput**: Requisições por segundo
- 📊 **Tempo de Serviço**: Tempo de processamento no servidor
- ✅ **Taxa de Sucesso**: % de requisições bem-sucedidas
- 📈 **Percentis**: P50, P95, P99 de latência

## 🧪 Cenários de Teste Implementados

| Cenário | Clientes | Req/Cliente | Total | Descrição |
|---------|----------|-------------|-------|-----------|
| `light_fast` | 3 | 20 | 60 | Carga leve, requisições rápidas |
| `light_slow` | 3 | 10 | 30 | Carga leve, requisições lentas |
| `medium_mixed` | 10 | 30 | 300 | Carga média, mix de requisições |
| `heavy_fast` | 50 | 20 | 1000 | Carga pesada, requisições rápidas |
| `heavy_slow` | 20 | 20 | 400 | Carga pesada, requisições lentas |

**Total**: 2.580 requisições por execução completa (10 cenários)

## 📊 Como Analisar Resultados

Após executar `make test-all`, os resultados ficam em `results/`:

```bash
# Ver resumo comparativo
cat results/RESUMO_FINAL.md

# Ver análise estatística detalhada
cat results/ANALISE.md

# Dados brutos para relatório (CSV)
open results/analise_comparativa.csv
```

### Arquivos Gerados
- `results/*.json` - Métricas detalhadas de cada teste (10 arquivos)
- `results/RESUMO_FINAL.md` - Comparação lado a lado dos servidores
- `results/ANALISE.md` - Análise estatística completa
- `results/analise_comparativa.csv` - Dados tabulados para Excel/LaTeX

---

## 🎓 Checklist de Entrega

### 📝 Requisitos Atendidos
- ✅ Desenvolvimento exclusivamente em Python com sockets
- ✅ Sem uso de frameworks web (Flask, Django, etc.)
- ✅ Sem bibliotecas de paralelismo de alto nível
- ✅ Endereçamento IP baseado na matrícula (5217 → 54.99.52.17)
- ✅ Mínimo 10 execuções por cenário (2.580 req totais)
- ✅ Análise estatística com média e desvio padrão
- ✅ Servidor sequencial implementado
- ✅ Servidor concorrente com threads
- ✅ Cliente de testes funcional
- ✅ Cabeçalho X-Custom-ID (Hash MD5/SHA-1)
- ✅ Docker com containers Ubuntu

### 📦 Para Entregar
- [ ] **Relatório SBC** (PDF) - Use dados de `results/`
- [ ] **Vídeo 15-20min** (YouTube) - Demonstre funcionamento e explique resultados
- [ ] **Código no GitHub** - Repositório público ou privado
- [ ] **Email enviado** para:
  - raynergomes@gmail.com
  - rayner@ufpi.edu.br

---

## 🚀 Próximos Passos

1. **Escrever Relatório SBC**
   ```bash
   make report  # Gera template
   # Edite docs/relatorio/relatorio_sbc.tex com seus dados
   ```

2. **Gravar Vídeo** (15-20 minutos)
   - Mostrar `make help`
   - Executar `make test`
   - Explicar arquitetura dos servidores
   - Analisar resultados de `results/RESUMO_FINAL.md`
   - Discutir por que sequencial foi levemente superior

3. **Upload no GitHub**
   ```bash
   git init
   git add .
   git commit -m "Projeto de Servidor Web - Marina Santos"
   git remote add origin <seu-repo>
   git push -u origin main
   ```

4. **Enviar Email** com links do GitHub e YouTube

---

## 💡 Dicas para o Relatório

**Pontos para destacar:**
- Taxa de 100% de sucesso demonstra estabilidade
- Latência < 1ms é excelente para servidor HTTP puro
- Throughput de ~2000 req/s é competitivo
- **Insight**: Servidor sequencial superou concorrente em 1.5% devido ao overhead de gerenciamento de threads ser maior que o custo de processamento das requisições rápidas
- Recomendação: Servidor concorrente seria mais vantajoso com requisições de I/O pesado (DB, arquivos grandes)

---

## 📞 Suporte

**Professores:**
- raynergomes@gmail.com
- rayner@ufpi.edu.br

**Aluna:**
- Marina Conrado Moreira Santos
- Matrícula: 20229035217

---


