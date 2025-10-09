#!/usr/bin/env python3

#Teste Completo do Projeto Redes II
#Arquivo independente para testar servidores sequencial e concorrente

import sys
import os
import time
import json
import argparse
import threading
from datetime import datetime

#Adicionar diretório src ao path (um nível acima da pasta testes)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from cliente import ClienteHTTP
    from configuracao import ID_CUSTOMIZADO, PORTA_SERVIDOR
except ImportError as e:
    print(f"X Erro ao importar módulos: {e}")
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
        
        for id_cliente in range(num_clientes):
            thread = threading.Thread(
                target=self._trabalhador_cliente,
                args=(id_cliente, requisicoes_por_cliente, metodo, caminho)
            )
            threads.append(thread)
            thread.start()
        
        #Aguarda todas as threads terminarem
        for thread in threads:
            thread.join()
        
        tempo_total = time.time() - tempo_inicio
        
        return {
            'tempo_total': tempo_total,
            'resultados': self.resultados,
            'resumo': self._calcular_resumo()
        }
    
    def _trabalhador_cliente(self, id_cliente, num_requisicoes, metodo, caminho):
        #Worker para executar requisicoes de um cliente
        for id_req in range(num_requisicoes):
            resultado = self.teste_requisicao_unica(metodo, caminho, f"{id_cliente}-{id_req}")
            if id_req % 10 == 0:  #Log a cada 10 requisicoes
                print(f"Cliente {id_cliente}: {id_req + 1}/{num_requisicoes} requisicoes completadas")
    
    def _calcular_resumo(self):
        #Calcula estatísticas dos resultados
        if not self.resultados:
            return {}
        
        resultados_sucesso = [r for r in self.resultados if r['sucesso']]
        resultados_falha = [r for r in self.resultados if not r['sucesso']]
        
        if resultados_sucesso:
            tempos_resposta = [r['tempo_resposta'] for r in resultados_sucesso]
            
            resumo = {
                'total_requisicoes': len(self.resultados),
                'requisicoes_sucesso': len(resultados_sucesso),
                'requisicoes_falha': len(resultados_falha),
                'taxa_sucesso': len(resultados_sucesso) / len(self.resultados),
                'tempo_resposta_medio': sum(tempos_resposta) / len(tempos_resposta),
                'tempo_resposta_min': min(tempos_resposta),
                'tempo_resposta_max': max(tempos_resposta),
                'tempo_total': max([r['timestamp'] for r in self.resultados]) - min([r['timestamp'] for r in self.resultados])
            }
        else:
            resumo = {
                'total_requisicoes': len(self.resultados),
                'requisicoes_sucesso': 0,
                'requisicoes_falha': len(resultados_falha),
                'taxa_sucesso': 0
            }
        
        return resumo

class TestadorProjeto:
    #Classe para executar todos os testes do projeto
    
    def __init__(self):
        #Configuração baseada no ambiente
        self.servidores = {
            'sequencial': {
                'ip': '76.1.0.10',  #IP no Docker
                'porta': 80,  #Porta interna do contêiner
                'nome': 'Servidor Sequencial'
            },
            'concorrente': {
                'ip': '76.1.0.11',  #IP no Docker
                'porta': 80,  #Porta interna do contêiner
                'nome': 'Servidor Concorrente'
            }
        }
        
        #Para execução externa ao Docker (do host para contêineres)
        self.servidores_local = {
            'sequencial': {
                'ip': 'localhost',
                'porta': 8080,
                'nome': 'Servidor Sequencial (Local)'
            },
            'concorrente': {
                'ip': 'localhost',
                'porta': 8081,
                'nome': 'Servidor Concorrente (Local)'
            }
        }
        
        self.endpoints = [
            {'path': '/', 'nome': 'Página inicial', 'tempo_esperado': 0.1},
            {'path': '/status', 'nome': 'Status do servidor', 'tempo_esperado': 0.1},
            {'path': '/rapido', 'nome': 'Processamento rápido', 'tempo_esperado': 0.1},
            {'path': '/medio', 'nome': 'Processamento médio', 'tempo_esperado': 0.6},
            {'path': '/lento', 'nome': 'Processamento lento', 'tempo_esperado': 2.1},
        ]
        
        self.resultados = []
    
    def detectar_ambiente(self):
        #Detecta se está rodando dentro do Docker ou localmente
        try:
            #Tenta conectar no IP do Docker primeiro (comunicação interna)
            cliente_teste = ClienteHTTP('76.1.0.10', 80)
            resultado = cliente_teste.enviar_requisicao('GET', '/')
            if resultado['codigo_status'] == 200:
                print("[DOCKER] Ambiente Docker detectado (comunicação interna)")
                return 'docker'
        except:
            pass
        
        try:
            #Tenta conectar via portas mapeadas (do host para Docker)
            cliente_teste = ClienteHTTP('localhost', 8080)
            resultado = cliente_teste.enviar_requisicao('GET', '/')
            if resultado['codigo_status'] == 200:
                print("[LOCAL] Ambiente local detectado (host->Docker)")
                return 'local'
        except:
            pass
        
        print("[ERRO] Nenhum servidor encontrado")
        return None
    
    def teste_conectividade_basica(self, ambiente='docker'):
        #Testa conectividade básica com ambos servidores
        print("\n" + "="*60)
        print("🔌 TESTE DE CONECTIVIDADE BÁSICA")
        print("="*60)
        
        servidores = self.servidores if ambiente == 'docker' else self.servidores_local
        
        for tipo, config in servidores.items():
            print(f"\n📡 Testando {config['nome']} ({config['ip']}:{config['porta']})")
            
            try:
                cliente = ClienteHTTP(config['ip'], config['porta'])
                resultado = cliente.enviar_requisicao('GET', '/')
                
                if resultado['codigo_status'] == 200:
                    print(f"   [SUCESSO] Conectividade OK - Tempo: {resultado['tempo_resposta']:.3f}s")
                    
                    #Parse da resposta JSON
                    try:
                        dados = json.loads(resultado['corpo'])
                        print(f"   [DOCUMENTO] Tipo servidor: {dados.get('tipo_servidor', 'N/A')}")
                        print(f"   🔢 Requisições processadas: {dados.get('contador_requisicoes', 'N/A')}")
                        print(f"   🆔 ID válido: {dados.get('id_customizado_valido', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"   [DOCUMENTO] Resposta: {resultado['corpo'][:100]}...")
                        
                else:
                    print(f"   [ERRO] Erro: Status {resultado['codigo_status']}")
                    
            except Exception as e:
                print(f"   [ERRO] Falha na conexão: {str(e)}")
    
    def teste_endpoints(self, ambiente='docker'):
        #Testa todos os endpoints de ambos servidores
        print("\n" + "="*60)
        print("[TESTE] TESTE DE ENDPOINTS")
        print("="*60)
        
        servidores = self.servidores if ambiente == 'docker' else self.servidores_local
        
        for tipo, config in servidores.items():
            print(f"\n[SERVIDOR] {config['nome']}")
            print("-" * 40)
            
            cliente = ClienteHTTP(config['ip'], config['porta'])
            
            for endpoint in self.endpoints:
                print(f"  📍 {endpoint['nome']} ({endpoint['path']})")
                
                try:
                    resultado = cliente.enviar_requisicao('GET', endpoint['path'])
                    tempo = resultado['tempo_resposta']
                    status = resultado['codigo_status']
                    
                    if status == 200:
                        emoji = "[SUCESSO]" if tempo <= endpoint['tempo_esperado'] else "[AVISO]"
                        print(f"     {emoji} Status: {status} | Tempo: {tempo:.3f}s")
                        
                        #Salvar resultado para análise
                        self.resultados.append({
                            'servidor': tipo,
                            'endpoint': endpoint['path'],
                            'tempo': tempo,
                            'status': status,
                            'sucesso': True
                        })
                    else:
                        print(f"     [ERRO] Status: {status} | Tempo: {tempo:.3f}s")
                        self.resultados.append({
                            'servidor': tipo,
                            'endpoint': endpoint['path'],
                            'tempo': tempo,
                            'status': status,
                            'sucesso': False
                        })
                        
                except Exception as e:
                    print(f"     [ERRO] Erro: {str(e)}")
                    self.resultados.append({
                        'servidor': tipo,
                        'endpoint': endpoint['path'],
                        'tempo': 0,
                        'status': 0,
                        'sucesso': False,
                        'erro': str(e)
                    })
    
    def teste_validacao_cabecalho(self, ambiente='docker'):
        #Testa validação do cabeçalho X-Custom-ID
        print("\n" + "="*60)
        print("🔒 TESTE DE VALIDAÇÃO DO CABEÇALHO")
        print("="*60)
        
        servidores = self.servidores if ambiente == 'docker' else self.servidores_local
        
        casos_teste = [
            {'id': ID_CUSTOMIZADO, 'nome': 'ID Correto', 'deveria_passar': True},
            {'id': 'INVALIDO', 'nome': 'ID Inválido', 'deveria_passar': False},
            {'id': '', 'nome': 'ID Vazio', 'deveria_passar': False},
        ]
        
        for tipo, config in servidores.items():
            print(f"\n[SERVIDOR] {config['nome']}")
            print("-" * 40)
            
            for caso in casos_teste:
                print(f"  🧪 {caso['nome']}: {caso['id'][:20]}...")
                
                try:
                    cliente = ClienteHTTP(config['ip'], config['porta'])
                    #Sobrescrever o cabeçalho customizado
                    resultado = cliente.enviar_requisicao('GET', '/', {'X-Custom-ID': caso['id']})
                    
                    if resultado['codigo_status'] == 200:
                        dados = json.loads(resultado['corpo'])
                        valido = dados.get('id_customizado_valido', False)
                        
                        if valido == caso['deveria_passar']:
                            print(f"     [SUCESSO] Validação correta: {valido}")
                        else:
                            print(f"     [ERRO] Validação incorreta: esperado {caso['deveria_passar']}, obteve {valido}")
                    else:
                        print(f"     [ERRO] Erro: Status {resultado['codigo_status']}")
                        
                except Exception as e:
                    print(f"     [ERRO] Erro: {str(e)}")
    
    def teste_concorrencia(self, ambiente='docker'):
        #Testa capacidade de concorrência dos servidores
        print("\n" + "="*60)
        print("TESTE DE CONCORRÊNCIA")
        print("="*60)
        
        servidores = self.servidores if ambiente == 'docker' else self.servidores_local
        
        cenarios = [
            {'clientes': 3, 'requisicoes': 2, 'endpoint': '/medio'},
            {'clientes': 5, 'requisicoes': 1, 'endpoint': '/rapido'},
        ]
        
        for cenario in cenarios:
            print(f"\n🧪 Cenário: {cenario['clientes']} clientes, {cenario['requisicoes']} req/cliente, endpoint {cenario['endpoint']}")
            print("-" * 50)
            
            for tipo, config in servidores.items():
                print(f"  [SERVIDOR] {config['nome']}")
                
                try:
                    testador = TestadorCarga(config['ip'], config['porta'])
                    resultado = testador.teste_concorrente(
                        num_clientes=cenario['clientes'],
                        requisicoes_por_cliente=cenario['requisicoes'],
                        metodo='GET',
                        caminho=cenario['endpoint']
                    )
                    
                    resumo = resultado['resumo']
                    print(f"     [ESTATISTICA] Sucesso: {resumo['requisicoes_sucesso']}/{resumo['total_requisicoes']}")
                    print(f"     [TEMPO] Tempo médio: {resumo['tempo_resposta_medio']:.3f}s")
                    print(f"     📈 Taxa sucesso: {resumo['taxa_sucesso']:.1f}%")
                    
                except Exception as e:
                    print(f"     [ERRO] Erro: {str(e)}")
    
    def relatório_comparativo(self):
        #Gera relatório comparativo dos resultados
        print("\n" + "="*60)
        print("[ESTATÍSTICA] RELATÓRIO COMPARATIVO")
        print("="*60)
        
        if not self.resultados:
            print("[ERRO] Nenhum resultado disponível para análise")
            return
        
        #Agrupar por endpoint
        por_endpoint = {}
        for resultado in self.resultados:
            endpoint = resultado['endpoint']
            if endpoint not in por_endpoint:
                por_endpoint[endpoint] = {'sequencial': [], 'concorrente': []}
            
            if resultado['sucesso']:
                por_endpoint[endpoint][resultado['servidor']].append(resultado['tempo'])
        
        print("\n🏁 Comparação de Tempos de Resposta:")
        print("-" * 40)
        
        for endpoint, dados in por_endpoint.items():
            print(f"\n📍 Endpoint: {endpoint}")
            
            for servidor, tempos in dados.items():
                if tempos:
                    tempo_medio = sum(tempos) / len(tempos)
                    tempo_min = min(tempos)
                    tempo_max = max(tempos)
                    print(f"  {servidor:12}: {tempo_medio:.3f}s (min: {tempo_min:.3f}s, max: {tempo_max:.3f}s)")
                else:
                    print(f"  {servidor:12}: Sem dados")
    
    def executar_tudo(self, ambiente=None):
        #Executa todos os testes
        print("[EXECUÇÃO] TESTADOR COMPLETO DO PROJETO REDES II")
        print("Matrícula: 20239057601")
        print("Aluno: Raildom")
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        #Detectar ambiente se não especificado
        if ambiente is None:
            ambiente = self.detectar_ambiente()
            if ambiente is None:
                print("[ERRO] Nenhum servidor disponível. Certifique-se de que os servidores estejam rodando.")
                return False

        #Executar testes
        self.teste_conectividade_basica(ambiente)
        self.teste_endpoints(ambiente)
        self.teste_validacao_cabecalho(ambiente)
        self.teste_concorrencia(ambiente)
        self.relatório_comparativo()
        
        print("\n" + "="*60)
        print("🎉 TODOS OS TESTES CONCLUÍDOS!")
        print("="*60)
        
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
    
    args = parser.parse_args()
    
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
