#!/usr/bin/env python3
"""
Script para análise estatística dos resultados dos testes
Gera tabelas, gráficos e relatórios comparativos
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import statistics

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import matplotlib
    matplotlib.use('Agg')  # Backend não-interativo
    import matplotlib.pyplot as plt
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  Matplotlib não disponível. Gráficos não serão gerados.")
    print("   Instale com: pip install matplotlib")

# from tests.metrics import calcular_metricas_detalhadas  # Não usado


def carregar_resultados(results_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Carrega todos os arquivos JSON de resultados"""
    resultados = {
        'sequential': {},
        'concurrent': {}
    }
    
    for json_file in results_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extrai tipo de servidor e cenário do nome do arquivo
            filename = json_file.stem
            if filename.startswith('seq_'):
                server_type = 'sequential'
                scenario = filename[4:]
            elif filename.startswith('conc_'):
                server_type = 'concurrent'
                scenario = filename[5:]
            else:
                continue
            
            resultados[server_type][scenario] = data
            
        except Exception as e:
            print(f"❌ Erro ao carregar {json_file}: {e}")
    
    return resultados


def calcular_estatisticas(metricas_list: List[Dict]) -> Dict[str, Any]:
    """Calcula estatísticas agregadas de múltiplas execuções"""
    if not metricas_list:
        return {}
    
    # Extrai valores de cada métrica
    latencias = [m.get('latencia_media', 0) for m in metricas_list]
    throughputs = [m.get('throughput', 0) for m in metricas_list]
    taxas_sucesso = [m.get('taxa_sucesso', 0) for m in metricas_list]
    
    stats = {
        'latencia': {
            'media': statistics.mean(latencias),
            'desvio_padrao': statistics.stdev(latencias) if len(latencias) > 1 else 0,
            'min': min(latencias),
            'max': max(latencias),
            'mediana': statistics.median(latencias)
        },
        'throughput': {
            'media': statistics.mean(throughputs),
            'desvio_padrao': statistics.stdev(throughputs) if len(throughputs) > 1 else 0,
            'min': min(throughputs),
            'max': max(throughputs),
            'mediana': statistics.median(throughputs)
        },
        'taxa_sucesso': {
            'media': statistics.mean(taxas_sucesso),
            'desvio_padrao': statistics.stdev(taxas_sucesso) if len(taxas_sucesso) > 1 else 0,
            'min': min(taxas_sucesso),
            'max': max(taxas_sucesso)
        },
        'total_execucoes': len(metricas_list)
    }
    
    return stats


def gerar_tabela_comparativa(resultados: Dict, output_path: Path):
    """Gera tabela CSV com comparação entre servidores"""
    
    # Cabeçalho
    linhas = [
        "Cenário,Servidor,Latência Média (s),Desvio Padrão Latência,Throughput (req/s),Desvio Padrão Throughput,Taxa Sucesso (%),Execuções"
    ]
    
    # Coleta todos os cenários únicos
    cenarios = set(resultados['sequential'].keys()) | set(resultados['concurrent'].keys())
    
    for cenario in sorted(cenarios):
        # Dados do servidor sequencial
        if cenario in resultados['sequential']:
            data = resultados['sequential'][cenario]
            if 'execucoes' in data:
                stats = calcular_estatisticas(data['execucoes'])
                linhas.append(
                    f"{cenario},Sequencial,"
                    f"{stats['latencia']['media']:.4f},"
                    f"{stats['latencia']['desvio_padrao']:.4f},"
                    f"{stats['throughput']['media']:.2f},"
                    f"{stats['throughput']['desvio_padrao']:.2f},"
                    f"{stats['taxa_sucesso']['media']:.2f},"
                    f"{stats['total_execucoes']}"
                )
        
        # Dados do servidor concorrente
        if cenario in resultados['concurrent']:
            data = resultados['concurrent'][cenario]
            if 'execucoes' in data:
                stats = calcular_estatisticas(data['execucoes'])
                linhas.append(
                    f"{cenario},Concorrente,"
                    f"{stats['latencia']['media']:.4f},"
                    f"{stats['latencia']['desvio_padrao']:.4f},"
                    f"{stats['throughput']['media']:.2f},"
                    f"{stats['throughput']['desvio_padrao']:.2f},"
                    f"{stats['taxa_sucesso']['media']:.2f},"
                    f"{stats['total_execucoes']}"
                )
    
    # Salva CSV
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))
    
    print(f"✅ Tabela comparativa salva em: {output_path}")


def gerar_graficos(resultados: Dict, output_dir: Path):
    """Gera gráficos comparativos"""
    
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  Gráficos não gerados (matplotlib não disponível)")
        return
    
    cenarios = sorted(set(resultados['sequential'].keys()) | set(resultados['concurrent'].keys()))
    
    # Dados para gráficos
    dados_seq = {'latencia': [], 'throughput': [], 'labels': []}
    dados_conc = {'latencia': [], 'throughput': [], 'labels': []}
    
    for cenario in cenarios:
        # Sequencial
        if cenario in resultados['sequential']:
            data = resultados['sequential'][cenario]
            if 'execucoes' in data:
                stats = calcular_estatisticas(data['execucoes'])
                dados_seq['latencia'].append(stats['latencia']['media'])
                dados_seq['throughput'].append(stats['throughput']['media'])
                dados_seq['labels'].append(cenario)
        
        # Concorrente
        if cenario in resultados['concurrent']:
            data = resultados['concurrent'][cenario]
            if 'execucoes' in data:
                stats = calcular_estatisticas(data['execucoes'])
                dados_conc['latencia'].append(stats['latencia']['media'])
                dados_conc['throughput'].append(stats['throughput']['media'])
                if cenario not in dados_conc['labels']:
                    dados_conc['labels'].append(cenario)
    
    # Gráfico 1: Comparação de Latência
    plt.figure(figsize=(12, 6))
    x = range(len(cenarios))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], dados_seq['latencia'], width, label='Sequencial', color='#3498db')
    plt.bar([i + width/2 for i in x], dados_conc['latencia'], width, label='Concorrente', color='#e74c3c')
    
    plt.xlabel('Cenário de Teste')
    plt.ylabel('Latência Média (segundos)')
    plt.title('Comparação de Latência: Servidor Sequencial vs Concorrente')
    plt.xticks(x, cenarios, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'comparacao_latencia.png', dpi=300)
    plt.close()
    print(f"✅ Gráfico salvo: {output_dir / 'comparacao_latencia.png'}")
    
    # Gráfico 2: Comparação de Throughput
    plt.figure(figsize=(12, 6))
    
    plt.bar([i - width/2 for i in x], dados_seq['throughput'], width, label='Sequencial', color='#2ecc71')
    plt.bar([i + width/2 for i in x], dados_conc['throughput'], width, label='Concorrente', color='#f39c12')
    
    plt.xlabel('Cenário de Teste')
    plt.ylabel('Throughput (requisições/segundo)')
    plt.title('Comparação de Throughput: Servidor Sequencial vs Concorrente')
    plt.xticks(x, cenarios, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'comparacao_throughput.png', dpi=300)
    plt.close()
    print(f"✅ Gráfico salvo: {output_dir / 'comparacao_throughput.png'}")


def gerar_relatorio_markdown(resultados: Dict, stats_por_cenario: Dict, output_path: Path):
    """Gera relatório em Markdown com análise completa"""
    
    linhas = [
        "# 📊 Relatório de Análise de Performance",
        "",
        "## Marina Conrado Moreira Santos - Matrícula: 20229035217",
        "",
        "---",
        "",
        "## 📈 Resumo Executivo",
        "",
    ]
    
    # Conta total de execuções
    total_seq = sum(len(data.get('execucoes', [])) for data in resultados['sequential'].values())
    total_conc = sum(len(data.get('execucoes', [])) for data in resultados['concurrent'].values())
    
    linhas.extend([
        f"- **Total de execuções (Sequencial)**: {total_seq}",
        f"- **Total de execuções (Concorrente)**: {total_conc}",
        f"- **Cenários testados**: {len(stats_por_cenario)}",
        "",
        "---",
        "",
        "## 📊 Resultados por Cenário",
        ""
    ])
    
    for cenario, stats in sorted(stats_por_cenario.items()):
        linhas.extend([
            f"### {cenario.replace('_', ' ').title()}",
            "",
            "#### Servidor Sequencial",
            ""
        ])
        
        if 'sequential' in stats:
            s = stats['sequential']
            linhas.extend([
                f"- **Latência Média**: {s['latencia']['media']:.4f}s (± {s['latencia']['desvio_padrao']:.4f}s)",
                f"- **Throughput Médio**: {s['throughput']['media']:.2f} req/s (± {s['throughput']['desvio_padrao']:.2f})",
                f"- **Taxa de Sucesso**: {s['taxa_sucesso']['media']:.2f}%",
                ""
            ])
        
        linhas.extend([
            "#### Servidor Concorrente",
            ""
        ])
        
        if 'concurrent' in stats:
            c = stats['concurrent']
            linhas.extend([
                f"- **Latência Média**: {c['latencia']['media']:.4f}s (± {c['latencia']['desvio_padrao']:.4f}s)",
                f"- **Throughput Médio**: {c['throughput']['media']:.2f} req/s (± {c['throughput']['desvio_padrao']:.2f})",
                f"- **Taxa de Sucesso**: {c['taxa_sucesso']['media']:.2f}%",
                ""
            ])
        
        # Análise comparativa
        if 'sequential' in stats and 'concurrent' in stats:
            s = stats['sequential']
            c = stats['concurrent']
            
            melhor_latencia = "Concorrente" if c['latencia']['media'] < s['latencia']['media'] else "Sequencial"
            melhor_throughput = "Concorrente" if c['throughput']['media'] > s['throughput']['media'] else "Sequencial"
            
            dif_latencia = abs(c['latencia']['media'] - s['latencia']['media'])
            dif_throughput = abs(c['throughput']['media'] - s['throughput']['media'])
            
            linhas.extend([
                "#### 🔍 Análise Comparativa",
                "",
                f"- **Melhor Latência**: {melhor_latencia} (diferença: {dif_latencia:.4f}s)",
                f"- **Melhor Throughput**: {melhor_throughput} (diferença: {dif_throughput:.2f} req/s)",
                ""
            ])
        
        linhas.append("---")
        linhas.append("")
    
    # Conclusões
    linhas.extend([
        "## 🎯 Conclusões",
        "",
        "### Quando o Servidor Sequencial é Melhor?",
        "",
        "- Cargas leves com poucas requisições simultâneas",
        "- Cenários onde a overhead de gerenciamento de threads não compensa",
        "- Requisições muito rápidas que não se beneficiam de paralelismo",
        "",
        "### Quando o Servidor Concorrente é Melhor?",
        "",
        "- Cargas médias e pesadas com múltiplos clientes",
        "- Requisições lentas ou com I/O (onde threads podem trabalhar em paralelo)",
        "- Cenários de alta concorrência",
        "",
        "### Vantagens e Desvantagens",
        "",
        "**Servidor Sequencial:**",
        "- ✅ Simples e previsível",
        "- ✅ Menor overhead de memória",
        "- ❌ Não escala bem com múltiplos clientes",
        "",
        "**Servidor Concorrente:**",
        "- ✅ Melhor throughput em cargas altas",
        "- ✅ Maior responsividade",
        "- ❌ Maior complexidade",
        "- ❌ Overhead de gerenciamento de threads",
        ""
    ])
    
    # Salva relatório
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))
    
    print(f"✅ Relatório markdown salvo em: {output_path}")


def main():
    """Função principal"""
    print("\n📊 Analisando Resultados dos Testes...\n")
    
    # Diretórios
    project_root = Path(__file__).parent.parent
    results_dir = project_root / 'results'
    
    if not results_dir.exists():
        print("❌ Diretório 'results/' não encontrado!")
        print("💡 Execute os testes primeiro: make test-all")
        sys.exit(1)
    
    # Carrega resultados
    print("📁 Carregando resultados...")
    resultados = carregar_resultados(results_dir)
    
    total_arquivos = len(list(results_dir.glob('*.json')))
    print(f"   Encontrados {total_arquivos} arquivos de resultados")
    
    if total_arquivos == 0:
        print("❌ Nenhum arquivo de resultado encontrado!")
        sys.exit(1)
    
    # Calcula estatísticas por cenário
    stats_por_cenario = {}
    
    for server_type in ['sequential', 'concurrent']:
        for cenario, data in resultados[server_type].items():
            if cenario not in stats_por_cenario:
                stats_por_cenario[cenario] = {}
            
            if 'execucoes' in data:
                stats_por_cenario[cenario][server_type] = calcular_estatisticas(data['execucoes'])
    
    # Gera tabela CSV
    print("\n📋 Gerando tabela comparativa...")
    gerar_tabela_comparativa(resultados, results_dir / 'analise_comparativa.csv')
    
    # Gera gráficos
    print("\n📈 Gerando gráficos...")
    gerar_graficos(resultados, results_dir)
    
    # Gera relatório markdown
    print("\n📄 Gerando relatório em Markdown...")
    gerar_relatorio_markdown(resultados, stats_por_cenario, results_dir / 'ANALISE.md')
    
    print("\n✅ Análise completa!")
    print(f"\n📁 Arquivos gerados em: {results_dir}/")
    print("   - analise_comparativa.csv")
    print("   - comparacao_latencia.png")
    print("   - comparacao_throughput.png")
    print("   - ANALISE.md")
    print("")


if __name__ == '__main__':
    main()

