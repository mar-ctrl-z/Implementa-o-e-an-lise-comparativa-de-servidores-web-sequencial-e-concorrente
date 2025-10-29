#!/usr/bin/env python3
"""
Cliente de Teste para Servidores Web
Cliente HTTP simplificado que realiza testes de carga e mede performance
"""

import socket
import time
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from core.crypto_utils import gerar_custom_id
from tests.metrics import RequestMetrics, PerformanceMetrics
from tests.test_scenarios import TestScenarios


class SimpleHTTPClient:
    """Cliente HTTP simplificado e robusto"""
    
    def __init__(self, server_host: str = 'localhost', server_port: int = 80, client_id: int = 1):
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = client_id
        self.custom_id = gerar_custom_id()
    
    def send_request(self, method: str = 'GET', path: str = '/', body: str = '') -> Optional[Dict[str, Any]]:
        """
        Envia requisição HTTP e retorna resultado
        Cria nova conexão para cada requisição (Connection: close)
        """
        sock = None
        start_time = time.time()
        
        try:
            # Criar socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.server_host, self.server_port))
            
            # Construir requisição HTTP
            request_lines = [
                f"{method} {path} HTTP/1.1",
                f"Host: {self.server_host}:{self.server_port}",
                f"X-Custom-ID: {self.custom_id}",
                "User-Agent: SimpleTestClient/1.0",
                "Connection: close"
            ]
            
            # Adicionar Content-Length se houver body
            if body:
                body_bytes = body.encode('utf-8')
                request_lines.append(f"Content-Length: {len(body_bytes)}")
                request_lines.append("Content-Type: text/plain; charset=utf-8")
            
            # Finalizar headers e adicionar body
            request_lines.append("")
            request_lines.append(body if body else "")
            
            # Enviar requisição
            request_data = '\r\n'.join(request_lines).encode('utf-8')
            sock.sendall(request_data)
            
            # Receber resposta
            response_data = b""
            content_length = None
            headers_complete = False
            
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break  # Conexão fechada
                
                response_data += chunk
                
                # Verificar se temos headers completos
                if not headers_complete and b'\r\n\r\n' in response_data:
                    headers_complete = True
                    headers_end = response_data.find(b'\r\n\r\n')
                    headers_section = response_data[:headers_end].decode('utf-8', errors='ignore')
                    
                    # Extrair Content-Length
                    for line in headers_section.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            try:
                                content_length = int(line.split(':', 1)[1].strip())
                            except:
                                pass
                            break
                
                # Se temos Content-Length, verificar se recebemos tudo
                if content_length is not None and headers_complete:
                    headers_end = response_data.find(b'\r\n\r\n')
                    body_size = len(response_data) - (headers_end + 4)
                    if body_size >= content_length:
                        # Recebemos tudo!
                        break
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Parse da resposta
            if response_data:
                response_str = response_data.decode('utf-8', errors='ignore')
                lines = response_str.split('\r\n')
                status_line = lines[0] if lines else ""
                
                # Extrair status code
                status_code = 0
                if ' ' in status_line:
                    parts = status_line.split()
                    if len(parts) >= 2:
                        try:
                            status_code = int(parts[1])
                        except:
                            pass
                
                return {
                    'status_code': status_code,
                    'response_time': response_time,
                    'success': 200 <= status_code < 400,
                    'response_size': len(response_data),
                    'raw_response': response_str[:200]
                }
            else:
                return {
                    'status_code': 0,
                    'response_time': response_time,
                    'success': False,
                    'response_size': 0,
                    'error': 'Empty response'
                }
                
        except socket.timeout:
            return {
                'status_code': 0,
                'response_time': time.time() - start_time,
                'success': False,
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass


class LoadTestRunner:
    """Executor de testes de carga"""
    
    def __init__(self, server_host: str = 'localhost', server_port: int = 80):
        self.server_host = server_host
        self.server_port = server_port
    
    def run_scenario(self, scenario, server_type: str = "unknown") -> PerformanceMetrics:
        """
        Executa um cenário de teste específico
        
        Args:
            scenario: Objeto TestScenario
            server_type: Tipo do servidor ('sequential' ou 'concurrent')
        
        Returns:
            PerformanceMetrics com resultados
        """
        print(f"🎯 Executando cenário: {scenario.name}")
        print(f"   Tipo de servidor: {server_type}")
        print(f"   Clientes: {scenario.num_clients}")
        print(f"   Requisições/cliente: {scenario.requests_per_client}")
        print(f"   Total: {scenario.total_requests} requisições")
        
        metrics = PerformanceMetrics()
        metrics.start_test()
        
        request_id = 0
        
        # Criar clientes
        clients = []
        for i in range(scenario.num_clients):
            client = SimpleHTTPClient(self.server_host, self.server_port, i+1)
            clients.append(client)
        
        try:
            # Executar requisições para cada cliente
            for client_idx, client in enumerate(clients):
                print(f"   Cliente {client_idx+1}/{scenario.num_clients}: ", end="", flush=True)
                
                for req_idx in range(scenario.requests_per_client):
                    # Escolher tipo de requisição baseado no cenário
                    method, path, body = self._generate_request(scenario.request_type, req_idx)
                    
                    # Enviar requisição
                    start_time = time.time()
                    response = client.send_request(method, path, body)
                    end_time = time.time()
                    
                    if response:
                        # Registrar métrica
                        req_metric = RequestMetrics(
                            request_id=request_id,
                            start_time=start_time,
                            end_time=end_time,
                            response_time=response['response_time'],
                            status_code=response['status_code'],
                            success=response['success'],
                            server_type=server_type
                        )
                        metrics.add_request(req_metric)
                        
                        # Feedback visual
                        if req_idx % 10 == 0 and req_idx > 0:
                            print(f".{req_idx}", end="", flush=True)
                    
                    request_id += 1
                
                print(" ✓")
            
            metrics.end_test()
            
            # Calcular métricas ANTES de tentar usar
            calculated = metrics.calculate_metrics()
            
            print(f"Tempo total: {calculated['test_duration_seconds']:.2f}s")
            print(f"Throughput: {calculated['throughput_rps']:.2f} req/s")
            
        except KeyboardInterrupt:
            print("\n⚠️  Teste interrompido pelo usuário")
            metrics.end_test()
        except Exception as e:
            print(f"\n❌ Erro durante execução: {e}")
            metrics.end_test()
        
        return metrics
    
    def _generate_request(self, request_type: str, req_idx: int):
        """Gera uma requisição baseada no tipo"""
        if request_type == "fast":
            return ('GET', '/', '')
        elif request_type == "slow":
            return ('GET', '/status', '')
        elif request_type == "post":
            return ('POST', '/echo', f'Test data {req_idx}')
        else:  # mixed
            if req_idx % 3 == 0:
                return ('POST', '/echo', f'Data {req_idx}')
            elif req_idx % 3 == 1:
                return ('GET', '/info', '')
            else:
                return ('GET', '/', '')


def run_single_test(scenario_id: str, server_type: str, output_file: str = None):
    """
    Executa um único teste e exibe resultados
    
    Args:
        scenario_id: ID do cenário a executar
        server_type: 'sequential' ou 'concurrent'
        output_file: Arquivo para salvar resultados (opcional)
    """
    # Determinar porta baseado no tipo de servidor
    if server_type == 'sequential':
        port = 80
    elif server_type == 'concurrent':
        port = 8080
    else:
        print(f"❌ Tipo de servidor inválido: {server_type}")
        print("   Use 'sequential' ou 'concurrent'")
        return None
    
    # Buscar cenário
    test_scenarios = TestScenarios()
    scenario = test_scenarios.scenarios.get(scenario_id)
    if not scenario:
        print(f"❌ Cenário '{scenario_id}' não encontrado")
        print(f"   Cenários disponíveis: {', '.join(test_scenarios.scenarios.keys())}")
        return None
    
    # Executar teste
    runner = LoadTestRunner('localhost', port)
    metrics = runner.run_scenario(scenario, server_type)
    
    # Calcular métricas
    metrics.calculate_metrics()
    
    # Salvar resultados se especificado
    if output_file:
        metrics.export_to_json(output_file)
        print(f"📄 Resultados salvos em: {output_file}")
    
    # Mostrar relatório
    print("\n" + "="*60)
    print(metrics.get_summary_report())
    
    return metrics


if __name__ == "__main__":
    # Uso: python test_client.py <scenario_id> <server_type> [output_file]
    if len(sys.argv) < 3:
        print("Uso: python test_client.py <scenario_id> <server_type> [output_file]")
        print("Exemplo: python test_client.py light_fast sequential results.json")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    server_type = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    run_single_test(scenario_id, server_type, output_file)
