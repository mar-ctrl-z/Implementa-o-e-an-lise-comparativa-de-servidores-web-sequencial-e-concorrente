#!/usr/bin/env python3
"""
Script principal para execução do projeto
Servidores Web Sequencial e Concorrente
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_scenarios import TestScenarios
from client.test_client import run_single_test

class ProjectRunner:
    """Gerenciador de execução do projeto"""

    def __init__(self):
        self.project_root = Path(__file__).parent

    def setup_network(self):
        """Configura a rede Docker baseada na matrícula"""
        print("🌐 Configurando rede Docker...")
        setup_script = self.project_root / "scripts" / "setup_network.py"

        if not setup_script.exists():
            print("❌ Script setup_network.py não encontrado!")
            return False

        try:
            subprocess.run([sys.executable, str(setup_script)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na configuração da rede: {e}")
            return False

    def build_containers(self):
        """Constrói os containers Docker"""
        print("🐳 Construindo containers Docker...")
        try:
            subprocess.run(["docker-compose", "build"], check=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na construção dos containers: {e}")
            return False

    def start_server(self, server_type="sequential"):
        """Inicia o servidor especificado"""
        if server_type == "sequential":
            service = "server"
        elif server_type == "concurrent":
            service = ""  # Inicia todos os serviços
        else:
            print(f"❌ Tipo de servidor inválido: {server_type}")
            return False

        print(f"🚀 Iniciando servidor {server_type}...")
        try:
            if service:
                subprocess.run(["docker-compose", "up", "-d", service],
                             check=True, cwd=self.project_root)
            else:
                subprocess.run(["docker-compose", "up", "-d"],
                             check=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False

    def stop_containers(self):
        """Para todos os containers"""
        print("⏹️  Parando containers...")
        try:
            subprocess.run(["docker-compose", "down"], check=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao parar containers: {e}")
            return False

    def run_test(self, scenario_id, server_type, output_file=None):
        """Executa um teste específico"""
        print(f"🧪 Executando teste: {scenario_id} com servidor {server_type}")

        # Verificar se cenário existe
        scenarios = TestScenarios()
        scenario = scenarios.get_scenario(scenario_id)
        if not scenario:
            print(f"❌ Cenário '{scenario_id}' não encontrado!")
            return False

        try:
            run_single_test(scenario_id, server_type, output_file)
            return True
        except Exception as e:
            print(f"❌ Erro durante teste: {e}")
            return False

    def run_full_test_suite(self, iterations=3):
        """Executa suíte completa de testes"""
        print(f"🧪 Executando suíte completa de testes ({iterations} iterações por cenário)")

        scenarios = TestScenarios()
        recommended_scenarios = scenarios.get_recommended_scenarios()
        server_types = ["sequential", "concurrent"]

        results_dir = self.project_root / "results"
        results_dir.mkdir(exist_ok=True)

        total_tests = len(recommended_scenarios) * len(server_types) * iterations
        test_count = 0

        print(f"📊 Total de testes: {total_tests}")

        for scenario_id in recommended_scenarios:
            for server_type in server_types:
                for i in range(iterations):
                    test_count += 1
                    print(f"\n🔄 Teste {test_count}/{total_tests}: {scenario_id} - {server_type} (iteração {i+1})")

                    # Iniciar servidor
                    if not self.start_server(server_type):
                        continue

                    # Aguardar servidor inicializar
                    time.sleep(2)

                    # Executar teste
                    output_file = results_dir / f"{scenario_id}_{server_type}_iter{i+1}.json"
                    success = self.run_test(scenario_id, server_type, str(output_file))

                    # Parar servidor
                    self.stop_containers()

                    if not success:
                        print(f"⚠️  Teste {scenario_id} falhou na iteração {i+1}")

        print("✅ Suíte de testes concluída!")

    def show_scenarios(self):
        """Mostra cenários disponíveis"""
        from tests.test_scenarios import print_scenarios_summary
        print_scenarios_summary()

    def clean_results(self):
        """Limpa resultados anteriores"""
        results_dir = self.project_root / "results"
        if results_dir.exists():
            for file in results_dir.glob("*.json"):
                file.unlink()
            print("🧹 Resultados anteriores limpos!")
        else:
            print("📁 Diretório de resultados não existe")

def main():
    parser = argparse.ArgumentParser(description="Servidor Web Sequencial e Concorrente")
    parser.add_argument("command", choices=[
        "setup", "build", "start", "stop", "test", "suite", "scenarios", "clean"
    ], help="Comando a executar")
    parser.add_argument("--server", choices=["sequential", "concurrent"],
                       default="sequential", help="Tipo de servidor")
    parser.add_argument("--scenario", help="ID do cenário de teste")
    parser.add_argument("--iterations", type=int, default=3,
                       help="Número de iterações para suíte de testes")
    parser.add_argument("--output", help="Arquivo de saída para resultados")

    args = parser.parse_args()

    runner = ProjectRunner()

    if args.command == "setup":
        if runner.setup_network():
            print("✅ Rede configurada com sucesso!")

    elif args.command == "build":
        if runner.build_containers():
            print("✅ Containers construídos com sucesso!")

    elif args.command == "start":
        if runner.start_server(args.server):
            print(f"✅ Servidor {args.server} iniciado!")

    elif args.command == "stop":
        if runner.stop_containers():
            print("✅ Containers parados!")

    elif args.command == "test":
        if not args.scenario:
            print("❌ Especifique --scenario para executar teste")
            sys.exit(1)

        if runner.start_server(args.server):
            time.sleep(2)  # Aguardar inicialização
            success = runner.run_test(args.scenario, args.server, args.output)
            runner.stop_containers()

            if success:
                print("✅ Teste executado com sucesso!")
            else:
                print("❌ Teste falhou!")
                sys.exit(1)

    elif args.command == "suite":
        runner.run_full_test_suite(args.iterations)

    elif args.command == "scenarios":
        runner.show_scenarios()

    elif args.command == "clean":
        runner.clean_results()

if __name__ == "__main__":
    main()
