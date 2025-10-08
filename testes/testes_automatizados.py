"""
Script para executar testes automatizados nos servidores
"""
import time
import json
import statistics
import threading
from datetime import datetime
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from teste_cliente import TestadorCarga
from configuracao import ITERACOES_TESTE, CLIENTES_TESTE, TAMANHOS_REQUISICAO

class TestadorAutomatizado:
    def __init__(self):
        self.resultados = {}
        
    def executar_todos_testes(self):
        """Executa todos os testes automatizados"""
        print("=== Iniciando Testes Automatizados ===")
        print(f"Data/Hora: {datetime.now()}")
        
        # Endereços dos servidores (baseado no docker-compose)
        servidores = {
            'sequencial': '76.1.0.10',
            'concorrente': '76.1.0.11'
        }
        
        # Diferentes cenários de teste
        cenarios_teste = [
            {'nome': 'rapido', 'caminho': '/rapido', 'descricao': 'Processamento rápido'},
            {'nome': 'medio', 'caminho': '/medio', 'descricao': 'Processamento médio (0.5s)'},
            {'nome': 'lento', 'caminho': '/lento', 'descricao': 'Processamento lento (2s)'},
        ]
        
        for tipo_servidor, ip_servidor in servidores.items():
            print(f"\n=== Testando Servidor {tipo_servidor.upper()} ({ip_servidor}) ===")
            self.resultados[tipo_servidor] = {}
            
            for cenario in cenarios_teste:
                print(f"\n--- Cenário: {cenario['descricao']} ---")
                self.resultados[tipo_servidor][cenario['nome']] = {}
                
                for num_clientes in CLIENTES_TESTE:
                    print(f"\nTestando com {num_clientes} clientes simultâneos...")
                    
                    resultados_cenario = []
                    
                    # Executa múltiplas iterações para calcular média e desvio padrão
                    for iteracao in range(ITERACOES_TESTE):
                        print(f"  Iteração {iteracao + 1}/{ITERACOES_TESTE}")
                        
                        try:
                            testador = TestadorCarga(ip_servidor)
                            resultado = testador.teste_concorrente(
                                num_clientes=num_clientes,
                                requisicoes_por_cliente=2,  # 2 requisições por cliente
                                metodo='GET',
                                caminho=cenario['caminho']
                            )
                            
                            resultados_cenario.append(resultado['resumo'])
                            
                            # Pequena pausa entre iterações
                            time.sleep(1)
                            
                        except Exception as e:
                            print(f"    Erro na iteração {iteracao + 1}: {e}")
                            resultados_cenario.append({
                                'total_requisicoes': num_clientes * 2,
                                'requisicoes_sucesso': 0,
                                'requisicoes_falha': num_clientes * 2,
                                'taxa_sucesso': 0,
                                'tempo_resposta_medio': 0,
                                'erro': str(e)
                            })
                    
                    # Calcula estatísticas
                    estatisticas = self.calcular_estatisticas(resultados_cenario)
                    self.resultados[tipo_servidor][cenario['nome']][num_clientes] = estatisticas
                    
                    print(f"    Resultados:")
                    print(f"      Taxa de sucesso: {estatisticas['taxa_sucesso_media']:.2%} (±{estatisticas['taxa_sucesso_desvio']:.2%})")
                    print(f"      Tempo médio: {estatisticas['tempo_resposta_media']:.4f}s (±{estatisticas['tempo_resposta_desvio']:.4f}s)")
        
        # Salva resultados
        self.salvar_resultados()
        print(f"\n=== Testes Concluídos ===")
        print("Resultados salvos em resultados/resultados_testes.json")
    
    def calcular_estatisticas(self, resultados):
        """Calcula estatísticas dos resultados"""
        if not resultados:
            return {}
        
        # Filtra apenas resultados bem-sucedidos para algumas métricas
        resultados_sucesso = [r for r in resultados if r.get('taxa_sucesso', 0) > 0]
        
        estatisticas = {
            'total_iteracoes': len(resultados),
            'iteracoes_sucesso': len(resultados_sucesso),
            'total_requisicoes_media': statistics.mean([r.get('total_requisicoes', 0) for r in resultados]),
            'requisicoes_sucesso_media': statistics.mean([r.get('requisicoes_sucesso', 0) for r in resultados]),
            'requisicoes_falha_media': statistics.mean([r.get('requisicoes_falha', 0) for r in resultados]),
        }
        
        # Calcula estatísticas de taxa de sucesso
        taxas_sucesso = [r.get('taxa_sucesso', 0) for r in resultados]
        estatisticas['taxa_sucesso_media'] = statistics.mean(taxas_sucesso)
        estatisticas['taxa_sucesso_desvio'] = statistics.stdev(taxas_sucesso) if len(taxas_sucesso) > 1 else 0
        estatisticas['taxa_sucesso_min'] = min(taxas_sucesso)
        estatisticas['taxa_sucesso_max'] = max(taxas_sucesso)
        
        # Calcula estatísticas de tempo de resposta (apenas para resultados bem-sucedidos)
        if resultados_sucesso:
            tempos_resposta = [r.get('tempo_resposta_medio', 0) for r in resultados_sucesso]
            estatisticas['tempo_resposta_media'] = statistics.mean(tempos_resposta)
            estatisticas['tempo_resposta_desvio'] = statistics.stdev(tempos_resposta) if len(tempos_resposta) > 1 else 0
            estatisticas['tempo_resposta_min'] = min(tempos_resposta)
            estatisticas['tempo_resposta_max'] = max(tempos_resposta)
        else:
            estatisticas['tempo_resposta_media'] = 0
            estatisticas['tempo_resposta_desvio'] = 0
            estatisticas['tempo_resposta_min'] = 0
            estatisticas['tempo_resposta_max'] = 0
        
        # Lista de erros encontrados
        erros = [r.get('erro') for r in resultados if 'erro' in r]
        estatisticas['erros'] = list(set(erros))
        
        return estatisticas
    
    def salvar_resultados(self):
        """Salva os resultados em arquivo JSON"""
        os.makedirs('/app/resultados', exist_ok=True)
        
        resultados_com_metadados = {
            'timestamp': datetime.now().isoformat(),
            'configuracao_teste': {
                'iteracoes': ITERACOES_TESTE,
                'contagens_clientes': CLIENTES_TESTE,
                'requisicoes_por_cliente': 2
            },
            'resultados': self.resultados
        }
        
        with open('/app/resultados/resultados_testes.json', 'w') as f:
            json.dump(resultados_com_metadados, f, indent=2)
    
    def executar_teste_conectividade_simples(self):
        """Executa teste simples de conectividade"""
        print("=== Teste de Conectividade ===")
        
        servidores = {
            'sequencial': '76.1.0.10',
            'concorrente': '76.1.0.11'
        }
        
        for tipo_servidor, ip_servidor in servidores.items():
            print(f"\nTestando {tipo_servidor} ({ip_servidor})...")
            
            try:
                from cliente import ClienteHTTP
                cliente = ClienteHTTP(ip_servidor)
                resultado = cliente.enviar_requisicao('GET', '/')
                
                if resultado['sucesso']:
                    print(f"  ✓ Conectividade OK - Status: {resultado['codigo_status']}")
                    print(f"  ✓ Tempo de resposta: {resultado['tempo_resposta']:.4f}s")
                else:
                    print(f"  ✗ Erro de conectividade: {resultado.get('erro', 'Erro desconhecido')}")
                    
            except Exception as e:
                print(f"  ✗ Erro: {e}")

if __name__ == "__main__":
    testador = TestadorAutomatizado()
    
    # Primeiro executa teste de conectividade
    testador.executar_teste_conectividade_simples()
    
    # Pergunta se deve executar todos os testes
    if len(sys.argv) > 1 and sys.argv[1] == '--completo':
        testador.executar_todos_testes()
    else:
        print("\nPara executar todos os testes, use: python testes_automatizados.py --completo")
