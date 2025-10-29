#!/usr/bin/env python3
"""
Métricas de Performance para Servidores Web
Define métricas matemáticas para avaliação de desempenho dos servidores sequencial e concorrente
"""

import time
import statistics
import math
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RequestMetrics:
    """Métricas de uma requisição individual"""
    request_id: int
    start_time: float
    end_time: float
    response_time: float  # Tempo de resposta (latência)
    status_code: int
    success: bool
    server_type: str  # 'sequential' ou 'concurrent'

    @property
    def latency_ms(self) -> float:
        """Latência em milissegundos"""
        return self.response_time * 1000

class PerformanceMetrics:
    """
    Calculadora de métricas de performance para servidores web

    Métricas definidas conforme requisitos:
    - Latência média (Mean Latency)
    - Throughput (Requisições por segundo)
    - Tempo de serviço (Service Time)
    - Taxa de erro (Error Rate)
    - Utilização do servidor (Server Utilization)
    """

    def __init__(self):
        self.requests: List[RequestMetrics] = []
        self.test_start_time: float = 0
        self.test_end_time: float = 0

    def add_request(self, request: RequestMetrics):
        """Adiciona uma requisição às métricas"""
        self.requests.append(request)

    def start_test(self):
        """Marca o início do teste"""
        self.test_start_time = time.time()

    def end_test(self):
        """Marca o fim do teste"""
        self.test_end_time = time.time()

    @property
    def test_duration(self) -> float:
        """Duração total do teste em segundos"""
        if self.test_end_time > self.test_start_time:
            return self.test_end_time - self.test_start_time
        return time.time() - self.test_start_time

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calcula todas as métricas de performance

        Returns:
            Dict contendo todas as métricas calculadas
        """
        if not self.requests:
            return self._empty_metrics()

        # Métricas básicas
        total_requests = len(self.requests)
        successful_requests = len([r for r in self.requests if r.success])
        failed_requests = total_requests - successful_requests

        # Latências de todas as requisições
        latencies = [r.response_time for r in self.requests]
        successful_latencies = [r.response_time for r in self.requests if r.success]

        # Cálculos estatísticos
        metrics = {
            # === MÉTRICAS BÁSICAS ===
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "test_duration_seconds": self.test_duration,

            # === TAXA DE SUCESSO ===
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "error_rate": failed_requests / total_requests if total_requests > 0 else 0,

            # === LATÊNCIA (RESPONSE TIME) ===
            # Latência média: μ = (1/n) * Σ(response_time_i)
            "mean_latency_seconds": statistics.mean(latencies) if latencies else 0,
            "mean_latency_ms": statistics.mean(latencies) * 1000 if latencies else 0,

            # Latência mediana
            "median_latency_seconds": statistics.median(latencies) if latencies else 0,
            "median_latency_ms": statistics.median(latencies) * 1000 if latencies else 0,

            # Desvio padrão da latência: σ = sqrt( (1/(n-1)) * Σ((x_i - μ)²) )
            "latency_std_seconds": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "latency_std_ms": statistics.stdev(latencies) * 1000 if len(latencies) > 1 else 0,

            # Latência mínima e máxima
            "min_latency_seconds": min(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) * 1000 if latencies else 0,
            "max_latency_seconds": max(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) * 1000 if latencies else 0,

            # Percentis (importantes para análise de performance)
            "latency_p95_seconds": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies) if latencies else 0,  # 95th percentile
            "latency_p99_seconds": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies) if latencies else 0,  # 99th percentile

            # === THROUGHPUT ===
            # Throughput: λ = total_requests / test_duration
            "throughput_rps": total_requests / self.test_duration if self.test_duration > 0 else 0,  # requests per second
            "throughput_rpm": (total_requests / self.test_duration) * 60 if self.test_duration > 0 else 0,  # requests per minute

            # Throughput de sucesso
            "successful_throughput_rps": successful_requests / self.test_duration if self.test_duration > 0 else 0,

            # === TEMPO DE SERVIÇO ===
            # Service Time: tempo que o servidor gasta processando requisições
            # Para este projeto, service time ≈ response time (já que não temos medição separada)
            "mean_service_time_seconds": statistics.mean(successful_latencies) if successful_latencies else 0,
            "service_time_std_seconds": statistics.stdev(successful_latencies) if len(successful_latencies) > 1 else 0,

            # === UTILIZAÇÃO DO SERVIDOR ===
            # Server Utilization: U = (service_time * arrival_rate) / num_servers
            # Para servidor sequencial: U = service_time / inter_arrival_time médio
            # Para servidor concorrente: U = (service_time * λ) / num_threads

            # === CONFIABILIDADE ===
            # Coefficient of Variation (CoV) da latência: CoV = σ/μ
            "latency_cov": (statistics.stdev(latencies) / statistics.mean(latencies)) if latencies and statistics.mean(latencies) > 0 else 0,

            # === EFICIÊNCIA ===
            # Efficiency: E = throughput / (mean_latency * num_servers)
            # Maior eficiência = melhor distribuição de carga

            # === TIMESTAMP DA ANÁLISE ===
            "analysis_timestamp": datetime.now().isoformat(),
            "server_type": self.requests[0].server_type if self.requests else "unknown"
        }

        # Cálculos adicionais que dependem de outras métricas
        metrics.update(self._calculate_advanced_metrics(metrics))

        return metrics

    def _calculate_advanced_metrics(self, base_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas avançadas baseadas nas métricas básicas"""
        advanced = {}

        # Eficiência do servidor
        mean_latency = base_metrics["mean_latency_seconds"]
        throughput = base_metrics["throughput_rps"]

        if mean_latency > 0:
            # Efficiency: quanto maior, melhor (mais requisições por unidade de latência)
            advanced["server_efficiency"] = throughput / mean_latency
        else:
            advanced["server_efficiency"] = 0

        # Taxa de processamento (requests per second por segundo de latência média)
        advanced["processing_rate"] = throughput * (1 / mean_latency) if mean_latency > 0 else 0

        # Índice de performance (throughput / latência)
        advanced["performance_index"] = throughput / base_metrics["mean_latency_ms"] if base_metrics["mean_latency_ms"] > 0 else 0

        return advanced

    def _empty_metrics(self) -> Dict[str, Any]:
        """Retorna métricas vazias para quando não há dados"""
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "test_duration_seconds": 0,
            "success_rate": 0,
            "error_rate": 0,
            "mean_latency_seconds": 0,
            "mean_latency_ms": 0,
            "throughput_rps": 0,
            "server_type": "unknown",
            "analysis_timestamp": datetime.now().isoformat()
        }

    def get_summary_report(self) -> str:
        """
        Gera um relatório resumido das métricas em formato texto

        Returns:
            String com relatório formatado
        """
        metrics = self.calculate_metrics()

        report = f"""
{'='*60}
RELATÓRIO DE PERFORMANCE - {metrics['server_type'].upper()}
{'='*60}

📊 MÉTRICAS GERAIS:
   • Total de requisições: {metrics['total_requests']}
   • Requisições bem-sucedidas: {metrics['successful_requests']}
   • Taxa de sucesso: {metrics['success_rate']:.1%}
   • Duração do teste: {metrics['test_duration_seconds']:.2f}s

🏁 LATÊNCIA (Response Time):
   • Média: {metrics['mean_latency_ms']:.2f}ms
   • Mediana: {metrics['median_latency_ms']:.2f}ms
   • Desvio padrão: {metrics['latency_std_ms']:.2f}ms
   • Mínima: {metrics['min_latency_ms']:.2f}ms
   • Máxima: {metrics['max_latency_ms']:.2f}ms
   • 95º percentil: {metrics['latency_p95_seconds']*1000:.2f}ms

⚡ THROUGHPUT:
   • Requisições/segundo: {metrics['throughput_rps']:.2f} req/s
   • Requisições/minuto: {metrics['throughput_rpm']:.1f} req/min
   • Throughput de sucesso: {metrics['successful_throughput_rps']:.2f} req/s

🔧 TEMPO DE SERVIÇO:
   • Média: {metrics['mean_service_time_seconds']*1000:.2f}ms
   • Desvio padrão: {metrics['service_time_std_seconds']*1000:.2f}ms

📈 EFICIÊNCIA:
   • Índice de performance: {metrics['performance_index']:.4f}
   • Eficiência do servidor: {metrics['server_efficiency']:.4f}
   • Coeficiente de variação: {metrics['latency_cov']:.4f}

⏰ ANÁLISE GERADA EM: {metrics['analysis_timestamp']}
{'='*60}
"""
        return report

    def export_to_json(self, filename: str):
        """Exporta métricas para arquivo JSON"""
        import json
        metrics = self.calculate_metrics()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        print(f"📄 Métricas exportadas para {filename}")

    def compare_with(self, other: 'PerformanceMetrics') -> Dict[str, Any]:
        """
        Compara métricas com outro conjunto de métricas

        Args:
            other: Outro objeto PerformanceMetrics para comparação

        Returns:
            Dict com métricas de comparação
        """
        self_metrics = self.calculate_metrics()
        other_metrics = other.calculate_metrics()

        comparison = {
            "comparison_timestamp": datetime.now().isoformat(),
            "server_a_type": self_metrics["server_type"],
            "server_b_type": other_metrics["server_type"],
            "metrics_comparison": {}
        }

        # Comparar métricas principais
        key_metrics = [
            "throughput_rps", "mean_latency_ms", "success_rate",
            "latency_std_ms", "server_efficiency", "performance_index"
        ]

        for metric in key_metrics:
            self_val = self_metrics.get(metric, 0)
            other_val = other_metrics.get(metric, 0)

            if self_val != 0 and other_val != 0:
                ratio = other_val / self_val
                improvement = ((other_val - self_val) / self_val) * 100
            else:
                ratio = 0
                improvement = 0

            comparison["metrics_comparison"][metric] = {
                "server_a_value": self_val,
                "server_b_value": other_val,
                "ratio_b_over_a": ratio,
                "improvement_percent": improvement
            }

        return comparison

# Funções auxiliares para análise estatística
def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> tuple:
    """
    Calcula intervalo de confiança para uma lista de dados

    Args:
        data: Lista de valores numéricos
        confidence: Nível de confiança (padrão: 95%)

    Returns:
        Tupla (lower_bound, upper_bound)
    """
    if len(data) < 2:
        return (data[0], data[0]) if data else (0, 0)

    mean = statistics.mean(data)
    std = statistics.stdev(data)
    n = len(data)

    # Valor z para confiança de 95% (aproximadamente 1.96)
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_scores.get(confidence, 1.96)

    margin_error = z * (std / math.sqrt(n))

    return (mean - margin_error, mean + margin_error)

def analyze_performance_trends(metrics_list: List[PerformanceMetrics]) -> Dict[str, Any]:
    """
    Analisa tendências de performance ao longo de múltiplos testes

    Args:
        metrics_list: Lista de objetos PerformanceMetrics

    Returns:
        Dict com análise de tendências
    """
    if not metrics_list:
        return {}

    throughputs = []
    latencies = []
    success_rates = []

    for m in metrics_list:
        calc_metrics = m.calculate_metrics()
        throughputs.append(calc_metrics["throughput_rps"])
        latencies.append(calc_metrics["mean_latency_ms"])
        success_rates.append(calc_metrics["success_rate"])

    return {
        "throughput_trend": {
            "mean": statistics.mean(throughputs),
            "std": statistics.stdev(throughputs) if len(throughputs) > 1 else 0,
            "min": min(throughputs),
            "max": max(throughputs),
            "confidence_interval_95": calculate_confidence_interval(throughputs)
        },
        "latency_trend": {
            "mean": statistics.mean(latencies),
            "std": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "min": min(latencies),
            "max": max(latencies),
            "confidence_interval_95": calculate_confidence_interval(latencies)
        },
        "success_rate_trend": {
            "mean": statistics.mean(success_rates),
            "std": statistics.stdev(success_rates) if len(success_rates) > 1 else 0,
            "min": min(success_rates),
            "max": max(success_rates)
        },
        "num_tests": len(metrics_list)
    }

# Teste das métricas
if __name__ == "__main__":
    # Exemplo de uso
    pm = PerformanceMetrics()
    pm.start_test()

    # Simular algumas requisições
    for i in range(10):
        latency = 0.1 + (i * 0.01)  # Latência crescente para teste
        req = RequestMetrics(
            request_id=i,
            start_time=time.time(),
            end_time=time.time() + latency,
            response_time=latency,
            status_code=200,
            success=True,
            server_type="sequential"
        )
        pm.add_request(req)

    pm.end_test()

    # Mostrar relatório
    print(pm.get_summary_report())

    # Exportar para JSON
    pm.export_to_json("test_metrics.json")
