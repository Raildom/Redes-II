"""
Configurações do projeto baseadas na matrícula 20239057601
"""
import hashlib

# Matrícula e informações do aluno
MATRICULA = "20239057601"
NOME_ALUNO = "Aluno"  # Substitua pelo seu nome

# Configuração de rede baseada nos últimos 4 dígitos da matrícula (7601)
ULTIMOS_QUATRO_DIGITOS = MATRICULA[-4:]  # 7601
BASE_SUBNET = f"{ULTIMOS_QUATRO_DIGITOS[:2]}.{ULTIMOS_QUATRO_DIGITOS[2:]}"  # 76.01

# IPs da rede Docker
NOME_REDE = "redes2_network"
SUBNET = f"{BASE_SUBNET}.0.0/16"
IP_SERVIDOR = f"{BASE_SUBNET}.0.10"
IP_BASE_CLIENTE = f"{BASE_SUBNET}.0"

# Configurações do servidor
PORTA_SERVIDOR = 8080
MAX_CONEXOES = 100

# Cabeçalho HTTP customizado
def gerar_id_customizado():
    """Gera o X-Custom-ID baseado na matrícula e nome do aluno"""
    dados = f"{MATRICULA} {NOME_ALUNO}"
    return hashlib.md5(dados.encode()).hexdigest()

ID_CUSTOMIZADO = gerar_id_customizado()

# Configurações de teste
ITERACOES_TESTE = 10
CLIENTES_TESTE = [1, 5, 10, 20, 50]
TAMANHOS_REQUISICAO = ["pequeno", "medio", "grande"]

print(f"Configuração da rede: {SUBNET}")
print(f"IP do servidor: {IP_SERVIDOR}")
print(f"Custom ID: {ID_CUSTOMIZADO}")
