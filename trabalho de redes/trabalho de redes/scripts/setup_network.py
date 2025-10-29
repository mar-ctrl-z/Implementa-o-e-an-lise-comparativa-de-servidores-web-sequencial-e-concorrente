#!/usr/bin/env python3
"""
Script para configurar a rede Docker baseada na matrícula do aluno
"""

import re
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

def atualizar_docker_compose(matricula):
    """Atualiza o docker-compose.yml com os IPs baseados na matrícula"""

    if len(matricula) != 4 or not matricula.isdigit():
        raise ValueError("Matrícula deve ter exatamente 4 dígitos")

    ips = config.calcular_ips(matricula)

    # Ler docker-compose.yml
    with open('docker-compose.yml', 'r') as f:
        content = f.read()

    # Atualizar IPs
    content = re.sub(r'ipv4_address: 172\.20\.0\.10', f"ipv4_address: {ips['server']}", content)
    content = re.sub(r'ipv4_address: 172\.20\.0\.11', f"ipv4_address: {ips['client1']}", content)
    content = re.sub(r'ipv4_address: 172\.20\.0\.12', f"ipv4_address: {ips['client2']}", content)
    content = re.sub(r'ipv4_address: 172\.20\.0\.13', f"ipv4_address: {ips['client3']}", content)

    # Atualizar subnet
    subnet = f"{ips['server'].rsplit('.', 1)[0]}.0/24"
    content = re.sub(r'subnet: 172\.20\.0\.0/16', f"subnet: {subnet}", content)

    # Escrever arquivo atualizado
    with open('docker-compose.yml', 'w') as f:
        f.write(content)

    print("Docker Compose atualizado com os seguintes IPs:")
    print(f"Servidor: {ips['server']}")
    print(f"Cliente 1: {ips['client1']}")
    print(f"Cliente 2: {ips['client2']}")
    print(f"Cliente 3: {ips['client3']}")
    print(f"Subnet: {subnet}")

if __name__ == "__main__":
    matricula = input("Digite os 4 últimos algarismos da sua matrícula: ").strip()
    atualizar_docker_compose(matricula)
