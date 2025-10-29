#!/usr/bin/env python3
"""
Servidor Web Concorrente com Threads
Implementa um servidor web que processa múltiplas requisições simultaneamente usando threads
"""

import socket
import sys
import signal
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import queue

# Importar módulos do projeto
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from core.http_utils import HTTPRequest, validate_http_request, create_error_response
from core.server_handlers import get_handlers

class ConcurrentWebServer:
    """Servidor web concorrente que processa múltiplas requisições simultaneamente"""

    def __init__(self, host=config.SERVER_HOST, port=config.SERVER_PORT, max_workers=10):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.server_socket = None
        self.running = False
        self.executor = None
        self.handlers = get_handlers()

        # Estatísticas thread-safe
        self.stats_lock = threading.Lock()
        self.requests_processed = 0
        self.errors_count = 0
        self.active_connections = 0
        self.start_time = None

        # Fila para controlar conexões ativas
        self.connection_queue = queue.Queue(maxsize=max_workers * 2)

        # Configurar signal handler para graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        print(f"\nRecebido sinal {signum}. Encerrando servidor...")
        self.stop()

    def start(self):
        """Inicia o servidor"""
        try:
            # Criar socket TCP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind na porta
            self.server_socket.bind((self.host, self.port))

            # Listen por conexões
            self.server_socket.listen(self.max_workers * 2)
            self.running = True
            self.start_time = time.time()

            # Criar pool de threads
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="Worker")

            print(f"🚀 Servidor Concorrente iniciado em {self.host}:{self.port}")
            print(f"📊 Workers: {self.max_workers}")
            print(f"📅 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("⏹️  Pressione Ctrl+C para parar\n")

            self._run_server_loop()

        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
            self.stop()
            sys.exit(1)

    def stop(self):
        """Para o servidor"""
        self.running = False

        if self.executor:
            self.executor.shutdown(wait=True)

        if self.server_socket:
            self.server_socket.close()

        print("✅ Servidor concorrente encerrado")

    def _run_server_loop(self):
        """Loop principal do servidor concorrente"""
        while self.running:
            try:
                # Aguardar conexão (não bloqueante devido ao timeout)
                self.server_socket.settimeout(1.0)
                client_socket, client_address = self.server_socket.accept()

                # Incrementar contador de conexões ativas
                with self.stats_lock:
                    self.active_connections += 1

                print(f"📥 Conexão aceita de {client_address[0]}:{client_address[1]} (ativas: {self.active_connections})")

                # Submeter tarefa para o pool de threads
                future = self.executor.submit(self._handle_client, client_socket, client_address)

                # Adicionar callback para decrementar contador quando terminar
                future.add_done_callback(lambda f: self._decrement_active_connections())

            except socket.timeout:
                # Timeout normal, continuar loop
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro no loop do servidor: {e}")
                with self.stats_lock:
                    self.errors_count += 1

    def _decrement_active_connections(self):
        """Decrementa contador de conexões ativas (thread-safe)"""
        with self.stats_lock:
            self.active_connections = max(0, self.active_connections - 1)

    def _handle_client(self, client_socket, client_address):
        """Processa uma requisição de cliente (executada em thread separada)"""
        try:
            # Configurar timeout para a conexão
            client_socket.settimeout(config.CONNECTION_TIMEOUT)

            # Receber dados da requisição
            request_data = self._receive_request(client_socket)

            if not request_data:
                print(f"❌ Requisição vazia de {client_address[0]} (thread: {threading.current_thread().name})")
                return

            # Parse da requisição HTTP
            request = HTTPRequest(request_data)

            # Log da requisição
            thread_name = threading.current_thread().name
            print(f"📨 [{thread_name}] {request.method} {request.path} - X-Custom-ID: {request.get_custom_id_status()}")

            # Validar requisição
            if not request.is_valid():
                if not request.valid:
                    print(f"❌ [{thread_name}] Requisição HTTP inválida de {client_address[0]}")
                    response = create_error_response(400, "Requisição HTTP inválida")
                elif not request.custom_id_valid:
                    print(f"❌ [{thread_name}] X-Custom-ID inválido de {client_address[0]}")
                    response = create_error_response(401, "X-Custom-ID inválido ou ausente")
                else:
                    response = create_error_response(400, "Requisição inválida")
            else:
                # Processar requisição válida
                response = self.handlers.process_request(request)
                with self.stats_lock:
                    self.requests_processed += 1
                print(f"✅ [{thread_name}] Resposta: {response.status_code} {response.status_message}")

            # Enviar resposta
            self._send_response(client_socket, response)

        except socket.timeout:
            thread_name = threading.current_thread().name
            print(f"⏰ [{thread_name}] Timeout na conexão com {client_address[0]}")
        except Exception as e:
            thread_name = threading.current_thread().name
            print(f"Erro [{thread_name}] ao processar cliente {client_address[0]}: {e}")
            with self.stats_lock:
                self.errors_count += 1
            try:
                error_response = create_error_response(500, "Erro interno do servidor")
                self._send_response(client_socket, error_response)
            except:
                pass
        finally:
            # Fechar conexão do cliente
            try:
                client_socket.close()
            except:
                pass

    def _receive_request(self, client_socket):
        """Recebe dados da requisição HTTP"""
        request_data = b""
        client_socket.settimeout(5.0)  # Timeout para receber headers

        try:
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break

                request_data += chunk

                # Verificar se recebemos headers completos
                if b'\r\n\r\n' in request_data:
                    # Verificar se há Content-Length para ler o body
                    headers_end = request_data.find(b'\r\n\r\n')
                    headers = request_data[:headers_end].decode('utf-8', errors='ignore')

                    content_length = 0
                    for line in headers.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            try:
                                content_length = int(line.split(':')[1].strip())
                            except:
                                pass
                            break

                    # Se temos Content-Length, aguardar pelo body completo
                    if content_length > 0:
                        body_received = len(request_data) - (headers_end + 4)
                        while body_received < content_length:
                            chunk = client_socket.recv(1024)
                            if not chunk:
                                break
                            request_data += chunk
                            body_received += len(chunk)

                    break

        except socket.timeout:
            pass
        except Exception as e:
            thread_name = threading.current_thread().name
            print(f"Erro [{thread_name}] ao receber dados: {e}")

        return request_data.decode('utf-8', errors='ignore') if request_data else ""

    def _send_response(self, client_socket, response):
        """Envia resposta HTTP para o cliente"""
        try:
            response_bytes = response.to_bytes()
            client_socket.sendall(response_bytes)
        except Exception as e:
            thread_name = threading.current_thread().name
            print(f"Erro [{thread_name}] ao enviar resposta: {e}")

    def get_stats(self):
        """Retorna estatísticas do servidor (thread-safe)"""
        with self.stats_lock:
            uptime = time.time() - self.start_time if self.start_time else 0
            return {
                "server_type": "concurrent",
                "requests_processed": self.requests_processed,
                "errors_count": self.errors_count,
                "active_connections": self.active_connections,
                "max_workers": self.max_workers,
                "uptime": uptime,
                "requests_per_second": self.requests_processed / uptime if uptime > 0 else 0
            }

def main():
    """Função principal"""
    print("🌐 Servidor Web Concorrente com Threads")
    print("=" * 50)

    # Configurar número de workers baseado na CPU
    import multiprocessing
    max_workers = min(multiprocessing.cpu_count() * 2, 20)  # Máximo 20 workers

    server = ConcurrentWebServer(max_workers=max_workers)
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        stats = server.get_stats()
        print("\n📊 Estatísticas Finais:")
        print(f"   Requisições processadas: {stats['requests_processed']}")
        print(f"   Erros: {stats['errors_count']}")
        print(f"   Conexões ativas: {stats['active_connections']}")
        print(f"   Workers: {stats['max_workers']}")
        print(".2f")
        print(".2f")

if __name__ == "__main__":
    main()
