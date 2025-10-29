#!/usr/bin/env python3
"""
Utilitários criptográficos para o projeto
Implementa funções de hash MD5/SHA-1 conforme requisitos
"""

import hashlib
import config

def calcular_hash_aluno(matricula=None, nome_aluno=None, algoritmo=None):
    """
    Calcula o hash MD5 ou SHA-1 da concatenação: matrícula + " " + nome_do_aluno

    Args:
        matricula (str): Matrícula do aluno (4 últimos algarismos)
        nome_aluno (str): Nome completo do aluno
        algoritmo (str): 'md5' ou 'sha1' (padrão: config.HASH_ALGORITHM)

    Returns:
        str: Hash em formato hexadecimal

    Raises:
        ValueError: Se parâmetros forem inválidos
    """
    if matricula is None:
        matricula = config.MATRICULA
    if nome_aluno is None:
        nome_aluno = config.NOME_ALUNO
    if algoritmo is None:
        algoritmo = config.HASH_ALGORITHM

    # Validar entrada
    if not matricula or not nome_aluno:
        raise ValueError("Matrícula e nome do aluno são obrigatórios")

    if len(matricula) != 4 or not matricula.isdigit():
        raise ValueError("Matrícula deve ter exatamente 4 dígitos numéricos")

    if algoritmo not in ['md5', 'sha1']:
        raise ValueError("Algoritmo deve ser 'md5' ou 'sha1'")

    # Concatenar: matrícula + espaço + nome
    dados = f"{matricula} {nome_aluno}"

    # Calcular hash
    if algoritmo == 'md5':
        hash_obj = hashlib.md5(dados.encode('utf-8'))
    else:  # sha1
        hash_obj = hashlib.sha1(dados.encode('utf-8'))

    return hash_obj.hexdigest()

def gerar_custom_id():
    """
    Gera o valor para o cabeçalho X-Custom-ID usando o hash do aluno

    Returns:
        str: Valor do X-Custom-ID
    """
    return calcular_hash_aluno()

def validar_custom_id(custom_id):
    """
    Valida se o X-Custom-ID fornecido corresponde ao hash esperado

    Args:
        custom_id (str): Valor do cabeçalho X-Custom-ID

    Returns:
        bool: True se válido, False caso contrário
    """
    expected_id = gerar_custom_id()
    return custom_id == expected_id

# Funções auxiliares para debugging
def print_hash_info():
    """Imprime informações sobre o hash calculado para debug"""
    hash_md5 = calcular_hash_aluno(algoritmo='md5')
    hash_sha1 = calcular_hash_aluno(algoritmo='sha1')

    print("=== Informações de Hash ===")
    print(f"Matrícula: {config.MATRICULA}")
    print(f"Nome: {config.NOME_ALUNO}")
    print(f"Dados concatenados: '{config.MATRICULA} {config.NOME_ALUNO}'")
    print(f"MD5: {hash_md5}")
    print(f"SHA-1: {hash_sha1}")
    print(f"Algoritmo padrão: {config.HASH_ALGORITHM}")
    print(f"X-Custom-ID: {gerar_custom_id()}")
    print("=" * 40)

if __name__ == "__main__":
    # Para testes
    print_hash_info()
