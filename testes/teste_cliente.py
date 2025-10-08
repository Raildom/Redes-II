#!/usr/bin/env python3
"""
Teste Completo do Projeto Redes II
Arquivo independente para testar servidores sequencial e concorrente
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime

# Adicionar diretório src ao path (um nível acima da pasta testes)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from cliente import ClienteHTTP, TestadorCarga
    from configuracao import ID_CUSTOMIZADO, PORTA_SERVIDOR
except ImportError as e:
    print(f"X Erro ao importar módulos: {e}")
    print("Certifique-se de estar no diretório correto do projeto")
    sys.exit(1)

class TestadorProjeto:
    """Classe para executar todos os testes do projeto"""
    
    def __init__(self):
        # Configuração baseada no ambiente
        self.servidores = {
            'sequencial': {
                'ip': '76.1.0.10',  # IP no Docker
                'porta': 8080,
                'nome': 'Servidor Sequencial'
            },
            'concorrente': {
                'ip': '76.1.0.11',  # IP no Docker
                'porta': 8080,
                'nome': 'Servidor Concorrente'
            }
        }
        
        # Para execução local (fora do Docker)
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
        """Detecta se está rodando dentro do Docker ou localmente"""
        try:
            # Tenta conectar no IP do Docker primeiro
            cliente_teste = ClienteHTTP('76.1.0.10', 8080)
            resultado = cliente_teste.enviar_requisicao('GET', '/')
            if resultado['codigo_status'] == 200:
                print("🐳 Ambiente Docker detectado")
                return 'docker'
        except:
            pass
        
        try:
            # Tenta conectar localmente
            cliente_teste = ClienteHTTP('localhost', 8080)
            resultado = cliente_teste.enviar_requisicao('GET', '/')
            if resultado['codigo_status'] == 200:
                print("💻 Ambiente local detectado")
                return 'local'
        except:
            pass
        
        print("❌ Nenhum servidor encontrado")
        return None
    
    def teste_conectividade_basica(self, ambiente='docker'):
        """Testa conectividade básica com ambos servidores"""
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
                    print(f"   ✅ Conectividade OK - Tempo: {resultado['tempo_resposta']:.3f}s")
                    
                    # Parse da resposta JSON
                    try:
                        dados = json.loads(resultado['corpo'])
                        print(f"   📄 Tipo servidor: {dados.get('tipo_servidor', 'N/A')}")
                        print(f"   🔢 Requisições processadas: {dados.get('contador_requisicoes', 'N/A')}")
                        print(f"   🆔 ID válido: {dados.get('id_customizado_valido', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"   📄 Resposta: {resultado['corpo'][:100]}...")
                        
                else:
                    print(f"   ❌ Erro: Status {resultado['codigo_status']}")
                    
            except Exception as e:
                print(f"   ❌ Falha na conexão: {str(e)}")
    
    def teste_endpoints(self, ambiente='docker'):
        """Testa todos os endpoints de ambos servidores"""
        print("\n" + "="*60)
        print("🎯 TESTE DE ENDPOINTS")
        print("="*60)
        
        servidores = self.servidores if ambiente == 'docker' else self.servidores_local
        
        for tipo, config in servidores.items():
            print(f"\n🖥️ {config['nome']}")
            print("-" * 40)
            
            cliente = ClienteHTTP(config['ip'], config['porta'])
            
            for endpoint in self.endpoints:
                print(f"  📍 {endpoint['nome']} ({endpoint['path']})")
                
                try:
                    resultado = cliente.enviar_requisicao('GET', endpoint['path'])
                    tempo = resultado['tempo_resposta']
                    status = resultado['codigo_status']
                    
                    if status == 200:
                        emoji = "✅" if tempo <= endpoint['tempo_esperado'] else "⚠️"
                        print(f"     {emoji} Status: {status} | Tempo: {tempo:.3f}s")
                        
                        # Salvar resultado para análise
                        self.resultados.append({
                            'servidor': tipo,
                            'endpoint': endpoint['path'],
                            'tempo': tempo,
                            'status': status,
                            'sucesso': True
                        })
                    else:
                        print(f"     ❌ Status: {status} | Tempo: {tempo:.3f}s")
                        self.resultados.append({
                            'servidor': tipo,
                            'endpoint': endpoint['path'],
                            'tempo': tempo,
                            'status': status,
                            'sucesso': False
                        })
                        
                except Exception as e:
                    print(f"     ❌ Erro: {str(e)}")
                    self.resultados.append({
                        'servidor': tipo,
                        'endpoint': endpoint['path'],
                        'tempo': 0,
                        'status': 0,
                        'sucesso': False,
                        'erro': str(e)
                    })
    
    def teste_validacao_cabecalho(self, ambiente='docker'):
        """Testa validação do cabeçalho X-Custom-ID"""
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
            print(f"\n🖥️ {config['nome']}")
            print("-" * 40)
            
            for caso in casos_teste:
                print(f"  🧪 {caso['nome']}: {caso['id'][:20]}...")
                
                try:
                    cliente = ClienteHTTP(config['ip'], config['porta'])
                    # Sobrescrever o cabeçalho customizado
                    resultado = cliente.enviar_requisicao('GET', '/', {'X-Custom-ID': caso['id']})
                    
                    if resultado['codigo_status'] == 200:
                        dados = json.loads(resultado['corpo'])
                        valido = dados.get('id_customizado_valido', False)
                        
                        if valido == caso['deveria_passar']:
                            print(f"     ✅ Validação correta: {valido}")
                        else:
                            print(f"     ❌ Validação incorreta: esperado {caso['deveria_passar']}, obteve {valido}")
                    else:
                        print(f"     ❌ Erro: Status {resultado['codigo_status']}")
                        
                except Exception as e:
                    print(f"     ❌ Erro: {str(e)}")
    
    def teste_concorrencia(self, ambiente='docker'):
        """Testa capacidade de concorrência dos servidores"""
        print("\n" + "="*60)
        print("⚡ TESTE DE CONCORRÊNCIA")
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
                print(f"  🖥️ {config['nome']}")
                
                try:
                    testador = TestadorCarga(config['ip'], config['porta'])
                    resultado = testador.teste_concorrente(
                        num_clientes=cenario['clientes'],
                        requisicoes_por_cliente=cenario['requisicoes'],
                        metodo='GET',
                        caminho=cenario['endpoint']
                    )
                    
                    resumo = resultado['resumo']
                    print(f"     📊 Sucesso: {resumo['requisicoes_sucesso']}/{resumo['total_requisicoes']}")
                    print(f"     ⏱️ Tempo médio: {resumo['tempo_resposta_medio']:.3f}s")
                    print(f"     📈 Taxa sucesso: {resumo['taxa_sucesso']:.1f}%")
                    
                except Exception as e:
                    print(f"     ❌ Erro: {str(e)}")
    
    def relatorio_comparativo(self):
        """Gera relatório comparativo dos resultados"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO COMPARATIVO")
        print("="*60)
        
        if not self.resultados:
            print("❌ Nenhum resultado disponível para análise")
            return
        
        # Agrupar por endpoint
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
        """Executa todos os testes"""
        print("🚀 TESTADOR COMPLETO DO PROJETO REDES II")
        print("Matrícula: 20239057601")
        print("Aluno: Raildom")
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Detectar ambiente se não especificado
        if ambiente is None:
            ambiente = self.detectar_ambiente()
            if ambiente is None:
                print("❌ Nenhum servidor disponível. Certifique-se de que os servidores estejam rodando.")
                return False
        
        # Executar testes
        self.teste_conectividade_basica(ambiente)
        self.teste_endpoints(ambiente)
        self.teste_validacao_cabecalho(ambiente)
        self.teste_concorrencia(ambiente)
        self.relatorio_comparativo()
        
        print("\n" + "="*60)
        print("🎉 TODOS OS TESTES CONCLUÍDOS!")
        print("="*60)
        
        return True

def main():
    """Função principal"""
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
    
    # Se nenhum teste específico foi especificado, executar tudo
    if not any([args.conectividade, args.endpoints, args.cabecalho, args.concorrencia]):
        testador.executar_tudo(args.ambiente)
    else:
        # Detectar ambiente se não especificado
        ambiente = args.ambiente
        if ambiente is None:
            ambiente = testador.detectar_ambiente()
            if ambiente is None:
                print("❌ Nenhum servidor disponível")
                return
        
        # Executar testes específicos
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
