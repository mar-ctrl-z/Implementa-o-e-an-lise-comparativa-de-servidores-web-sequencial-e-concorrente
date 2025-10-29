#!/usr/bin/env python3
"""
Utilitários para manipulação de mensagens HTTP
Implementa parsing de requisições e construção de respostas HTTP
"""

import re
from datetime import datetime
from .crypto_utils import validar_custom_id, gerar_custom_id

class HTTPRequest:
    """Classe para representar uma requisição HTTP"""

    def __init__(self, raw_request):
        self.raw_request = raw_request
        self.method = None
        self.path = None
        self.version = None
        self.headers = {}
        self.body = None
        self.valid = False
        self.custom_id_valid = False

        self._parse_request()

    def _parse_request(self):
        """Parse da requisição HTTP bruta"""
        try:
            lines = self.raw_request.split('\r\n')

            if not lines:
                return

            # Parse da linha de requisição
            request_line = lines[0].strip()
            parts = request_line.split()
            if len(parts) >= 3:
                self.method = parts[0].upper()
                self.path = parts[1]
                self.version = parts[2]

            # Parse dos headers
            header_lines = []
            body_start = 0

            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '':
                    body_start = i + 1
                    break
                header_lines.append(line)

            # Processar headers
            for header_line in header_lines:
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    self.headers[key.strip().lower()] = value.strip()

            # Parse do body
            if body_start < len(lines):
                self.body = '\r\n'.join(lines[body_start:])

            # Validar requisição básica
            self.valid = (self.method in ['GET', 'POST', 'HEAD'] and
                         self.path and
                         self.version)

            # Validar X-Custom-ID
            if 'x-custom-id' in self.headers:
                self.custom_id_valid = validar_custom_id(self.headers['x-custom-id'])
            else:
                self.custom_id_valid = False

        except Exception as e:
            print(f"Erro ao parsear requisição: {e}")
            self.valid = False

    def is_valid(self):
        """Verifica se a requisição é válida"""
        return self.valid and self.custom_id_valid

    def get_custom_id_status(self):
        """Retorna status do X-Custom-ID"""
        if 'x-custom-id' not in self.headers:
            return "MISSING"
        elif self.custom_id_valid:
            return "VALID"
        else:
            return "INVALID"

class HTTPResponse:
    """Classe para construir respostas HTTP"""

    def __init__(self, status_code=200, status_message="OK"):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = {
            'Server': 'Python-Web-Server/1.0',
            'Date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Connection': 'close',
            'Content-Type': 'text/html; charset=utf-8'
        }
        self.body = ""

    def set_header(self, key, value):
        """Define um header"""
        self.headers[key] = value

    def set_body(self, content, content_type='text/html; charset=utf-8'):
        """Define o corpo da resposta"""
        self.body = content
        self.set_header('Content-Type', content_type)
        self.set_header('Content-Length', str(len(content.encode('utf-8'))))

    def set_json_body(self, data):
        """Define corpo como JSON"""
        import json
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        self.set_body(json_content, 'application/json; charset=utf-8')

    def to_bytes(self):
        """Converte a resposta para bytes"""
        # Linha de status
        response_lines = [f"HTTP/1.1 {self.status_code} {self.status_message}"]

        # Headers
        for key, value in self.headers.items():
            response_lines.append(f"{key}: {value}")

        # Linha em branco
        response_lines.append("")

        # Body
        if self.body:
            response_lines.append(self.body)

        return '\r\n'.join(response_lines).encode('utf-8')

def create_error_response(status_code, message=None):
    """Cria uma resposta de erro padrão"""
    status_messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error"
    }

    status_message = status_messages.get(status_code, "Unknown Error")

    response = HTTPResponse(status_code, status_message)

    if message:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error {status_code}</title></head>
        <body>
            <h1>Error {status_code}: {status_message}</h1>
            <p>{message}</p>
        </body>
        </html>
        """
        response.set_body(error_html)
    else:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error {status_code}</title></head>
        <body>
            <h1>Error {status_code}: {status_message}</h1>
        </body>
        </html>
        """
        response.set_body(error_html)

    return response

def create_success_response(content="OK", content_type='text/html; charset=utf-8'):
    """Cria uma resposta de sucesso"""
    response = HTTPResponse(200, "OK")
    response.set_body(content, content_type)
    return response

def validate_http_request(raw_request):
    """
    Função auxiliar para validar uma requisição HTTP
    Retorna (is_valid, custom_id_status, parsed_request)
    """
    parsed = HTTPRequest(raw_request)
    return parsed.is_valid(), parsed.get_custom_id_status(), parsed

# Teste das classes
if __name__ == "__main__":
    # Teste de requisição
    test_request = """GET / HTTP/1.1\r
Host: localhost\r
X-Custom-ID: 28eb7dd540947b6293030206534bb85faf9f7cc2\r
User-Agent: TestClient/1.0\r
\r
"""

    req = HTTPRequest(test_request)
    print(f"Método: {req.method}")
    print(f"Path: {req.path}")
    print(f"Válida: {req.is_valid()}")
    print(f"X-Custom-ID Status: {req.get_custom_id_status()}")

    # Teste de resposta
    response = create_success_response("<h1>Olá Mundo!</h1>")
    print("\nResposta HTTP:")
    print(response.to_bytes().decode('utf-8', errors='replace'))
