"""
Script para gerar gráficos e análises dos resultados dos testes
"""
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import os

class ResultsAnalyzer:
    def __init__(self, results_file='/app/results/test_results.json'):
        self.results_file = results_file
        self.results = None
        self.load_results()
        
    def load_results(self):
        """Carrega os resultados dos testes"""
        try:
            with open(self.results_file, 'r') as f:
                self.results = json.load(f)
            print(f"Resultados carregados de {self.results_file}")
        except FileNotFoundError:
            print(f"Arquivo de resultados não encontrado: {self.results_file}")
            self.results = None
        except Exception as e:
            print(f"Erro ao carregar resultados: {e}")
            self.results = None
    
    def generate_all_plots(self):
        """Gera todos os gráficos de análise"""
        if not self.results:
            print("Nenhum resultado disponível para análise")
            return
        
        # Configura o estilo dos gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Cria diretório para gráficos
        os.makedirs('/app/results/plots', exist_ok=True)
        
        print("Gerando gráficos...")
        
        # 1. Comparação de tempo de resposta
        self.plot_response_time_comparison()
        
        # 2. Taxa de sucesso
        self.plot_success_rate_comparison()
        
        # 3. Escalabilidade por número de clientes
        self.plot_scalability_analysis()
        
        # 4. Comparação por cenário
        self.plot_scenario_comparison()
        
        # 5. Análise estatística detalhada
        self.plot_statistical_analysis()
        
        print("Gráficos salvos em /app/results/plots/")
    
    def plot_response_time_comparison(self):
        """Gráfico de comparação de tempo de resposta"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Comparação de Tempo de Resposta - Servidor Sequencial vs Concorrente', fontsize=16)
        
        scenarios = ['fast', 'medium', 'slow']
        scenario_names = ['Rápido', 'Médio (0.5s)', 'Lento (2s)']
        
        for idx, (scenario, scenario_name) in enumerate(zip(scenarios, scenario_names)):
            ax = axes[idx]
            
            # Dados para cada servidor
            clients = []
            seq_times = []
            seq_errors = []
            conc_times = []
            conc_errors = []
            
            for num_clients in sorted([int(k) for k in self.results['results']['sequential'][scenario].keys()]):
                clients.append(num_clients)
                
                # Servidor sequencial
                seq_data = self.results['results']['sequential'][scenario][str(num_clients)]
                seq_times.append(seq_data['response_time_mean'])
                seq_errors.append(seq_data['response_time_std'])
                
                # Servidor concorrente
                conc_data = self.results['results']['concurrent'][scenario][str(num_clients)]
                conc_times.append(conc_data['response_time_mean'])
                conc_errors.append(conc_data['response_time_std'])
            
            # Plota os dados
            x = np.arange(len(clients))
            width = 0.35
            
            ax.bar(x - width/2, seq_times, width, label='Sequencial', 
                   yerr=seq_errors, capsize=5, alpha=0.8)
            ax.bar(x + width/2, conc_times, width, label='Concorrente', 
                   yerr=conc_errors, capsize=5, alpha=0.8)
            
            ax.set_title(f'Cenário {scenario_name}')
            ax.set_xlabel('Número de Clientes')
            ax.set_ylabel('Tempo de Resposta (s)')
            ax.set_xticks(x)
            ax.set_xticklabels(clients)
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/app/results/plots/response_time_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_success_rate_comparison(self):
        """Gráfico de comparação de taxa de sucesso"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Comparação de Taxa de Sucesso - Servidor Sequencial vs Concorrente', fontsize=16)
        
        scenarios = ['fast', 'medium', 'slow']
        scenario_names = ['Rápido', 'Médio (0.5s)', 'Lento (2s)']
        
        for idx, (scenario, scenario_name) in enumerate(zip(scenarios, scenario_names)):
            ax = axes[idx]
            
            # Dados para cada servidor
            clients = []
            seq_success = []
            seq_errors = []
            conc_success = []
            conc_errors = []
            
            for num_clients in sorted([int(k) for k in self.results['results']['sequential'][scenario].keys()]):
                clients.append(num_clients)
                
                # Servidor sequencial
                seq_data = self.results['results']['sequential'][scenario][str(num_clients)]
                seq_success.append(seq_data['success_rate_mean'] * 100)
                seq_errors.append(seq_data['success_rate_std'] * 100)
                
                # Servidor concorrente
                conc_data = self.results['results']['concurrent'][scenario][str(num_clients)]
                conc_success.append(conc_data['success_rate_mean'] * 100)
                conc_errors.append(conc_data['success_rate_std'] * 100)
            
            # Plota os dados
            x = np.arange(len(clients))
            width = 0.35
            
            ax.bar(x - width/2, seq_success, width, label='Sequencial', 
                   yerr=seq_errors, capsize=5, alpha=0.8)
            ax.bar(x + width/2, conc_success, width, label='Concorrente', 
                   yerr=conc_errors, capsize=5, alpha=0.8)
            
            ax.set_title(f'Cenário {scenario_name}')
            ax.set_xlabel('Número de Clientes')
            ax.set_ylabel('Taxa de Sucesso (%)')
            ax.set_xticks(x)
            ax.set_xticklabels(clients)
            ax.set_ylim(0, 105)
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/app/results/plots/success_rate_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_scalability_analysis(self):
        """Análise de escalabilidade"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Análise de Escalabilidade', fontsize=16)
        
        # Prepara dados
        data = []
        for server_type in ['sequential', 'concurrent']:
            for scenario in ['fast', 'medium', 'slow']:
                for num_clients in self.results['results'][server_type][scenario]:
                    stats = self.results['results'][server_type][scenario][num_clients]
                    data.append({
                        'server_type': server_type,
                        'scenario': scenario,
                        'num_clients': int(num_clients),
                        'response_time': stats['response_time_mean'],
                        'success_rate': stats['success_rate_mean'],
                        'throughput': stats['successful_requests_mean'] / stats['response_time_mean'] if stats['response_time_mean'] > 0 else 0
                    })
        
        df = pd.DataFrame(data)
        
        # Gráfico 1: Tempo de resposta vs número de clientes
        ax1 = axes[0, 0]
        for scenario in ['fast', 'medium', 'slow']:
            scenario_data = df[df['scenario'] == scenario]
            for server_type in ['sequential', 'concurrent']:
                server_data = scenario_data[scenario_data['server_type'] == server_type]
                ax1.plot(server_data['num_clients'], server_data['response_time'], 
                        marker='o', label=f'{server_type.title()} - {scenario}')
        
        ax1.set_xlabel('Número de Clientes')
        ax1.set_ylabel('Tempo de Resposta (s)')
        ax1.set_title('Escalabilidade: Tempo de Resposta')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Taxa de sucesso vs número de clientes
        ax2 = axes[0, 1]
        for scenario in ['fast', 'medium', 'slow']:
            scenario_data = df[df['scenario'] == scenario]
            for server_type in ['sequential', 'concurrent']:
                server_data = scenario_data[scenario_data['server_type'] == server_type]
                ax2.plot(server_data['num_clients'], server_data['success_rate'], 
                        marker='s', label=f'{server_type.title()} - {scenario}')
        
        ax2.set_xlabel('Número de Clientes')
        ax2.set_ylabel('Taxa de Sucesso')
        ax2.set_title('Escalabilidade: Taxa de Sucesso')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Throughput
        ax3 = axes[1, 0]
        for scenario in ['fast', 'medium', 'slow']:
            scenario_data = df[df['scenario'] == scenario]
            for server_type in ['sequential', 'concurrent']:
                server_data = scenario_data[scenario_data['server_type'] == server_type]
                ax3.plot(server_data['num_clients'], server_data['throughput'], 
                        marker='^', label=f'{server_type.title()} - {scenario}')
        
        ax3.set_xlabel('Número de Clientes')
        ax3.set_ylabel('Throughput (req/s)')
        ax3.set_title('Escalabilidade: Throughput')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Heatmap de performance
        ax4 = axes[1, 1]
        pivot_data = df.pivot_table(values='response_time', 
                                   index=['server_type', 'scenario'], 
                                   columns='num_clients')
        sns.heatmap(pivot_data, annot=True, fmt='.3f', ax=ax4, cmap='YlOrRd')
        ax4.set_title('Heatmap: Tempo de Resposta')
        
        plt.tight_layout()
        plt.savefig('/app/results/plots/scalability_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_scenario_comparison(self):
        """Comparação por cenário"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Comparação Detalhada por Cenário', fontsize=16)
        
        # Dados agregados
        scenarios = ['fast', 'medium', 'slow']
        server_types = ['sequential', 'concurrent']
        
        # Gráfico 1: Tempo médio por cenário
        ax1 = axes[0, 0]
        scenario_means = {}
        for scenario in scenarios:
            scenario_means[scenario] = {}
            for server_type in server_types:
                times = []
                for num_clients in self.results['results'][server_type][scenario]:
                    times.append(self.results['results'][server_type][scenario][num_clients]['response_time_mean'])
                scenario_means[scenario][server_type] = np.mean(times)
        
        x = np.arange(len(scenarios))
        width = 0.35
        
        seq_means = [scenario_means[s]['sequential'] for s in scenarios]
        conc_means = [scenario_means[s]['concurrent'] for s in scenarios]
        
        ax1.bar(x - width/2, seq_means, width, label='Sequencial', alpha=0.8)
        ax1.bar(x + width/2, conc_means, width, label='Concorrente', alpha=0.8)
        ax1.set_xlabel('Cenário')
        ax1.set_ylabel('Tempo Médio de Resposta (s)')
        ax1.set_title('Tempo Médio por Cenário')
        ax1.set_xticks(x)
        ax1.set_xticklabels(['Rápido', 'Médio', 'Lento'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Eficiência relativa
        ax2 = axes[0, 1]
        efficiency = []
        for scenario in scenarios:
            seq_time = scenario_means[scenario]['sequential']
            conc_time = scenario_means[scenario]['concurrent']
            if conc_time > 0:
                efficiency.append(seq_time / conc_time)
            else:
                efficiency.append(0)
        
        colors = ['green' if e > 1 else 'red' for e in efficiency]
        ax2.bar(scenarios, efficiency, color=colors, alpha=0.7)
        ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Cenário')
        ax2.set_ylabel('Eficiência Relativa (Seq/Conc)')
        ax2.set_title('Eficiência: Sequencial vs Concorrente')
        ax2.set_xticklabels(['Rápido', 'Médio', 'Lento'])
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Variabilidade (desvio padrão)
        ax3 = axes[1, 0]
        scenario_stds = {}
        for scenario in scenarios:
            scenario_stds[scenario] = {}
            for server_type in server_types:
                stds = []
                for num_clients in self.results['results'][server_type][scenario]:
                    stds.append(self.results['results'][server_type][scenario][num_clients]['response_time_std'])
                scenario_stds[scenario][server_type] = np.mean(stds)
        
        seq_stds = [scenario_stds[s]['sequential'] for s in scenarios]
        conc_stds = [scenario_stds[s]['concurrent'] for s in scenarios]
        
        ax3.bar(x - width/2, seq_stds, width, label='Sequencial', alpha=0.8)
        ax3.bar(x + width/2, conc_stds, width, label='Concorrente', alpha=0.8)
        ax3.set_xlabel('Cenário')
        ax3.set_ylabel('Desvio Padrão Médio (s)')
        ax3.set_title('Variabilidade por Cenário')
        ax3.set_xticks(x)
        ax3.set_xticklabels(['Rápido', 'Médio', 'Lento'])
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Taxa de sucesso por cenário
        ax4 = axes[1, 1]
        scenario_success = {}
        for scenario in scenarios:
            scenario_success[scenario] = {}
            for server_type in server_types:
                success_rates = []
                for num_clients in self.results['results'][server_type][scenario]:
                    success_rates.append(self.results['results'][server_type][scenario][num_clients]['success_rate_mean'])
                scenario_success[scenario][server_type] = np.mean(success_rates) * 100
        
        seq_success = [scenario_success[s]['sequential'] for s in scenarios]
        conc_success = [scenario_success[s]['concurrent'] for s in scenarios]
        
        ax4.bar(x - width/2, seq_success, width, label='Sequencial', alpha=0.8)
        ax4.bar(x + width/2, conc_success, width, label='Concorrente', alpha=0.8)
        ax4.set_xlabel('Cenário')
        ax4.set_ylabel('Taxa de Sucesso Média (%)')
        ax4.set_title('Taxa de Sucesso por Cenário')
        ax4.set_xticks(x)
        ax4.set_xticklabels(['Rápido', 'Médio', 'Lento'])
        ax4.set_ylim(0, 105)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/app/results/plots/scenario_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_statistical_analysis(self):
        """Análise estatística detalhada"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Análise Estatística Detalhada', fontsize=16)
        
        # Prepara dados para boxplots
        data_for_analysis = []
        for server_type in ['sequential', 'concurrent']:
            for scenario in ['fast', 'medium', 'slow']:
                for num_clients in self.results['results'][server_type][scenario]:
                    stats = self.results['results'][server_type][scenario][num_clients]
                    data_for_analysis.append({
                        'server_type': server_type,
                        'scenario': scenario,
                        'num_clients': int(num_clients),
                        'response_time_mean': stats['response_time_mean'],
                        'response_time_std': stats['response_time_std'],
                        'success_rate_mean': stats['success_rate_mean']
                    })
        
        df = pd.DataFrame(data_for_analysis)
        
        # Boxplot 1: Distribuição de tempos de resposta
        ax1 = axes[0, 0]
        sns.boxplot(data=df, x='scenario', y='response_time_mean', hue='server_type', ax=ax1)
        ax1.set_title('Distribuição dos Tempos de Resposta')
        ax1.set_xlabel('Cenário')
        ax1.set_ylabel('Tempo de Resposta (s)')
        
        # Boxplot 2: Distribuição de desvios padrão
        ax2 = axes[0, 1]
        sns.boxplot(data=df, x='scenario', y='response_time_std', hue='server_type', ax=ax2)
        ax2.set_title('Distribuição dos Desvios Padrão')
        ax2.set_xlabel('Cenário')
        ax2.set_ylabel('Desvio Padrão (s)')
        
        # Scatter plot: Correlação entre clientes e tempo
        ax3 = axes[1, 0]
        for server_type in ['sequential', 'concurrent']:
            server_data = df[df['server_type'] == server_type]
            ax3.scatter(server_data['num_clients'], server_data['response_time_mean'], 
                       label=server_type.title(), alpha=0.7, s=60)
        
        ax3.set_xlabel('Número de Clientes')
        ax3.set_ylabel('Tempo de Resposta (s)')
        ax3.set_title('Correlação: Clientes vs Tempo de Resposta')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Violin plot: Distribuição detalhada
        ax4 = axes[1, 1]
        sns.violinplot(data=df, x='server_type', y='success_rate_mean', ax=ax4)
        ax4.set_title('Distribuição da Taxa de Sucesso')
        ax4.set_xlabel('Tipo de Servidor')
        ax4.set_ylabel('Taxa de Sucesso')
        
        plt.tight_layout()
        plt.savefig('/app/results/plots/statistical_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self):
        """Gera relatório em texto"""
        if not self.results:
            return
        
        report = []
        report.append("=== RELATÓRIO DE ANÁLISE DE PERFORMANCE ===")
        report.append(f"Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data dos testes: {self.results['timestamp']}")
        report.append("")
        
        # Configuração dos testes
        config = self.results['test_config']
        report.append("=== CONFIGURAÇÃO DOS TESTES ===")
        report.append(f"Iterações por teste: {config['iterations']}")
        report.append(f"Números de clientes testados: {config['client_counts']}")
        report.append(f"Requisições por cliente: {config['requests_per_client']}")
        report.append("")
        
        # Análise por cenário
        scenarios = ['fast', 'medium', 'slow']
        scenario_names = ['Rápido', 'Médio (0.5s)', 'Lento (2s)']
        
        for scenario, scenario_name in zip(scenarios, scenario_names):
            report.append(f"=== CENÁRIO: {scenario_name.upper()} ===")
            
            for num_clients in sorted([int(k) for k in self.results['results']['sequential'][scenario].keys()]):
                report.append(f"\nClientes simultâneos: {num_clients}")
                
                # Dados do servidor sequencial
                seq_data = self.results['results']['sequential'][scenario][str(num_clients)]
                report.append(f"  Servidor Sequencial:")
                report.append(f"    Tempo médio: {seq_data['response_time_mean']:.4f}s (±{seq_data['response_time_std']:.4f}s)")
                report.append(f"    Taxa de sucesso: {seq_data['success_rate_mean']:.2%} (±{seq_data['success_rate_std']:.2%})")
                
                # Dados do servidor concorrente
                conc_data = self.results['results']['concurrent'][scenario][str(num_clients)]
                report.append(f"  Servidor Concorrente:")
                report.append(f"    Tempo médio: {conc_data['response_time_mean']:.4f}s (±{conc_data['response_time_std']:.4f}s)")
                report.append(f"    Taxa de sucesso: {conc_data['success_rate_mean']:.2%} (±{conc_data['success_rate_std']:.2%})")
                
                # Comparação
                if conc_data['response_time_mean'] > 0:
                    speedup = seq_data['response_time_mean'] / conc_data['response_time_mean']
                    if speedup > 1:
                        report.append(f"    → Servidor concorrente é {speedup:.2f}x mais rápido")
                    else:
                        report.append(f"    → Servidor sequencial é {1/speedup:.2f}x mais rápido")
            
            report.append("")
        
        # Conclusões
        report.append("=== CONCLUSÕES ===")
        report.append("1. Performance Geral:")
        
        # Calcula médias gerais
        seq_avg = np.mean([
            self.results['results']['sequential'][scenario][str(num_clients)]['response_time_mean']
            for scenario in scenarios
            for num_clients in [1, 5, 10, 20, 50]
        ])
        
        conc_avg = np.mean([
            self.results['results']['concurrent'][scenario][str(num_clients)]['response_time_mean']
            for scenario in scenarios
            for num_clients in [1, 5, 10, 20, 50]
        ])
        
        if conc_avg > 0:
            overall_speedup = seq_avg / conc_avg
            if overall_speedup > 1:
                report.append(f"   - Servidor concorrente é em média {overall_speedup:.2f}x mais rápido")
            else:
                report.append(f"   - Servidor sequencial é em média {1/overall_speedup:.2f}x mais rápido")
        
        report.append("\n2. Recomendações:")
        report.append("   - Use servidor concorrente para alto volume de requisições simultâneas")
        report.append("   - Use servidor sequencial para processamento simples com poucos clientes")
        report.append("   - O servidor concorrente escala melhor com o aumento de clientes")
        
        # Salva relatório
        with open('/app/results/performance_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        print("Relatório salvo em /app/results/performance_report.txt")

if __name__ == "__main__":
    analyzer = ResultsAnalyzer()
    analyzer.generate_all_plots()
    analyzer.generate_report()
