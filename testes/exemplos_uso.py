"""
Exemplo de uso direto do cliente HTTP
Execute este script dentro do container de teste
"""
import sys
import os
import time

# Adiciona o diretório src ao path
sys.path.append('/app/src')

from cliente import ClienteHTTP, TestadorCarga
from configuracao import ID_CUSTOMIZADO

def exemplo_basico():
    """Exemplo básico de uso do cliente"""
    print("=== Exemplo Básico de Uso do Cliente ===")
    
    # IPs dos servidores
    servidor_sequencial = "76.1.0.10"
    servidor_concorrente = "76.1.0.11"
    
    print(f"Custom ID configurado: {ID_CUSTOMIZADO}")
    print()
    
    # Teste do servidor sequencial
    print("1. Testando Servidor Sequencial:")
    cliente_seq = ClienteHTTP(servidor_sequencial)
    
    # Requisição simples
    resultado = cliente_seq.enviar_requisicao('GET', '/')
    if resultado['sucesso']:
        print(f"   ✓ Status: {resultado['codigo_status']}")
        print(f"   ✓ Tempo: {resultado['tempo_resposta']:.4f}s")
    else:
        print(f"   ✗ Erro: {resultado.get('erro', 'Desconhecido')}")
    
    print()
    
    # Teste do servidor concorrente
    print("2. Testando Servidor Concorrente:")
    cliente_conc = ClienteHTTP(servidor_concorrente)
    
    resultado = cliente_conc.enviar_requisicao('GET', '/')
    if resultado['sucesso']:
        print(f"   ✓ Status: {resultado['codigo_status']}")
        print(f"   ✓ Tempo: {resultado['tempo_resposta']:.4f}s")
    else:
        print(f"   ✗ Erro: {resultado.get('erro', 'Desconhecido')}")

def exemplo_endpoints():
    """Testa todos os endpoints disponíveis"""
    print("\n=== Testando Todos os Endpoints ===")
    
    servidor = "76.1.0.10"  # Servidor sequencial
    client = HTTPClient(servidor)
    
    endpoints = [
        ('GET', '/'),
        ('GET', '/status'),
        ('GET', '/fast'),
        ('GET', '/medium'),
        ('GET', '/slow'),
        ('POST', '/data')
    ]
    
    for method, path in endpoints:
        print(f"\nTestando {method} {path}:")
        resultado = client.send_request(method, path)
        
        if resultado['success']:
            print(f"   ✓ Status: {resultado['status_code']}")
            print(f"   ✓ Tempo: {resultado['response_time']:.4f}s")
            
            # Mostra parte da resposta
            if resultado['body']:
                try:
                    import json
                    data = json.loads(resultado['body'])
                    print(f"   ✓ Tipo de servidor: {data.get('server_type', 'N/A')}")
                    print(f"   ✓ Mensagem: {data.get('message', 'N/A')[:50]}...")
                except:
                    print(f"   ✓ Resposta: {resultado['body'][:50]}...")
        else:
            print(f"   ✗ Erro: {resultado.get('error', 'Desconhecido')}")

def exemplo_teste_carga():
    """Exemplo de teste de carga simples"""
    print("\n=== Exemplo de Teste de Carga ===")
    
    servidor_seq = "76.1.0.10"
    servidor_conc = "76.1.0.11"
    
    # Teste simples com poucos clientes
    num_clientes = 3
    requisicoes_por_cliente = 2
    
    print(f"Teste: {num_clientes} clientes, {requisicoes_por_cliente} requisições cada")
    
    # Testa servidor sequencial
    print("\n1. Servidor Sequencial:")
    tester_seq = LoadTester(servidor_seq)
    resultado_seq = tester_seq.concurrent_test(
        num_clientes, requisicoes_por_cliente, 'GET', '/fast'
    )
    
    print(f"   Tempo total: {resultado_seq['total_time']:.2f}s")
    print(f"   Taxa de sucesso: {resultado_seq['summary']['success_rate']:.2%}")
    print(f"   Tempo médio: {resultado_seq['summary']['avg_response_time']:.4f}s")
    
    # Pequena pausa
    time.sleep(2)
    
    # Testa servidor concorrente
    print("\n2. Servidor Concorrente:")
    tester_conc = LoadTester(servidor_conc)
    resultado_conc = tester_conc.concurrent_test(
        num_clientes, requisicoes_por_cliente, 'GET', '/fast'
    )
    
    print(f"   Tempo total: {resultado_conc['total_time']:.2f}s")
    print(f"   Taxa de sucesso: {resultado_conc['summary']['success_rate']:.2%}")
    print(f"   Tempo médio: {resultado_conc['summary']['avg_response_time']:.4f}s")
    
    # Comparação
    if (resultado_seq['summary']['avg_response_time'] > 0 and 
        resultado_conc['summary']['avg_response_time'] > 0):
        
        speedup = resultado_seq['summary']['avg_response_time'] / resultado_conc['summary']['avg_response_time']
        print(f"\n3. Comparação:")
        if speedup > 1:
            print(f"   → Servidor concorrente foi {speedup:.2f}x mais rápido")
        else:
            print(f"   → Servidor sequencial foi {1/speedup:.2f}x mais rápido")

def exemplo_comparacao_cenarios():
    """Compara diferentes cenários de processamento"""
    print("\n=== Comparação de Cenários ===")
    
    servidor = "76.1.0.11"  # Servidor concorrente
    client = HTTPClient(servidor)
    
    cenarios = [
        ('/fast', 'Processamento Rápido'),
        ('/medium', 'Processamento Médio'),
        ('/slow', 'Processamento Lento')
    ]
    
    for path, nome in cenarios:
        print(f"\n{nome} ({path}):")
        
        # Faz 3 requisições para calcular média
        tempos = []
        for i in range(3):
            resultado = client.send_request('GET', path)
            if resultado['success']:
                tempos.append(resultado['response_time'])
            time.sleep(0.5)
        
        if tempos:
            tempo_medio = sum(tempos) / len(tempos)
            print(f"   Tempo médio: {tempo_medio:.4f}s")
            print(f"   Min/Max: {min(tempos):.4f}s / {max(tempos):.4f}s")
        else:
            print("   ✗ Falha nos testes")

if __name__ == "__main__":
    print("=== Exemplos de Uso do Cliente HTTP ===")
    print("Executando dentro do container de teste...")
    print()
    
    try:
        exemplo_basico()
        exemplo_endpoints()
        exemplo_teste_carga()
        exemplo_comparacao_cenarios()
        
        print("\n=== Exemplos Concluídos ===")
        print("Para testes mais completos, execute:")
        print("  python3 tests/automated_tests.py --full")
        
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário")
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        print("Verifique se os servidores estão rodando:")
