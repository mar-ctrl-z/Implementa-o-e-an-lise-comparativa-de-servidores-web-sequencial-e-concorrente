# Configurações do projeto
# Substitua pelos seus dados pessoais

# Dados do aluno
MATRICULA = "5217"  # Últimos 4 dígitos da matrícula: 20229035217
NOME_ALUNO = "Marina Conrado Moreira Santos"  # Nome completo

# Configurações de rede baseadas na matrícula
# Formato: XX.YY.AA.BB onde AA.BB são os 4 últimos algarismos
# Exemplo: se matrícula termina com 1234, então IPs serão 54.99.12.34, 54.99.12.35, etc.

# IPs calculados dinamicamente
def calcular_ips(matricula):
    """Calcula os endereços IP baseados nos 4 últimos algarismos da matrícula"""
    if len(matricula) != 4 or not matricula.isdigit():
        raise ValueError("Matrícula deve ter exatamente 4 dígitos")

    parte1 = matricula[0:2]  # primeiros 2 dígitos
    parte2 = matricula[2:4]  # últimos 2 dígitos

    # IPs no formato 54.99.AA.BB
    ip_base = f"54.99.{parte1}.{parte2}"

    return {
        'server': ip_base,
        'client1': f"54.99.{parte1}.{int(parte2)+1:02d}",
        'client2': f"54.99.{parte1}.{int(parte2)+2:02d}",
        'client3': f"54.99.{parte1}.{int(parte2)+3:02d}"
    }

# Configurações do servidor
SERVER_HOST = '0.0.0.0'  # Escuta em todas as interfaces dentro do container
SERVER_PORT = 80

# Configurações do cliente (para testes)
CLIENT_HOST = 'localhost'  # Host para conectar nos testes
CLIENT_PORT_SEQ = 80       # Porta do servidor sequencial
CLIENT_PORT_CONC = 8080    # Porta do servidor concorrente

# Configurações de criptografia
HASH_ALGORITHM = 'sha1'  # ou 'md5'

# Timeout para conexões (segundos)
CONNECTION_TIMEOUT = 30

# Configurações de teste
TEST_ITERATIONS = 10  # mínimo 10 execuções por cenário
MAX_CLIENTS = 50      # número máximo de clientes para testes de carga
