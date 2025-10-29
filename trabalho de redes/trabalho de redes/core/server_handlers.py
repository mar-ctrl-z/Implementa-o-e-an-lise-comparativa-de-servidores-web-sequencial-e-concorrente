#!/usr/bin/env python3
"""
Handlers para as primitivas HTTP do servidor web
Define as funcionalidades de cada método HTTP suportado
"""

import time
import json
import os
from .http_utils import HTTPResponse, create_success_response, create_error_response
from .crypto_utils import gerar_custom_id

class HTTPHandlers:
    """Classe que define os handlers para as primitivas HTTP"""

    def __init__(self):
        # Estatísticas do servidor
        self.requests_served = 0
        self.start_time = time.time()

    def handle_get(self, request):
        """
        Handler para requisições GET

        Funcionalidades implementadas:
        - GET / : Página inicial com informações do servidor
        - GET /status : Status e estatísticas do servidor
        - GET /info : Informações do projeto
        - GET /time : Timestamp atual
        """
        self.requests_served += 1

        if request.path == "/":
            # Página inicial
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Servidor Web Python</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>Servidor Web Sequencial e Concorrente</h1>
    <h2>Projeto de Redes de Computadores II</h2>
    <p>Servidor implementado em Python usando sockets TCP</p>
    <p>Requisições atendidas: {}</p>
    <p>Tempo online: {:.2f} segundos</p>
    <h3>Endpoints Disponíveis:</h3>
    <ul>
        <li>GET / - Esta página</li>
        <li>GET /status - Status detalhado</li>
        <li>GET /info - Informações do projeto</li>
        <li>GET /time - Timestamp atual</li>
        <li>POST /echo - Echo do corpo da requisição</li>
        <li>POST /hash - Calcula hash dos dados enviados</li>
    </ul>
</body>
</html>""".format(self.requests_served, time.time() - self.start_time)

            return create_success_response(html_content)

        elif request.path == "/status":
            # Status detalhado em JSON
            status_data = {
                "server": "Python Web Server 1.0",
                "status": "running",
                "uptime": time.time() - self.start_time,
                "requests_served": self.requests_served,
                "timestamp": time.time(),
                "supported_methods": ["GET", "POST", "HEAD"],
                "endpoints": [
                    {"path": "/", "method": "GET", "description": "Página inicial"},
                    {"path": "/status", "method": "GET", "description": "Status do servidor"},
                    {"path": "/info", "method": "GET", "description": "Informações do projeto"},
                    {"path": "/time", "method": "GET", "description": "Timestamp atual"},
                    {"path": "/echo", "method": "POST", "description": "Echo do corpo"},
                    {"path": "/hash", "method": "POST", "description": "Calcula hash"}
                ]
            }
            response = HTTPResponse(200, "OK")
            response.set_json_body(status_data)
            return response

        elif request.path == "/info":
            # Informações do projeto
            info_data = {
                "project": "Servidor Web Sequencial e Concorrente",
                "course": "Redes de Computadores II",
                "technologies": ["Python", "Sockets TCP", "Docker"],
                "features": [
                    "Servidor sequencial síncrono",
                    "Servidor concorrente com threads/multiprocess",
                    "Avaliação de performance",
                    "Métricas de latência e throughput"
                ],
                "x_custom_id": gerar_custom_id()
            }
            response = HTTPResponse(200, "OK")
            response.set_json_body(info_data)
            return response

        elif request.path == "/time":
            # Timestamp atual
            time_data = {
                "timestamp": time.time(),
                "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "uptime": time.time() - self.start_time
            }
            response = HTTPResponse(200, "OK")
            response.set_json_body(time_data)
            return response

        else:
            # Página não encontrada
            return create_error_response(404, f"Path '{request.path}' não encontrado")

    def handle_post(self, request):
        """
        Handler para requisições POST

        Funcionalidades implementadas:
        - POST /echo : Retorna o corpo da requisição
        - POST /hash : Calcula hash MD5/SHA-1 do corpo
        """
        self.requests_served += 1

        if request.path == "/echo":
            # Echo do corpo da requisição
            if request.body:
                response = HTTPResponse(200, "OK")
                response.set_body(request.body, 'text/plain; charset=utf-8')
                return response
            else:
                return create_error_response(400, "Corpo da requisição vazio")

        elif request.path == "/hash":
            # Calcula hash do corpo
            import hashlib

            if not request.body:
                return create_error_response(400, "Corpo da requisição necessário para calcular hash")

            # Calcular MD5 e SHA-1
            md5_hash = hashlib.md5(request.body.encode('utf-8')).hexdigest()
            sha1_hash = hashlib.sha1(request.body.encode('utf-8')).hexdigest()

            hash_data = {
                "input": request.body,
                "md5": md5_hash,
                "sha1": sha1_hash,
                "length": len(request.body)
            }

            response = HTTPResponse(200, "OK")
            response.set_json_body(hash_data)
            return response

        else:
            # Método não permitido para este path
            return create_error_response(405, f"Método POST não suportado para '{request.path}'")

    def handle_head(self, request):
        """
        Handler para requisições HEAD
        Retorna apenas headers (sem body) como se fosse GET
        """
        self.requests_served += 1

        # Processa como GET mas remove o body
        if request.path in ["/", "/status", "/info", "/time"]:
            response = self.handle_get(request)
            response.body = ""  # Remove body para HEAD
            response.set_header('Content-Length', '0')
            return response
        else:
            response = create_error_response(404, f"Path '{request.path}' não encontrado")
            response.body = ""
            response.set_header('Content-Length', '0')
            return response

    def process_request(self, request):
        """
        Processa uma requisição HTTP e retorna a resposta apropriada
        """
        try:
            # Simular processamento (para testes de performance)
            # time.sleep(0.001)  # 1ms de processamento simulado

            if request.method == "GET":
                return self.handle_get(request)
            elif request.method == "POST":
                return self.handle_post(request)
            elif request.method == "HEAD":
                return self.handle_head(request)
            else:
                return create_error_response(405, f"Método '{request.method}' não suportado")

        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
            return create_error_response(500, "Erro interno do servidor")

# Função auxiliar para obter instância do handler
_handlers_instance = None

def get_handlers():
    """Retorna instância singleton dos handlers"""
    global _handlers_instance
    if _handlers_instance is None:
        _handlers_instance = HTTPHandlers()
    return _handlers_instance

# Mapeamento de métodos suportados
SUPPORTED_METHODS = {
    'GET': 'handle_get',
    'POST': 'handle_post',
    'HEAD': 'handle_head'
}

def is_method_supported(method):
    """Verifica se um método HTTP é suportado"""
    return method.upper() in SUPPORTED_METHODS
