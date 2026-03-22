# Impacto da Selic nos Fundos de Renda Fixa (2019-2022)

Este repositório contém o código e os dados utilizados para a análise de regressão linear do TCC sobre a associação entre a taxa Selic e o patrimônio líquido dos fundos de renda fixa no Brasil.

## 📊 Objetivo
O objetivo do estudo é verificar se existe associação estatística entre a taxa Selic e o patrimônio líquido dos fundos de renda fixa, controlando pelo IPCA (inflação).

## 📂 Estrutura do Projeto
- `data/`: Contém os dados brutos obtidos do Banco Central (BCB) e ANBIMA.
- `scripts/`: Contém os scripts Python para análise e inspeção.
  - `regressao_tcc.py`: Script principal da análise.
  - `inspect_excel.py`: Auxiliar para inspeção de planilhas.
- `results/`: Contém os gráficos gerados (`grafico_*.png`).
- `requirements.txt`: Lista de dependências do projeto.
- `README.md`: Documentação geral.

## ⚙️ Pré-requisitos
Para rodar o código, é necessário ter o Python instalado com as seguintes bibliotecas:
```bash
pip install pandas statsmodels matplotlib seaborn openpyxl
```

## 🚀 Como Rodar o Projeto (Tutorial)

Siga os passos abaixo para executar a análise localmente após o clone:

1. **Clone o repositório**:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd "Dados TCC"
   ```

2. **Instale as dependências**:
   Certifique-se de ter o Python instalado. Em seguida, instale as bibliotecas necessárias:
   ```bash
   pip install pandas statsmodels matplotlib seaborn openpyxl
   ```

3. **Execute a análise**:
   O script principal é o `regressao_tcc.py`. Ele utiliza caminhos dinâmicos, então funcionará automaticamente em qualquer diretório (Windows ou Linux):
   ```bash
   python regressao_tcc.py
   ```

4. **Verifique os resultados**:
   O sumário estatístico será exibido no terminal e dois arquivos de imagem com os gráficos serão gerados na pasta raiz.

## 📉 Resultados e Rigor Estatístico
O projeto foi aprimorado com técnicas avançadas para atender exigências de bancas de TCC:
- **Testes de Estacionariedade (ADF):** Verificação de raiz unitária para evitar regressões espúrias.
- **Erros-Padrão Robustos (HAC/Newey-West):** Correção de autocorrelação nos resíduos (Durbin-Watson baixo), garantindo que os p-valores sejam confiáveis.
- **Resultados:** O modelo confirmou um impacto positivo e estatisticamente significativo da taxa Selic no patrimônio líquido dos fundos (p < 0.001), mesmo com a correção HAC.

---
*Projeto desenvolvido para fins acadêmicos (TCC).*
