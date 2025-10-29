#!/usr/bin/env python3
"""
Servidor Web Sequencial Síncrono
Implementa um servidor web básico que processa uma requisição por vez
"""

import socket
import sys
import signal
import time
from datetime import datetime

# Importar módulos do projeto
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from core.http_utils import HTTPRequest, validate_http_request, create_error_response
from core.server_handlers import get_handlers

class SequentialWebServer:
    """Servidor web sequencial que processa uma requisição por vez"""

    def __init__(self, host=config.SERVER_HOST, port=config.SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.handlers = get_handlers()

        # Estatísticas
        self.requests_processed = 0
        self.errors_count = 0
        self.start_time = None

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
            self.server_socket.listen(5)
            self.running = True
            self.start_time = time.time()

            print(f"🚀 Servidor Sequencial iniciado em {self.host}:{self.port}")
            print(f"📊 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("⏹️  Pressione Ctrl+C para parar\n")

            self._run_server_loop()

        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
            self.stop()
            sys.exit(1)

    def stop(self):
        """Para o servidor"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("✅ Servidor encerrado")

    def _run_server_loop(self):
        """Loop principal do servidor sequencial"""
        while self.running:
            try:
                # Aguardar conexão (bloqueante)
                client_socket, client_address = self.server_socket.accept()
                print(f"📥 Conexão aceita de {client_address[0]}:{client_address[1]}")

                # Processar requisição (sequencial - uma por vez)
                self._handle_client(client_socket, client_address)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Erro no loop do servidor: {e}")
                self.errors_count += 1

    def _handle_client(self, client_socket, client_address):
        """Processa uma requisição de cliente"""
        try:
            # Configurar timeout para a conexão
            client_socket.settimeout(config.CONNECTION_TIMEOUT)

            # Receber dados da requisição
            request_data = self._receive_request(client_socket)

            if not request_data:
                print(f"❌ Requisição vazia de {client_address[0]}")
                return

            # Parse da requisição HTTP
            request = HTTPRequest(request_data)

            # Log da requisição
            print(f"📨 {request.method} {request.path} - X-Custom-ID: {request.get_custom_id_status()}")

            # Validar requisição
            if not request.is_valid():
                if not request.valid:
                    print(f"❌ Requisição HTTP inválida de {client_address[0]}")
                    response = create_error_response(400, "Requisição HTTP inválida")
                elif not request.custom_id_valid:
                    print(f"❌ X-Custom-ID inválido de {client_address[0]}")
                    response = create_error_response(401, "X-Custom-ID inválido ou ausente")
                else:
                    response = create_error_response(400, "Requisição inválida")
            else:
                # Processar requisição válida
                response = self.handlers.process_request(request)
                self.requests_processed += 1
                print(f"✅ Resposta: {response.status_code} {response.status_message}")

            # Enviar resposta
            self._send_response(client_socket, response)

        except socket.timeout:
            print(f"⏰ Timeout na conexão com {client_address[0]}")
        except Exception as e:
            print(f"Erro ao processar cliente {client_address[0]}: {e}")
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
            print(f"Erro ao receber dados: {e}")

        return request_data.decode('utf-8', errors='ignore') if request_data else ""

    def _send_response(self, client_socket, response):
        """Envia resposta HTTP para o cliente"""
        try:
            response_bytes = response.to_bytes()
            client_socket.sendall(response_bytes)
        except Exception as e:
            print(f"Erro ao enviar resposta: {e}")

    def get_stats(self):
        """Retorna estatísticas do servidor"""
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            "server_type": "sequential",
            "requests_processed": self.requests_processed,
            "errors_count": self.errors_count,
            "uptime": uptime,
            "requests_per_second": self.requests_processed / uptime if uptime > 0 else 0
        }

def main():
    """Função principal"""
    print("🌐 Servidor Web Sequencial")
    print("=" * 50)

    server = SequentialWebServer()
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
        print(".2f")
        print(".2f")

if __name__ == "__main__":
    main()
