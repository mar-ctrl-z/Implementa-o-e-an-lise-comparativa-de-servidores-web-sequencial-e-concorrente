#!/usr/bin/env python3
"""
Gera template de relatório no formato SBC (LaTeX)
"""

import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MATRICULA, NOME_ALUNO


TEMPLATE_LATEX = r'''% Template de Relatório - Formato SBC
% Aluno: ''' + NOME_ALUNO + r'''
% Matrícula: ''' + MATRICULA + r'''

\documentclass[12pt]{article}

\usepackage{sbc-template}
\usepackage{graphicx,url}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{amsmath}

\sloppy

\title{Análise Comparativa de Servidores Web:\\Sequencial vs Concorrente}

\author{''' + NOME_ALUNO + r'''}

\address{Universidade Federal do Piauí (UFPI)\\
  Disciplina: Redes de Computadores II\\
  Matrícula: ''' + MATRICULA + r'''
  \email{[seu-email]@[dominio].com}
}

\begin{document}

\maketitle

\begin{abstract}
Este trabalho apresenta uma análise comparativa entre servidores web implementados com arquiteturas sequencial síncrona e concorrente assíncrona. Foram desenvolvidos dois servidores HTTP/1.1 utilizando sockets TCP em Python, avaliados sob diferentes cenários de carga. Os resultados demonstram as vantagens e limitações de cada abordagem, fornecendo insights sobre quando cada arquitetura é mais apropriada.
\end{abstract}

\section{Introdução}

A escolha entre arquiteturas sequenciais e concorrentes é fundamental no design de servidores web. Enquanto servidores sequenciais oferecem simplicidade e previsibilidade, servidores concorrentes prometem maior throughput e responsividade. Este trabalho investiga empiricamente estas diferenças através de uma implementação prática e testes controlados.

\subsection{Objetivos}

\begin{itemize}
    \item Implementar servidor web sequencial síncrono usando sockets TCP
    \item Implementar servidor web concorrente usando threads
    \item Definir métricas de performance apropriadas
    \item Avaliar ambos servidores sob diferentes cenários de carga
    \item Identificar vantagens e desvantagens de cada abordagem
\end{itemize}

\section{Fundamentação Teórica}

\subsection{Servidor Sequencial Síncrono}

Um servidor sequencial processa uma requisição por vez, bloqueando a aceitação de novas conexões até que a requisição corrente seja completamente processada. Este modelo é simples de implementar e debugar, mas não escala bem sob alta concorrência.

\subsection{Servidor Concorrente com Threads}

Servidores concorrentes utilizam múltiplas threads de execução para processar requisições simultaneamente. Cada conexão é delegada a uma thread worker, permitindo que o servidor continue aceitando novas conexões enquanto outras estão sendo processadas.

\subsection{Protocolo HTTP/1.1}

Ambos servidores implementam um subconjunto do protocolo HTTP/1.1, incluindo:
\begin{itemize}
    \item Métodos: GET, POST, HEAD
    \item Códigos de status: 200, 400, 401, 404, 500
    \item Cabeçalhos customizados para autenticação
\end{itemize}

\section{Metodologia}

\subsection{Ambiente de Desenvolvimento}

\begin{itemize}
    \item \textbf{Linguagem}: Python 3.x
    \item \textbf{Biblioteca de Rede}: Socket (TCP)
    \item \textbf{Paralelismo}: ThreadPoolExecutor (concurrent.futures)
    \item \textbf{Containerização}: Docker + Docker Compose
    \item \textbf{Endereçamento IP}: Baseado nos 4 últimos dígitos da matrícula
\end{itemize}

\subsection{Métricas de Performance}

As seguintes métricas foram definidas para avaliar os servidores:

\begin{equation}
\text{Latência Média} = \frac{1}{n} \sum_{i=1}^{n} (t_{fim}^{i} - t_{inicio}^{i})
\end{equation}

\begin{equation}
\text{Throughput} = \frac{\text{Total de Requisições}}{\text{Tempo Total}}
\end{equation}

\begin{equation}
\text{Taxa de Sucesso} = \frac{\text{Requisições Bem-sucedidas}}{\text{Total de Requisições}} \times 100\%
\end{equation}

\begin{equation}
\text{Desvio Padrão} = \sqrt{\frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2}
\end{equation}

\subsection{Cenários de Teste}

Foram elaborados os seguintes cenários para avaliar diferentes aspectos dos servidores:

\begin{table}[h]
\centering
\caption{Cenários de Teste Definidos}
\label{tab:cenarios}
\begin{tabular}{@{}lccl@{}}
\toprule
\textbf{Cenário} & \textbf{Clientes} & \textbf{Req/Cliente} & \textbf{Tipo} \\ \midrule
Light Fast       & 3                 & 10                    & Rápidas       \\
Light Slow       & 3                 & 10                    & Lentas        \\
Medium Mixed     & 10                & 15                    & Mistas        \\
Heavy Stress     & 30                & 20                    & Rápidas       \\
Heavy Slow       & 20                & 10                    & Lentas        \\ \bottomrule
\end{tabular}
\end{table}

Cada cenário foi executado \textbf{10 vezes} para garantir significância estatística.

\section{Implementação}

\subsection{Servidor Sequencial}

\begin{verbatim}
def run_server():
    with socket.socket(socket.AF_INET, 
                       socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        
        while True:
            conn, addr = sock.accept()
            handle_request(conn, addr)
            conn.close()
\end{verbatim}

\subsection{Servidor Concorrente}

\begin{verbatim}
def run_server():
    executor = ThreadPoolExecutor(max_workers=20)
    
    with socket.socket(socket.AF_INET, 
                       socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        
        while True:
            conn, addr = sock.accept()
            executor.submit(handle_request, 
                          conn, addr)
\end{verbatim}

\subsection{Autenticação Customizada}

Ambos servidores implementam autenticação através do cabeçalho \texttt{X-Custom-ID}, calculado como:

\begin{equation}
\text{X-Custom-ID} = \text{SHA1}(\text{matrícula} + \text{" "} + \text{nome})
\end{equation}

\section{Resultados}

\subsection{Análise Quantitativa}

\textit{[INSERIR AQUI: Tabela com resultados de latência e throughput para cada cenário]}

\begin{table}[h]
\centering
\caption{Resultados de Performance}
\label{tab:resultados}
\begin{tabular}{@{}llcc@{}}
\toprule
\textbf{Cenário} & \textbf{Servidor} & \textbf{Latência (s)} & \textbf{Throughput (req/s)} \\ \midrule
Light Fast       & Sequencial        & X.XXXX ± X.XXXX       & XX.XX ± X.XX                \\
                 & Concorrente       & X.XXXX ± X.XXXX       & XX.XX ± X.XX                \\
\midrule
Medium Mixed     & Sequencial        & X.XXXX ± X.XXXX       & XX.XX ± X.XX                \\
                 & Concorrente       & X.XXXX ± X.XXXX       & XX.XX ± X.XX                \\
\midrule
Heavy Stress     & Sequencial        & X.XXXX ± X.XXXX       & XX.XX ± X.XX                \\
                 & Concorrente       & X.XXXX ± X.XXXX       & XX.XX ± X.XX                \\ \bottomrule
\end{tabular}
\end{table}

\subsection{Análise Gráfica}

\textit{[INSERIR AQUI: Gráficos de comparação]}

\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{../../results/comparacao_latencia.png}
\caption{Comparação de Latência entre Servidores}
\label{fig:latencia}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{../../results/comparacao_throughput.png}
\caption{Comparação de Throughput entre Servidores}
\label{fig:throughput}
\end{figure}

\section{Discussão}

\subsection{Quando o Servidor Sequencial é Melhor?}

\textit{[PREENCHER com base nos resultados obtidos]}

O servidor sequencial demonstrou vantagens em:
\begin{itemize}
    \item Cargas leves (poucos clientes)
    \item Requisições muito rápidas
    \item Cenários onde a overhead de threads não compensa
\end{itemize}

\subsection{Quando o Servidor Concorrente é Melhor?}

\textit{[PREENCHER com base nos resultados obtidos]}

O servidor concorrente mostrou-se superior em:
\begin{itemize}
    \item Cargas médias e pesadas
    \item Alta concorrência
    \item Requisições com I/O ou processamento lento
\end{itemize}

\subsection{Vantagens e Desvantagens}

\textbf{Servidor Sequencial:}
\begin{itemize}
    \item \textbf{Vantagens}: Simplicidade, menor uso de memória, previsibilidade
    \item \textbf{Desvantagens}: Baixo throughput, não escala, bloqueia clientes
\end{itemize}

\textbf{Servidor Concorrente:}
\begin{itemize}
    \item \textbf{Vantagens}: Alto throughput, responsividade, escala melhor
    \item \textbf{Desvantagens}: Maior complexidade, overhead de threads, race conditions
\end{itemize}

\section{Considerações Finais}

Este trabalho demonstrou empiricamente as diferenças entre arquiteturas sequenciais e concorrentes para servidores web. Os resultados confirmam que não existe uma "melhor" arquitetura absoluta, mas sim diferentes trade-offs adequados a diferentes contextos.

Para aplicações com baixa carga e requisições rápidas, a simplicidade do modelo sequencial pode ser vantajosa. Já para aplicações web modernas com alta concorrência, o modelo concorrente é essencial.

\subsection{Trabalhos Futuros}

\begin{itemize}
    \item Implementar servidor assíncrono com asyncio
    \item Avaliar modelo multiprocesso vs threads
    \item Testes com requisições de diferentes tamanhos
    \item Análise de consumo de memória e CPU
\end{itemize}

\bibliographystyle{sbc}
\bibliography{sbc-template}

\end{document}
'''


README_RELATORIO = '''# 📄 Relatório SBC

## Estrutura do Relatório

Este diretório contém o relatório no formato SBC (Sociedade Brasileira de Computação).

## Arquivos

- `relatorio_sbc.tex` - Documento LaTeX principal
- `sbc-template.sty` - Estilo SBC (baixar de: https://www.sbc.org.br/documentos-da-sbc/summary/169-templates-para-artigos-e-capitulos-de-livros/878-modelosparapublicaodeartigos)

## Como Compilar

### Online (Recomendado)
1. Acesse [Overleaf](https://www.overleaf.com/)
2. Faça upload dos arquivos
3. Compile online

### Local (Linux/Mac)
```bash
pdflatex relatorio_sbc.tex
pdflatex relatorio_sbc.tex  # Segunda passagem para referências
```

### Local (Windows)
Instale MiKTeX ou TeX Live e compile usando TeXworks ou TeXstudio.

## Preenchimento

1. ✅ **Dados pessoais** já estão preenchidos automaticamente
2. 📊 **Resultados**: Após executar `make test-all` e `make analyze`, copie os valores das tabelas para o relatório
3. 📈 **Gráficos**: Já estão referenciados, certifique-se que os arquivos PNG existam em `results/`
4. 📝 **Discussão**: Preencha com suas análises baseadas nos resultados obtidos

## Checklist

- [ ] Baixar `sbc-template.sty` e colocar neste diretório
- [ ] Preencher seção de Resultados com dados reais
- [ ] Inserir gráficos (já gerados automaticamente)
- [ ] Preencher Discussão com análises
- [ ] Revisar Conclusão
- [ ] Compilar e gerar PDF final
- [ ] Incluir email correto no template

## Recursos

- Template SBC: https://www.sbc.org.br/documentos-da-sbc/summary/169-templates-para-artigos-e-capitulos-de-livros/878-modelosparapublicaodeartigos
- Overleaf: https://www.overleaf.com/
'''


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera template de relatório SBC')
    parser.add_argument('--force', action='store_true', help='Sobrescreve arquivos existentes')
    args = parser.parse_args()
    
    # Diretório de destino
    project_root = Path(__file__).parent.parent
    relatorio_dir = project_root / 'docs' / 'relatorio'
    relatorio_dir.mkdir(parents=True, exist_ok=True)
    
    # Arquivos
    tex_file = relatorio_dir / 'relatorio_sbc.tex'
    readme_file = relatorio_dir / 'README.md'
    
    # Verifica se já existe
    if tex_file.exists() and not args.force:
        print(f"⚠️  Arquivo {tex_file} já existe!")
        print("   Use --force para sobrescrever")
        return
    
    # Cria arquivo LaTeX
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(TEMPLATE_LATEX)
    print(f"✅ Template LaTeX criado: {tex_file}")
    
    # Cria README
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(README_RELATORIO)
    print(f"✅ README criado: {readme_file}")
    
    print("\n📄 Template do relatório SBC gerado com sucesso!")
    print(f"\n📁 Localização: {relatorio_dir}/")
    print("\n📝 Próximos passos:")
    print("   1. Baixar sbc-template.sty de: https://www.sbc.org.br/")
    print("   2. Executar testes: make test-all")
    print("   3. Gerar análises: make analyze")
    print("   4. Preencher resultados no relatório")
    print("   5. Compilar LaTeX (Overleaf recomendado)")
    print("")


if __name__ == '__main__':
    main()

