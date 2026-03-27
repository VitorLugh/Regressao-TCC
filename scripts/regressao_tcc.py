import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

# --- 1. CONFIGURAÇÕES E CAMINHOS ---
# O script está em scripts/, então subimos um nível para acessar data/ e results/
base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.abspath(os.path.join(base_path, '..', 'data'))
results_path = os.path.abspath(os.path.join(base_path, '..', 'results'))

# Criar pasta results se não existir
if not os.path.exists(results_path):
    os.makedirs(results_path)

selic_file = os.path.join(data_path, 'SELIC-STP-20260321213426004.csv')
ipca_file = os.path.join(data_path, 'IPCA-STP-20260321213354533.csv')
imab_file = os.path.join(data_path, 'IMAB_2019_2022.csv')

excel_files = {
    2019: ('Anexo-Boletim-FI-201912.xlsx', 'Pag. 3 - PL por Classe'),
    '2020_2021': ('Anexo-Boletim-FI-202112.xlsx', 'Pag. 3 - PL por Classe'), # Este arquivo contém o histórico de 2020 e 2021 juntos
    2022: ('Anexo_boletim_fundos_investimento_dezembro_Valor.xlsx', 'Pág. 4 - PL por Classe')
}

print("Iniciando carregamento e limpeza de dados...")

# --- 2. CARREGAR SELIC (BCB) ---
# Separador ';' e decimal ',' conforme inspeção
selic = pd.read_csv(selic_file, sep=';', decimal=',', engine='python', encoding='latin1')
selic.columns = ['data', 'Selic']
# Usar errors='coerce' para lidar com rodapés como "Fonte;Copom"
selic['data'] = pd.to_datetime(selic['data'], dayfirst=True, errors='coerce')
selic['Selic'] = pd.to_numeric(selic['Selic'], errors='coerce')
selic.dropna(subset=['data', 'Selic'], inplace=True)
selic.set_index('data', inplace=True)
# Resampling para média mensal
selic_mensal = selic['Selic'].resample('MS').mean()

# --- 3. CARREGAR IPCA (BCB) ---
# Formato MM/YYYY;valor
ipca = pd.read_csv(ipca_file, sep=';', decimal=',', engine='python', encoding='latin1')
ipca.columns = ['data', 'IPCA']
# Ajustar formato MM/YYYY para datetime (primeiro dia do mês)
ipca['data'] = pd.to_datetime(ipca['data'], format='%m/%Y', errors='coerce')
ipca['IPCA'] = pd.to_numeric(ipca['IPCA'], errors='coerce')
ipca.dropna(subset=['data', 'IPCA'], inplace=True)
ipca.set_index('data', inplace=True)

# --- 3.5 CARREGAR IMA-B (ANBIMA) ---
imab = pd.read_csv(imab_file, sep=';', decimal=',', engine='python', encoding='latin1')
imab = imab[['Data de Referencia', 'Numero Indice']].copy()
imab.columns = ['data', 'IMAB']
imab['data'] = pd.to_datetime(imab['data'], errors='coerce')
imab['IMAB'] = pd.to_numeric(imab['IMAB'], errors='coerce')
imab.dropna(subset=['data', 'IMAB'], inplace=True)
imab.set_index('data', inplace=True)
# Resampling para média mensal
imab_mensal = imab['IMAB'].resample('MS').mean()

# --- 4. CARREGAR PATRIMÔNIO (ANBIMA) ---
dfs_anbima = []

# Extração de 2018-2019
f19, s19 = excel_files[2019]
df19 = pd.read_excel(os.path.join(data_path, f19), sheet_name=s19, skiprows=4)
# Renomear primeira coluna para data
df19.columns.values[0] = 'data'
rf_col19 = [c for c in df19.columns if 'Renda fixa' in str(c) or 'Renda Fixa' in str(c)][0]
df19 = df19[['data', rf_col19]].copy()
df19.columns = ['data', 'Patrimonio']
dfs_anbima.append(df19)

# Extração de 2020 e 2021 (O arquivo de 2021 já engloba todo o ano de 2020)
f20_21, s20_21 = excel_files['2020_2021']
df20_21 = pd.read_excel(os.path.join(data_path, f20_21), sheet_name=s20_21, skiprows=4)
df20_21.columns.values[0] = 'data'
rf_col20_21 = [c for c in df20_21.columns if 'Renda fixa' in str(c) or 'Renda Fixa' in str(c)][0]
df20_21 = df20_21[['data', rf_col20_21]].copy()
df20_21.columns = ['data', 'Patrimonio']
dfs_anbima.append(df20_21)

# Extração de 2022
f22, s22 = excel_files[2022]
df22 = pd.read_excel(os.path.join(data_path, f22), sheet_name=s22, skiprows=4)
df22.columns.values[0] = 'data'
rf_col22 = [c for c in df22.columns if 'Renda Fixa' in str(c) or 'Renda fixa' in str(c)][0]
df22 = df22[['data', rf_col22]].copy()
df22.columns = ['data', 'Patrimonio']
dfs_anbima.append(df22)

# Consolidar ANBIMA
anbima = pd.concat(dfs_anbima)
anbima['data'] = pd.to_datetime(anbima['data'], errors='coerce')
anbima.dropna(subset=['data', 'Patrimonio'], inplace=True)
anbima.set_index('data', inplace=True)

# Filtrar período 2019-2022
anbima = anbima.sort_index()
anbima = anbima.loc['2019-01-01':'2022-12-01']

# --- 5. JUNÇÃO DOS DADOS (MERGE) ---
df = pd.merge(selic_mensal, ipca, left_index=True, right_index=True)
df = pd.merge(df, imab_mensal, left_index=True, right_index=True)
df = pd.merge(df, anbima, left_index=True, right_index=True)

# Garantir que todos os dados sejam numéricos
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Limpeza final
df.dropna(inplace=True)
print("\nDados prontos para a regressão (primeiras 5 linhas):")
print(df.head())
print(f"Total de meses: {len(df)}")

# --- 6. ANÁLISE ESTATÍSTICA AVANÇADA (PARA A BANCA DO TCC) ---
from statsmodels.tsa.stattools import adfuller

print("\n" + "="*50)
print("       TESTES DE ESTACIONARIEDADE (ADF)")
print("="*50)
def test_stationarity(series, name):
    result = adfuller(series)
    print(f"Série: {name}")
    print(f"  Estatística ADF: {result[0]:.4f}")
    print(f"  p-valor: {result[1]:.4f}")
    if result[1] <= 0.05:
        print("  Resultado: Estacionária (p <= 0.05)")
    else:
        print("  Resultado: Não-Estacionária (p > 0.05) - Comum em séries nível")

test_stationarity(df['Patrimonio'], 'Patrimônio Líquido')
test_stationarity(df['Selic'], 'Taxa Selic')
test_stationarity(df['IPCA'], 'IPCA')
test_stationarity(df['IMAB'], 'IMA-B')

# --- 7. MODELAGEM OLS PRIMEIRA DIFERENÇA COM ERROS-PADRÃO ROBUSTOS (HAC) ---
# Transformando as variáveis em variação (primeira diferença)
df['Patrimonio_diff'] = df['Patrimonio'].diff()
df['Selic_diff'] = df['Selic'].diff()
df['IPCA_diff'] = df['IPCA'].diff()
df['IMAB_diff'] = df['IMAB'].diff()

# Removendo os valores NaN que surgem ao aplicar .diff()
df.dropna(inplace=True)

# Adicionar constante para o intercepto
X = sm.add_constant(df[['Selic_diff', 'IPCA_diff', 'IMAB_diff']])
y = df['Patrimonio_diff']

# Usando cov_type='HAC' (Newey-West) para corrigir autocorrelação nos resíduos
# maxlags=1 é uma escolha conservadora para dados mensais
modelo = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 1})

print("\n" + "="*50)
print("             SUMÁRIO DA REGRESSÃO (ROBUSTA HAC)")
print("="*50)
print(modelo.summary())

# --- Salvar Sumário da Regressão na pasta results ---
sumario_txt_path = os.path.join(results_path, 'sumario_regressao.txt')
with open(sumario_txt_path, 'w', encoding='utf-8') as f:
    f.write(modelo.summary().as_text())

sumario_csv_path = os.path.join(results_path, 'sumario_regressao.csv')
with open(sumario_csv_path, 'w', encoding='utf-8') as f:
    f.write(modelo.summary().as_csv())

print(f"\n[OK] Tabelas de resultados salvas em: {results_path}")


# --- 8. VISUALIZAÇÃO 1: DISPERSÃO E REGRESSÃO (ASSOCIAÇÃO ESTATÍSTICA) ---
import seaborn as sns
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

plt.figure(figsize=(12, 7))

# Regplot do Seaborn com a linha e IC (95% CI)
sns.regplot(x='Selic_diff', y='Patrimonio_diff', data=df, 
            scatter=False, 
            line_kws={'color':'red'}, 
            ci=95)

# Plotar os pontos manualmente com label
plt.scatter(df['Selic_diff'], df['Patrimonio_diff'], color='blue', alpha=0.6)

# Criar handles manuais para a legenda
blue_dot = mlines.Line2D([], [], color='blue', marker='o', linestyle='None',
                          markersize=8, alpha=0.6, label='Variação do Patrimônio Mensal')
red_line = mlines.Line2D([], [], color='red', label='Linha de Tendência OLS')
red_shadow = mpatches.Patch(color='red', alpha=0.2, label='Intervalo de Confiança (95%)')

# Adicionar legendas
plt.legend(handles=[blue_dot, red_line, red_shadow], loc='upper left', fontsize=10)

plt.title('Dispersão: Variação Selic vs. Variação Patrimônio Líquido\nCom Linha de Tendência e Margem de Confiança 95%', fontsize=14)
plt.xlabel('Variação da Taxa Selic (p.p.)', fontsize=12)
plt.ylabel('Variação do Patrimônio Líquido (milhões R$)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

# Salvar gráfico 1
scat_path = os.path.join(results_path, 'grafico_dispersao_regressao.png')
plt.savefig(scat_path)
print(f"\nGráfico de Dispersão salvo em: {scat_path}")


# --- 9. VISUALIZAÇÃO 2: SÉRIE TEMPORAL COM REGRESSÃO (DUPLO EIXO) ---
# Calcular valores previstos pelo modelo para comparação temporal
df['Patrimonio_diff_Previsto'] = modelo.predict(X)

fig, ax1 = plt.subplots(figsize=(12, 7))

# Eixo 1: Variação do Patrimônio Líquido (Observado e Previsto)
ax1.set_xlabel('Período (2019 - 2022)', fontsize=12)
ax1.set_ylabel('Variação do Patrimônio Líquido (R$ milhões)', color='blue', fontsize=12)

# Linha do observado
ax1.plot(df.index, df['Patrimonio_diff'], color='blue', linewidth=2, label='Variação Observada (Real)')
# Linha do previsto pela regressão
ax1.plot(df.index, df['Patrimonio_diff_Previsto'], color='green', linewidth=2, linestyle='--', label='Ajuste da Regressão (Modelo OLS)')

ax1.tick_params(axis='y', labelcolor='blue')
ax1.grid(True, linestyle='--', alpha=0.3)

# Criar o segundo eixo para a Variação da Selic
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Variação Taxa Selic (p.p.)', color=color, fontsize=12)
ax2.plot(df.index, df['Selic_diff'], color=color, linewidth=2, linestyle=':', label='Variação Selic (Variável Independente)')
ax2.tick_params(axis='y', labelcolor=color)

# Título e ajustes
plt.title('Evolução Temporal: Variação Selic vs. Variação Patrimônio Líquido\nComparação: Dados Reais vs. Modelo de Regressão (2019-2022)', fontsize=14)
fig.tight_layout()

# Combinar as legendas
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, shadow=True)

# Salvar gráfico 2
ts_path = os.path.join(results_path, 'grafico_evolucao_temporal.png')
plt.savefig(ts_path)
print(f"Gráfico de Evolução Temporal salvo em: {ts_path}")

# plt.show()
