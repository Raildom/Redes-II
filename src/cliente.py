"""
Cliente HTTP para testar os servidores
"""
import socket
import time
import json
import threading
from configuracao import ID_CUSTOMIZADO, PORTA_SERVIDOR

class ClienteHTTP:
    def __init__(self, host_servidor, porta_servidor=PORTA_SERVIDOR):
        self.host_servidor = host_servidor
        self.porta_servidor = porta_servidor
        
    def enviar_requisicao(self, metodo='GET', caminho='/', cabecalhos=None, corpo=None):
        #Envia uma requisição HTTP para o servidor
        if cabecalhos is None:
            cabecalhos = {}
        
        #Adiciona o cabeçalho customizado obrigatório
        cabecalhos['X-Custom-ID'] = ID_CUSTOMIZADO
        cabecalhos['Host'] = f"{self.host_servidor}:{self.porta_servidor}"
        cabecalhos['Connection'] = 'close'
        
        try:
            #Cria conexão
            socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_cliente.settimeout(10)  # Timeout de 10 segundos
            
            tempo_inicio = time.time()
            socket_cliente.connect((self.host_servidor, self.porta_servidor))
            tempo_conexao = time.time() - tempo_inicio
            
            #Monta a requisição HTTP
            linha_requisicao = f"{metodo} {caminho} HTTP/1.1\r\n"
            linhas_cabecalho = "\r\n".join([f"{chave}: {valor}" for chave, valor in cabecalhos.items()])
            
            if corpo:
                cabecalhos['Content-Length'] = str(len(corpo))
                requisicao = f"{linha_requisicao}{linhas_cabecalho}\r\n\r\n{corpo}"
            else:
                requisicao = f"{linha_requisicao}{linhas_cabecalho}\r\n\r\n"
            
            #Envia requisição
            inicio_envio = time.time()
            socket_cliente.send(requisicao.encode('utf-8'))
            tempo_envio = time.time() - inicio_envio
            
            #Recebe resposta
            inicio_recepcao = time.time()
            dados_resposta = b""
            while True:
                pedaco = socket_cliente.recv(4096)
                if not pedaco:
                    break
                dados_resposta += pedaco
                
                #Verifica se recebeu a resposta completa
                if b"\r\n\r\n" in dados_resposta:
                    fim_cabecalho = dados_resposta.find(b"\r\n\r\n")
                    parte_cabecalhos = dados_resposta[:fim_cabecalho].decode('utf-8')
                    
                    #Verifica se tem Content-Length
                    tamanho_conteudo = 0
                    for linha in parte_cabecalhos.split('\r\n'):
                        if linha.lower().startswith('content-length:'):
                            tamanho_conteudo = int(linha.split(':')[1].strip())
                            break
                    
                    if tamanho_conteudo > 0:
                        inicio_corpo = fim_cabecalho + 4
                        corpo_recebido = len(dados_resposta) - inicio_corpo
                        if corpo_recebido >= tamanho_conteudo:
                            break
                    else:
                        break
            
            tempo_recepcao = time.time() - inicio_recepcao
            tempo_total = time.time() - tempo_inicio
            
            socket_cliente.close()
            
            #Parse da resposta
            texto_resposta = dados_resposta.decode('utf-8')
            
            if "\r\n\r\n" in texto_resposta:
                parte_cabecalhos, parte_corpo = texto_resposta.split("\r\n\r\n", 1)
                linha_status = parte_cabecalhos.split('\r\n')[0]
                codigo_status = int(linha_status.split(' ')[1])
            else:
                codigo_status = 0
                parte_corpo = ""
            
            return {
                'codigo_status': codigo_status,
                'corpo': parte_corpo,
                'tempo_resposta': tempo_total,
                'tempo_conexao': tempo_conexao,
                'tempo_envio': tempo_envio,
                'tempo_recepcao': tempo_recepcao,
                'sucesso': True
            }
            
        except Exception as e:
            return {
                'codigo_status': 0,
                'corpo': "",
                'tempo_resposta': time.time() - tempo_inicio if 'tempo_inicio' in locals() else 0,
                'tempo_conexao': 0,
                'tempo_envio': 0,
                'tempo_recepcao': 0,
                'sucesso': False,
                'erro': str(e)
            }

class TestadorCarga:
    def __init__(self, host_servidor, porta_servidor=PORTA_SERVIDOR):
        self.cliente = ClienteHTTP(host_servidor, porta_servidor)
        self.resultados = []
        self.lock = threading.Lock()
        
    def teste_requisicao_unica(self, metodo='GET', caminho='/', id_cliente=None):
        """Executa um único teste de requisição"""
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
        #Worker para executar requisições de um cliente
        for id_req in range(num_requisicoes):
            resultado = self.teste_requisicao_unica(metodo, caminho, f"{id_cliente}-{id_req}")
            if id_req % 10 == 0:  # Log a cada 10 requisições
                print(f"Cliente {id_cliente}: {id_req + 1}/{num_requisicoes} requisições completadas")
    
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

if __name__ == "__main__":
    #Teste simples
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python cliente.py <ip_servidor>")
        sys.exit(1)
    
    ip_servidor = sys.argv[1]
    
    print(f"Testando servidor em {ip_servidor}:{PORTA_SERVIDOR}")
    
    cliente = ClienteHTTP(ip_servidor)
    
    #Teste básico
    print("Executando teste básico...")
    resultado = cliente.enviar_requisicao('GET', '/')
    print(f"Resultado: {resultado}")
    
    #Teste de carga simples
    print("\nExecutando teste de carga...")
    testador = TestadorCarga(ip_servidor)
    resultado_carga = testador.teste_concorrente(5, 2, 'GET', '/rapido')
    print(f"Resumo do teste: {resultado_carga['resumo']}")
