#!/usr/bin/env python3

#Teste Completo do Projeto Redes II
#Arquivo único para testar servidores sequencial e concorrente
#Consolida funcionalidades de teste_cliente.py e testes_automatizados.py

import sys
import os
import time
import json
import argparse
import threading
import statistics
from datetime import datetime

#Adicionar diretório src ao path (um nível acima da pasta testes)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from cliente import ClienteHTTP
    from configuracao import ID_CUSTOMIZADO, PORTA_SERVIDOR
except ImportError as e:
    print(f"[ERRO] Erro ao importar módulos: {e}")
    print("Certifique-se de estar no diretório correto do projeto")
    sys.exit(1)

class TestadorCarga:
    #Classe para executar testes de carga e concorrencia
    def __init__(self, host_servidor, porta_servidor=PORTA_SERVIDOR):
        self.cliente = ClienteHTTP(host_servidor, porta_servidor)
        self.resultados = []
        self.lock = threading.Lock()
        
    def teste_requisicao_unica(self, metodo='GET', caminho='/', id_cliente=None):
        #Executa um único teste de requisição
        resultado = self.cliente.enviar_requisicao(metodo, caminho)
        resultado['id_cliente'] = id_cliente
        resultado['timestamp'] = time.time()
        
        with self.lock:
            self.resultados.append(resultado)
        
        return resultado
    
    def teste_concorrente(self, num_clientes, requisicoes_por_cliente, metodo='GET', caminho='/'):
        #Executa teste com múltiplos clientes simultâneos
        threads = []
        self.resultados = []
        
        print(f"Iniciando teste com {num_clientes} clientes, {requisicoes_por_cliente} requisições cada")
        
        tempo_inicio = time.time()
        
        def executar_cliente(id_cliente):
            for i in range(requisicoes_por_cliente):
                self.teste_requisicao_unica(metodo, caminho, f"{id_cliente}-{i}")
                time.sleep(0.01)  #Pequeno delay entre requisições
        
        #Criar e iniciar threads
        for i in range(num_clientes):
            thread = threading.Thread(target=executar_cliente, args=(i,))
            threads.append(thread)
            thread.start()

        #Aguardar conclusão de todas as threads
        for thread in threads:
            thread.join()
        
        tempo_total = time.time() - tempo_inicio
        
        return {
            'tempo_total': tempo_total,
            'num_clientes': num_clientes,
            'requisicoes_por_cliente': requisicoes_por_cliente,
            'total_requisicoes': len(self.resultados),
            'resultados': self.resultados
        }
    
    def gerar_relatorio(self, resultado_teste):
        #Gera relatório detalhado do teste
        resultados = resultado_teste['resultados']
        sucessos = [r for r in resultados if r['sucesso']]
        falhas = [r for r in resultados if not r['sucesso']]
        
        if sucessos:
            tempos_resposta = [r['tempo_resposta'] for r in sucessos]
            tempo_medio = statistics.mean(tempos_resposta)
            tempo_min = min(tempos_resposta)
            tempo_max = max(tempos_resposta)
            tempo_mediano = statistics.median(tempos_resposta)
        else:
            tempo_medio = tempo_min = tempo_max = tempo_mediano = 0
        
        throughput = len(sucessos) / resultado_teste['tempo_total'] if resultado_teste['tempo_total'] > 0 else 0
        
        print(f"\n[RELATÓRIO]")
        print(f"Total de requisições: {len(resultados)}")
        print(f"Sucessos: {len(sucessos)}")
        print(f"Falhas: {len(falhas)}")
        print(f"Taxa de sucesso: {(len(sucessos)/len(resultados)*100):.1f}%")
        print(f"Tempo total: {resultado_teste['tempo_total']:.2f}s")
        print(f"Throughput: {throughput:.2f} req/s")
        
        if sucessos:
            print(f"Tempo de resposta médio: {tempo_medio:.4f}s")
            print(f"Tempo de resposta mínimo: {tempo_min:.4f}s")
            print(f"Tempo de resposta máximo: {tempo_max:.4f}s")
            print(f"Tempo de resposta mediano: {tempo_mediano:.4f}s")

class TestadorAutomatizado:
    #Classe para executar testes automatizados
    def __init__(self):
        self.resultados = {}
        
    def executar_todos_testes(self):
        #Executa todos os testes automatizados
        print("=== Iniciando Testes Automatizados ===")
        print(f"Data/Hora: {datetime.now()}")
        
        #Endereços dos servidores (baseado no docker-compose)
        servidores = {
            'sequencial': '76.1.0.10',
            'concorrente': '76.1.0.11'
        }
        
        #Diferentes cenários de teste
        cenarios_teste = [
            {'nome': 'rapido', 'caminho': '/rapido', 'descricao': 'Processamento rápido'},
            {'nome': 'medio', 'caminho': '/medio', 'descricao': 'Processamento médio (0.5s)'},
            {'nome': 'lento', 'caminho': '/lento', 'descricao': 'Processamento lento (2s)'},
        ]
        
        #Configurações de teste
        clientes_teste = [1, 5, 10, 20]
        requisicoes_por_cliente = 5
        
        for tipo_servidor, ip_servidor in servidores.items():
            print(f"\n=== Testando Servidor {tipo_servidor.upper()} ({ip_servidor}) ===")
            self.resultados[tipo_servidor] = {}
            
            for cenario in cenarios_teste:
                print(f"\n--- Cenário: {cenario['descricao']} ---")
                self.resultados[tipo_servidor][cenario['nome']] = {}
                
                for num_clientes in clientes_teste:
                    print(f"\nTestando com {num_clientes} clientes simultâneos...")
                    
                    testador = TestadorCarga(ip_servidor)
                    resultado = testador.teste_concorrente(
                        num_clientes, 
                        requisicoes_por_cliente,
                        'GET',
                        cenario['caminho']
                    )
                    
                    self.resultados[tipo_servidor][cenario['nome']][num_clientes] = resultado
                    testador.gerar_relatorio(resultado)
        
        self.salvar_resultados()
        self.gerar_comparacao()
    
    def salvar_resultados(self):
        #Salva os resultados em arquivo JSON
        resultados_com_metadados = {
            'metadados': {
                'data_teste': datetime.now().isoformat(),
                'id_personalizado': ID_CUSTOMIZADO,
                'versao_teste': '2.0'
            },
            'resultados': self.resultados
        }
        
        #Salvar resultados
        os.makedirs('/app/resultados', exist_ok=True)
        with open('/app/resultados/resultados_testes.json', 'w') as f:
            json.dump(resultados_com_metadados, f, indent=2)
        
        print(f"\n[SUCESSO] Resultados salvos em /app/resultados/resultados_testes.json")
    
    def gerar_comparacao(self):
        #Gera comparação entre servidores
        print("\n=== COMPARAÇÃO ENTRE SERVIDORES ===")
        
        if 'sequencial' in self.resultados and 'concorrente' in self.resultados:
            for cenario in ['rapido', 'medio', 'lento']:
                if cenario in self.resultados['sequencial'] and cenario in self.resultados['concorrente']:
                    print(f"\n--- Cenário: {cenario} ---")
                    
                    for num_clientes in [1, 5, 10, 20]:
                        if (num_clientes in self.resultados['sequencial'][cenario] and 
                            num_clientes in self.resultados['concorrente'][cenario]):
                            
                            seq = self.resultados['sequencial'][cenario][num_clientes]
                            conc = self.resultados['concorrente'][cenario][num_clientes]
                            
                            seq_sucessos = len([r for r in seq['resultados'] if r['sucesso']])
                            conc_sucessos = len([r for r in conc['resultados'] if r['sucesso']])
                            
                            seq_throughput = seq_sucessos / seq['tempo_total'] if seq['tempo_total'] > 0 else 0
                            conc_throughput = conc_sucessos / conc['tempo_total'] if conc['tempo_total'] > 0 else 0
                            
                            print(f"  {num_clientes} clientes:")
                            print(f"    Sequencial: {seq_throughput:.2f} req/s")
                            print(f"    Concorrente: {conc_throughput:.2f} req/s")
                            
                            if seq_throughput > 0:
                                melhoria = ((conc_throughput - seq_throughput) / seq_throughput) * 100
                                print(f"    Melhoria: {melhoria:.1f}%")

class TestadorProjeto:
    #Classe principal para testes do projeto
    
    def __init__(self):
        self.servidores_docker = {
            'sequencial': '76.1.0.10',
            'concorrente': '76.1.0.11'
        }
        self.servidores_local = {
            'sequencial': 'localhost:8080',
            'concorrente': 'localhost:8081'
        }
    
    def detectar_ambiente(self):
        #Detecta qual ambiente está disponível
        #Tenta Docker primeiro
        try:
            cliente = ClienteHTTP(self.servidores_docker['sequencial'])
            resultado = cliente.enviar_requisicao('GET', '/')
            if resultado['sucesso']:
                return 'docker'
        except:
            pass
        
        #Tenta local
        try:
            cliente = ClienteHTTP('localhost', 8080)
            resultado = cliente.enviar_requisicao('GET', '/')
            if resultado['sucesso']:
                return 'local'
        except:
            pass
        
        return None
    
    def teste_conectividade_basica(self, ambiente='docker'):
        #Executa teste básico de conectividade
        print("=== Teste de Conectividade ===")
        
        if ambiente == 'docker':
            configuracao_rede = "76.01.0.0/16"
            ip_servidor = "76.01.0.10"
            print(f"Configuração da rede: {configuracao_rede}")
            print(f"IP do servidor: {ip_servidor}")
            print(f"ID Personalizado: {ID_CUSTOMIZADO}")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\nTestando {tipo_servidor} ({endereco})...")
            
            try:
                if ':' in endereco:
                    host, porta = endereco.split(':')
                    cliente = ClienteHTTP(host, int(porta))
                else:
                    cliente = ClienteHTTP(endereco)
                
                resultado = cliente.enviar_requisicao('GET', '/')
                
                if resultado['sucesso']:
                    print(f"  [SUCESSO] Conectividade OK - Status: {resultado['codigo_status']}")
                    print(f"  [SUCESSO] Tempo de resposta: {resultado['tempo_resposta']:.4f}s")
                else:
                    print(f"  [ERRO] Erro de conectividade: {resultado.get('erro', 'Erro desconhecido')}")
                    
            except Exception as e:
                print(f"  [ERRO] Erro: {e}")
        
        print("\nPara executar todos os testes, use: python teste_completo.py --completo")
    
    def teste_endpoints(self, ambiente='docker'):
        #Testa diferentes endpoints dos servidores
        print("\n=== Teste de Endpoints ===")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        endpoints = ['/', '/rapido', '/medio', '/lento']
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\n--- Servidor {tipo_servidor} ---")
            
            if ':' in endereco:
                host, porta = endereco.split(':')
                cliente = ClienteHTTP(host, int(porta))
            else:
                cliente = ClienteHTTP(endereco)
            
            for endpoint in endpoints:
                resultado = cliente.enviar_requisicao('GET', endpoint)
                status = "[SUCESSO]" if resultado['sucesso'] else "[ERRO]"
                print(f"  {endpoint}: {status} - {resultado['codigo_status']} - {resultado['tempo_resposta']:.4f}s")
    
    def teste_validacao_cabecalho(self, ambiente='docker'):
        #Valida se o cabeçalho X-Custom-ID está presente
        print("\n=== Teste de Validação de Cabeçalho ===")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\n--- Servidor {tipo_servidor} ---")
            
            if ':' in endereco:
                host, porta = endereco.split(':')
                cliente = ClienteHTTP(host, int(porta))
            else:
                cliente = ClienteHTTP(endereco)
            
            resultado = cliente.enviar_requisicao('GET', '/')
            
            if resultado['sucesso']:
                cabecalhos = resultado.get('cabecalhos', {})
                if 'X-Custom-ID' in cabecalhos:
                    print(f"  [SUCESSO] X-Custom-ID encontrado: {cabecalhos['X-Custom-ID']}")
                    if cabecalhos['X-Custom-ID'] == ID_CUSTOMIZADO:
                        print(f"  [SUCESSO] ID correto!")
                    else:
                        print(f"  [AVISO] ID diferente do esperado")
                else:
                    print(f"  [ERRO] X-Custom-ID não encontrado nos cabeçalhos")
            else:
                print(f"  [ERRO] Falha na requisição")
    
    def teste_concorrencia(self, ambiente='docker'):
        #Executa teste de concorrência básico
        print("\n=== Teste de Concorrência ===")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\n--- Servidor {tipo_servidor} ---")
            
            if ':' in endereco:
                host, porta = endereco.split(':')
            else:
                host, porta = endereco, PORTA_SERVIDOR
            
            testador = TestadorCarga(host, int(porta))
            resultado = testador.teste_concorrente(5, 3, 'GET', '/medio')
            testador.gerar_relatorio(resultado)
    
    def executar_tudo(self, ambiente=None):
        #Executa todos os testes disponíveis
        if ambiente is None:
            ambiente = self.detectar_ambiente()
            if ambiente is None:
                print("[ERRO] Nenhum servidor disponível")
                return
        
        print(f"=== Executando todos os testes (ambiente: {ambiente}) ===")
        
        self.teste_conectividade_basica(ambiente)
        self.teste_endpoints(ambiente)
        self.teste_validacao_cabecalho(ambiente)
        self.teste_concorrencia(ambiente)
        
        print("\n" + "="*60)
        
        return True

def main():
    #Função principal
    parser = argparse.ArgumentParser(description='Testador Completo do Projeto Redes II')
    parser.add_argument('--ambiente', choices=['docker', 'local'], 
                       help='Especificar ambiente (docker ou local)')
    parser.add_argument('--conectividade', action='store_true',
                       help='Executar apenas teste de conectividade')
    parser.add_argument('--endpoints', action='store_true',
                       help='Executar apenas teste de endpoints')
    parser.add_argument('--cabecalho', action='store_true',
                       help='Executar apenas teste de validação de cabeçalho')
    parser.add_argument('--concorrencia', action='store_true',
                       help='Executar apenas teste de concorrência')
    parser.add_argument('--completo', action='store_true',
                       help='Executar testes automatizados completos')
    
    args = parser.parse_args()
    
    if args.completo:
        #Executar testes automatizados completos
        testador_auto = TestadorAutomatizado()
        testador_auto.executar_todos_testes()
    else:
        #Executar testes básicos
        testador = TestadorProjeto()
        
        #Se nenhum teste específico foi especificado, executar tudo
        if not any([args.conectividade, args.endpoints, args.cabecalho, args.concorrencia]):
            testador.executar_tudo(args.ambiente)
        else:
            #Detectar ambiente se não especificado
            ambiente = args.ambiente
            if ambiente is None:
                ambiente = testador.detectar_ambiente()
                if ambiente is None:
                    print("[ERRO] Nenhum servidor disponível")
                    return

            #Executar testes específicos
            if args.conectividade:
                testador.teste_conectividade_basica(ambiente)
            
            if args.endpoints:
                testador.teste_endpoints(ambiente)
            
            if args.cabecalho:
                testador.teste_validacao_cabecalho(ambiente)
            
            if args.concorrencia:
                testador.teste_concorrencia(ambiente)

if __name__ == "__main__":
    main()
