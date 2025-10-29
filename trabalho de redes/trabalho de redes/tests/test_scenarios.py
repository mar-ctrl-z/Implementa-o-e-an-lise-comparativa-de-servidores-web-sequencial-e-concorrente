#!/usr/bin/env python3
"""
Cenários de Teste para Avaliação de Performance
Define diferentes cenários para comparar servidores sequencial e concorrente
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass

class LoadType(Enum):
    """Tipos de carga para testes"""
    LIGHT = "light"       # Carga leve (poucos clientes)
    MEDIUM = "medium"     # Carga média
    HEAVY = "heavy"       # Carga pesada (muitos clientes)

class RequestType(Enum):
    """Tipos de requisição"""
    FAST = "fast"         # Requisições rápidas (pequenos dados)
    SLOW = "slow"         # Requisições lentas (grandes dados/simulação processamento)
    MIXED = "mixed"       # Mix de requisições rápidas e lentas

@dataclass
class TestScenario:
    """Define um cenário de teste completo"""
    name: str
    description: str
    load_type: LoadType
    request_type: RequestType
    num_clients: int
    requests_per_client: int
    delay_between_requests: float  # segundos
    server_simulation_delay: float  # segundos (simulação de processamento no servidor)

    @property
    def total_requests(self) -> int:
        """Total de requisições no cenário"""
        return self.num_clients * self.requests_per_client

    @property
    def expected_duration(self) -> float:
        """Duração esperada do teste (aproximada)"""
        return self.requests_per_client * self.delay_between_requests * self.num_clients

class TestScenarios:
    """Gerenciador de cenários de teste"""

    def __init__(self):
        self.scenarios = self._define_scenarios()

    def _define_scenarios(self) -> Dict[str, TestScenario]:
        """Define todos os cenários de teste"""

        scenarios = {}

        # === CENÁRIOS DE CARGA LEVE ===
        scenarios["light_fast"] = TestScenario(
            name="Carga Leve - Requisições Rápidas",
            description="Cenário com poucos clientes fazendo requisições rápidas (GET /)",
            load_type=LoadType.LIGHT,
            request_type=RequestType.FAST,
            num_clients=3,
            requests_per_client=20,
            delay_between_requests=0.1,  # 100ms entre requisições
            server_simulation_delay=0.001  # 1ms de processamento simulado
        )

        scenarios["light_slow"] = TestScenario(
            name="Carga Leve - Requisições Lentas",
            description="Cenário com poucos clientes fazendo requisições que exigem processamento",
            load_type=LoadType.LIGHT,
            request_type=RequestType.SLOW,
            num_clients=3,
            requests_per_client=10,
            delay_between_requests=0.5,  # 500ms entre requisições
            server_simulation_delay=0.1  # 100ms de processamento simulado
        )

        # === CENÁRIOS DE CARGA MÉDIA ===
        scenarios["medium_fast"] = TestScenario(
            name="Carga Média - Requisições Rápidas",
            description="Cenário com número moderado de clientes fazendo requisições rápidas",
            load_type=LoadType.MEDIUM,
            request_type=RequestType.FAST,
            num_clients=10,
            requests_per_client=30,
            delay_between_requests=0.05,  # 50ms entre requisições
            server_simulation_delay=0.001  # 1ms de processamento simulado
        )

        scenarios["medium_slow"] = TestScenario(
            name="Carga Média - Requisições Lentas",
            description="Cenário com número moderado de clientes fazendo requisições que exigem processamento",
            load_type=LoadType.MEDIUM,
            request_type=RequestType.SLOW,
            num_clients=8,
            requests_per_client=15,
            delay_between_requests=0.2,  # 200ms entre requisições
            server_simulation_delay=0.05  # 50ms de processamento simulado
        )

        scenarios["medium_mixed"] = TestScenario(
            name="Carga Média - Requisições Mistas",
            description="Cenário com clientes fazendo mix de requisições rápidas e lentas",
            load_type=LoadType.MEDIUM,
            request_type=RequestType.MIXED,
            num_clients=12,
            requests_per_client=25,
            delay_between_requests=0.1,  # 100ms entre requisições
            server_simulation_delay=0.02  # 20ms de processamento médio simulado
        )

        # === CENÁRIOS DE CARGA PESADA ===
        scenarios["heavy_fast"] = TestScenario(
            name="Carga Pesada - Requisições Rápidas",
            description="Cenário de stress com muitos clientes fazendo requisições rápidas",
            load_type=LoadType.HEAVY,
            request_type=RequestType.FAST,
            num_clients=25,
            requests_per_client=40,
            delay_between_requests=0.01,  # 10ms entre requisições
            server_simulation_delay=0.001  # 1ms de processamento simulado
        )

        scenarios["heavy_slow"] = TestScenario(
            name="Carga Pesada - Requisições Lentas",
            description="Cenário de stress com muitos clientes fazendo requisições que exigem processamento",
            load_type=LoadType.HEAVY,
            request_type=RequestType.SLOW,
            num_clients=20,
            requests_per_client=20,
            delay_between_requests=0.1,  # 100ms entre requisições
            server_simulation_delay=0.08  # 80ms de processamento simulado
        )

        scenarios["heavy_mixed"] = TestScenario(
            name="Carga Pesada - Requisições Mistas",
            description="Cenário de stress com muitos clientes fazendo mix de requisições",
            load_type=LoadType.HEAVY,
            request_type=RequestType.MIXED,
            num_clients=30,
            requests_per_client=35,
            delay_between_requests=0.05,  # 50ms entre requisições
            server_simulation_delay=0.03  # 30ms de processamento médio simulado
        )

        # === CENÁRIOS ESPECIAIS ===
        scenarios["burst_load"] = TestScenario(
            name="Carga em Burst",
            description="Cenário simulando picos de carga repentinos",
            load_type=LoadType.HEAVY,
            request_type=RequestType.FAST,
            num_clients=50,
            requests_per_client=100,
            delay_between_requests=0.001,  # 1ms entre requisições (muito rápido)
            server_simulation_delay=0.001  # Processamento mínimo
        )

        scenarios["sequential_vs_concurrent"] = TestScenario(
            name="Comparação Direta",
            description="Cenário otimizado para comparar diretamente sequencial vs concorrente",
            load_type=LoadType.MEDIUM,
            request_type=RequestType.MIXED,
            num_clients=15,
            requests_per_client=50,
            delay_between_requests=0.02,  # 20ms entre requisições
            server_simulation_delay=0.01  # 10ms de processamento simulado
        )

        return scenarios

    def get_scenario(self, scenario_id: str) -> TestScenario:
        """Retorna um cenário específico"""
        return self.scenarios.get(scenario_id)

    def get_all_scenarios(self) -> List[TestScenario]:
        """Retorna todos os cenários"""
        return list(self.scenarios.values())

    def get_scenarios_by_load(self, load_type: LoadType) -> List[TestScenario]:
        """Retorna cenários por tipo de carga"""
        return [s for s in self.scenarios.values() if s.load_type == load_type]

    def get_scenarios_by_request_type(self, request_type: RequestType) -> List[TestScenario]:
        """Retorna cenários por tipo de requisição"""
        return [s for s in self.scenarios.values() if s.request_type == request_type]

    def get_recommended_scenarios(self) -> List[str]:
        """
        Retorna IDs dos cenários recomendados para avaliação completa
        (equilibra tempo de teste com qualidade dos resultados)
        """
        return [
            "light_fast",      # Baseline simples
            "medium_mixed",    # Cenário equilibrado
            "heavy_fast",      # Teste de throughput
            "heavy_slow",      # Teste de carga com processamento
            "sequential_vs_concurrent"  # Comparação direta
        ]

class TestConfiguration:
    """Configuração geral dos testes"""

    # Configurações padrão
    DEFAULT_ITERATIONS = 10  # Mínimo 10 execuções por cenário
    WARMUP_REQUESTS = 5      # Requisições de aquecimento
    TIMEOUT_SECONDS = 30     # Timeout para requisições individuais

    # Configurações de relatório
    EXPORT_RESULTS = True
    GENERATE_PLOTS = True

    # Configurações de ambiente
    SERVER_HOST = "localhost"
    SERVER_PORT = 80

    # Cenários ativos (podem ser modificados)
    ACTIVE_SCENARIOS = [
        "light_fast",
        "light_slow",
        "medium_fast",
        "medium_slow",
        "medium_mixed",
        "heavy_fast",
        "heavy_slow",
        "heavy_mixed"
    ]

def print_scenarios_summary():
    """Imprime resumo de todos os cenários disponíveis"""
    scenarios_manager = TestScenarios()

    print("🎯 CENÁRIOS DE TESTE DISPONÍVEIS")
    print("=" * 80)

    for scenario_id, scenario in scenarios_manager.scenarios.items():
        print(f"\n📋 {scenario_id.upper()}")
        print(f"   Nome: {scenario.name}")
        print(f"   Descrição: {scenario.description}")
        print(f"   Carga: {scenario.load_type.value.upper()}")
        print(f"   Tipo: {scenario.request_type.value.upper()}")
        print(f"   Clientes: {scenario.num_clients}")
        print(f"   Requisições/cliente: {scenario.requests_per_client}")
        print(f"   Total de requisições: {scenario.total_requests}")
        print(f"   Delay entre reqs: {scenario.delay_between_requests*1000:.0f}ms")
        print(f"   Processamento simulado: {scenario.server_simulation_delay*1000:.0f}ms")
        print(f"   Duração esperada: ~{scenario.expected_duration:.1f}s")

    print("\n🎯 CENÁRIOS RECOMENDADOS PARA AVALIAÇÃO:")
    print("-" * 50)
    for scenario_id in scenarios_manager.get_recommended_scenarios():
        scenario = scenarios_manager.get_scenario(scenario_id)
        print(f"• {scenario_id}: {scenario.name}")

    print("\n📊 ESTRATÉGIA DE TESTE:")
    print("-" * 50)
    print("• Cada cenário será executado 10 vezes (mínimo exigido)")
    print("• Serão testados ambos os servidores (sequencial e concorrente)")
    print("• Métricas coletadas: latência, throughput, taxa de erro")
    print("• Análise estatística: média e desvio padrão")
    print("• Geração de gráficos comparativos")

if __name__ == "__main__":
    print_scenarios_summary()
