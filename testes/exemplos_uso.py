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
    cliente = ClienteHTTP(servidor)
    
    endpoints = [
        ('GET', '/'),
        ('GET', '/status'),
        ('GET', '/rapido'),
        ('GET', '/medio'),
        ('GET', '/lento'),
        ('POST', '/data')
    ]
    
    for method, path in endpoints:
        print(f"\nTestando {method} {path}:")
        resultado = cliente.enviar_requisicao(method, path)
        
        if resultado['sucesso']:
            print(f"   ✓ Status: {resultado['codigo_status']}")
            print(f"   ✓ Tempo: {resultado['tempo_resposta']:.4f}s")
            
            # Mostra parte da resposta
            if resultado['corpo']:
                try:
                    import json
                    data = json.loads(resultado['corpo'])
                    print(f"   ✓ Tipo de servidor: {data.get('tipo_servidor', 'N/A')}")
                    print(f"   ✓ Mensagem: {data.get('mensagem', 'N/A')[:50]}...")
                except:
                    print(f"   ✓ Resposta: {resultado['corpo'][:50]}...")
        else:
            print(f"   ✗ Erro: {resultado.get('erro', 'Desconhecido')}")

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
    testador_seq = TestadorCarga(servidor_seq)
    resultado_seq = testador_seq.teste_concorrente(
        num_clientes, requisicoes_por_cliente, 'GET', '/rapido'
    )
    
    print(f"   Tempo total: {resultado_seq['tempo_total']:.2f}s")
    print(f"   Taxa de sucesso: {resultado_seq['resumo']['taxa_sucesso']:.2%}")
    print(f"   Tempo médio: {resultado_seq['resumo']['tempo_resposta_medio']:.4f}s")
    
    # Pequena pausa
    time.sleep(2)
    
    # Testa servidor concorrente
    print("\n2. Servidor Concorrente:")
    testador_conc = TestadorCarga(servidor_conc)
    resultado_conc = testador_conc.teste_concorrente(
        num_clientes, requisicoes_por_cliente, 'GET', '/rapido'
    )
    
    print(f"   Tempo total: {resultado_conc['tempo_total']:.2f}s")
    print(f"   Taxa de sucesso: {resultado_conc['resumo']['taxa_sucesso']:.2%}")
    print(f"   Tempo médio: {resultado_conc['resumo']['tempo_resposta_medio']:.4f}s")
    
    # Comparação
    if (resultado_seq['resumo']['tempo_resposta_medio'] > 0 and 
        resultado_conc['resumo']['tempo_resposta_medio'] > 0):
        
        speedup = resultado_seq['resumo']['tempo_resposta_medio'] / resultado_conc['resumo']['tempo_resposta_medio']
        print(f"\n3. Comparação:")
        if speedup > 1:
            print(f"   → Servidor concorrente foi {speedup:.2f}x mais rápido")
        else:
            print(f"   → Servidor sequencial foi {1/speedup:.2f}x mais rápido")

def exemplo_comparacao_cenarios():
    """Compara diferentes cenários de processamento"""
    print("\n=== Comparação de Cenários ===")
    
    servidor = "76.1.0.11"  # Servidor concorrente
    cliente = ClienteHTTP(servidor)
    
    cenarios = [
        ('/rapido', 'Processamento Rápido'),
        ('/medio', 'Processamento Médio'),
        ('/lento', 'Processamento Lento')
    ]
    
    for path, nome in cenarios:
        print(f"\n{nome} ({path}):")
        
        # Faz 3 requisições para calcular média
        tempos = []
        for i in range(3):
            resultado = cliente.enviar_requisicao('GET', path)
            if resultado['sucesso']:
                tempos.append(resultado['tempo_resposta'])
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
        print("  python3 testes/testes_automatizados.py --completo")
        
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário")
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        print("Verifique se os servidores estão rodando:")
