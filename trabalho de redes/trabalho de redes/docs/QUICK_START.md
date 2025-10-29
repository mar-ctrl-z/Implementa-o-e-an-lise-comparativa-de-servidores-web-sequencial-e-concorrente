# 🚀 Quick Start Guide

**Marina Conrado Moreira Santos - Matrícula: 20229035217**

---

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.x
- Make (já vem no macOS/Linux)

---

## 🎯 Configuração Inicial (Primeira Vez)

Execute os seguintes comandos **na ordem**:

### 1. Verificar ambiente
```bash
make setup
```

Isso verifica se Docker e Python estão instalados e cria os diretórios necessários.

### 2. Buildar imagens Docker
```bash
make build
```

Isso cria as imagens Docker dos servidores (pode demorar ~2-5 minutos na primeira vez).

### 3. Iniciar servidores
```bash
make start
```

Isso inicia ambos servidores:
- **Sequencial**: `http://localhost:80`
- **Concorrente**: `http://localhost:8080`

### 4. Verificar se estão funcionando
```bash
make status
make check
```

---

## 🧪 Executando Testes

### Teste rápido (30 segundos)
```bash
make test
```

### Bateria completa (2-3 minutos)
```bash
make test-all
```

Isso executa 10 cenários (5 por servidor) e salva os resultados em `results/`.

---

## 📊 Analisando Resultados

### Gerar análise estatística
```bash
make analyze
```

Isso cria:
- `results/analise_comparativa.csv`
- `results/ANALISE.md`

### Ver informações do projeto
```bash
make info
```

---

## 📄 Gerando Relatório

```bash
make report
```

Isso cria o template do relatório SBC em `docs/relatorio/`.

---

## 🛠️ Comandos Úteis

### Ver logs em tempo real
```bash
make logs              # Ambos servidores
make logs-seq          # Só sequencial
make logs-conc         # Só concorrente
```

### Parar servidores
```bash
make stop
```

### Reiniciar servidores
```bash
make restart
```

### Limpar arquivos temporários
```bash
make clean
```

### Rebuild completo (se algo der errado)
```bash
make rebuild
```

---

## 📁 Estrutura de Arquivos

```
trabalho-de-redes/
├── Makefile              ← Comandos automatizados
├── README.md             ← Documentação principal
├── QUICK_START.md        ← Este guia
├── config.py             ← Configurações (matrícula, nome)
├── docker-compose.yml    ← Orquestração Docker
│
├── server/               ← Servidores
│   ├── sequential_server.py
│   └── concurrent_server.py
│
├── client/               ← Cliente de testes
│   └── test_client.py
│
├── core/                 ← Módulos principais
│   ├── crypto_utils.py
│   ├── http_utils.py
│   └── server_handlers.py
│
├── tests/                ← Métricas e cenários
│   ├── metrics.py
│   └── test_scenarios.py
│
├── scripts/              ← Scripts auxiliares
│   ├── analyze_results.py
│   └── generate_report_template.py
│
├── results/              ← Resultados dos testes (gerado)
│   ├── *.json
│   ├── RESUMO_FINAL.md
│   └── ANALISE.md
│
└── docs/                 ← Documentação
    └── relatorio/        ← Relatório SBC (gerado)
```

---

## ⚡ Workflow Completo (do zero ao relatório)

```bash
# 1. Setup inicial
make setup
make build
make start

# 2. Verificar
make check

# 3. Executar testes
make test-all

# 4. Gerar análise
make analyze

# 5. Ver resultados
cat results/RESUMO_FINAL.md

# 6. Gerar template do relatório
make report

# 7. Parar servidores quando terminar
make stop
```

---

## 🐛 Solução de Problemas

### Servidores não iniciam
```bash
make rebuild
make start
```

### Testes falhando
```bash
make status          # Verificar se estão rodando
make restart         # Reiniciar
make check           # Testar conectividade
```

### Porta já em uso
```bash
make stop            # Parar tudo
lsof -i :80          # Ver o que está usando porta 80
lsof -i :8080        # Ver o que está usando porta 8080
```

### Limpar tudo e recomeçar
```bash
make clean-all       # Limpa arquivos E Docker
make setup
make build
make start
```

---

## 📞 Comandos de Diagnóstico

```bash
make help            # Lista todos comandos
make info            # Info do projeto
make status          # Status dos containers
docker ps            # Ver containers Docker
docker logs <id>     # Ver logs de um container específico
```

---

## ✅ Checklist de Entrega

- [ ] `make setup` executado com sucesso
- [ ] `make build` concluído sem erros
- [ ] `make start` inicia ambos servidores
- [ ] `make check` retorna HTTP 200
- [ ] `make test` tem taxa de sucesso > 90%
- [ ] `make test-all` executado (10 cenários)
- [ ] `make analyze` gera arquivos em results/
- [ ] Relatório SBC preenchido e compilado
- [ ] Vídeo gravado (15-20 min)
- [ ] Código no GitHub
- [ ] Email enviado aos professores

---

**Boa sorte! 🚀**
