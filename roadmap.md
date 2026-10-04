# Roadmap do Projeto — Analisador Inteligente de KPIs e Métricas

# ETAPA 1 — Ambiente do Projeto

## Objetivos

- Criar repositório do projeto no GitHub;
- Criar ambiente virtual Python;
- Estruturar as pastas e arquitetura do projeto;
- Criar `requirements.txt`;
- Instalar as dependências;
- Criar arquivo `.env`;
- Configurar a chave da Gemini API;
- Criar aplicação inicial em Streamlit.

## Dependências

```text
streamlit
google-generativeai
python-dotenv
pandas
openpyxl
sqlalchemy
```

## Estrutura inicial

```text
kpi-business-analyzer/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── services/
│
├── analyzers/
│
├── prompts/
│
├── models/
│
├── database/
│
└── utils/
```

## Resultado esperado

Projeto configurado e executando localmente através do Streamlit.

```bash
streamlit run app.py
```

---

# ETAPA 2 — Criar Interface Básica

## Objetivo

Desenvolver a primeira versão da interface utilizando Streamlit.

A interface deverá permitir que o usuário carregue um arquivo contendo os dados dos indicadores de negócio.

## Interface

```text
┌─────────────────────────────────────────┐
│       📊 KPI Business Analyzer          │
│                                         │
│ Analise seus indicadores utilizando IA  │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📁 Upload CSV ou Excel              │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [ 🔍 Analisar indicadores ]             │
│                                         │
└─────────────────────────────────────────┘
```

## Elementos

- Título da aplicação;
- Descrição;
- Campo para upload;
- Botão para iniciar análise;
- Área para apresentação dos resultados.

## Resultado esperado

Ter:

- Interface funcionando;
- Upload disponível;
- Inputs organizados;
- Botão de análise funcionando.

---

# ETAPA 3 — Upload e Leitura dos Arquivos

## Objetivo

Implementar o processamento dos arquivos enviados pelo usuário.

O sistema deverá aceitar arquivos:

```text
.csv
.xlsx
.xls
```

## Fluxo

```text
Upload
   ↓
Identificação do formato
   ↓
Leitura com Pandas
   ↓
DataFrame
   ↓
Validação
   ↓
Dados disponíveis para análise
```

## `services/data_service.py`

Responsável por:

```text
ler_csv()
ler_excel()
validar_arquivo()
validar_dataframe()
```

## Exemplo

```python
import pandas as pd


def read_file(file):

    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)

    raise ValueError("Formato não suportado")
```

## Resultado esperado

O usuário poderá carregar um arquivo e visualizar uma prévia dos dados.

Exemplo:

```text
Arquivo: vendas.xlsx

Registros: 1.250

Colunas:

Data
Canal
Leads
Vendas
Conversão
Faturamento
```

---

# ETAPA 4 — Análise dos KPIs

## Objetivo

Criar a primeira camada de análise dos indicadores de negócio.

O sistema deverá analisar os dados antes de enviá-los para a Gemini API.

## Responsabilidades

Identificar:

- KPIs disponíveis;
- Crescimento;
- Queda;
- Variação percentual;
- Valores máximos;
- Valores mínimos;
- Tendências;
- Possíveis anomalias.

## Exemplo

```text
Faturamento

Período anterior: R$ 125.000
Período atual:    R$ 98.000

Variação: -21,6%

Status: 🔴 Queda significativa
```

## `analyzers/kpi_analyzer.py`

Possíveis funções:

```python
calculate_variation()

identify_kpis()

compare_periods()

calculate_average()

detect_decline()
```

## Resultado esperado

O sistema consegue identificar automaticamente quais indicadores apresentam alterações relevantes e precisam de atenção.

---

# ETAPA 5 — Integrar Gemini API

## Objetivo

Conectar a aplicação com a Gemini API.

## `services/gemini_service.py`

Responsável por:

```text
Configurar API
      ↓
Receber prompt
      ↓
Enviar para Gemini
      ↓
Receber resposta
      ↓
Retornar diagnóstico
```

## Fluxo

```text
KPI Analyzer
     ↓
Dados relevantes
     ↓
Gemini Service
     ↓
Gemini API
     ↓
Diagnóstico
```

## Primeiro teste

Utilizar inicialmente um prompt simples:

```text
Analise os seguintes indicadores de negócio:

Faturamento: -21%
Conversão: -15%
Vendas: -12%

Identifique os principais problemas.
```

## Resultado esperado

A Gemini API retorna uma análise dentro da interface Streamlit.

---

# ETAPA 6 — Criar Prompt Dinâmico

## Objetivo

Criar prompts personalizados utilizando os dados reais enviados pelo usuário.

## Informações utilizadas

O prompt deverá considerar:

```text
Dados analisados
KPIs
Variações
Período
Anomalias
Contexto do negócio
```

## `prompts/business_diagnostic_prompt.py`

Estrutura inicial:

```text
Você é um consultor especialista em análise de negócios.

Analise os seguintes indicadores:

[KPI 1]
[KPI 2]
[KPI 3]

Identifique:

1. Principais problemas
2. KPIs críticos
3. Anomalias
4. Possíveis causas-raiz
5. Relação entre os indicadores
6. Impacto no negócio
7. Plano de ação

Apresente a resposta de forma objetiva e estruturada.
```

## Fluxo

```text
Arquivo
   ↓
Pandas
   ↓
KPI Analyzer
   ↓
Dados relevantes
   ↓
build_prompt()
   ↓
Gemini
```

## Resultado esperado

Os diagnósticos passam a ser personalizados de acordo com os dados enviados pelo usuário.

---

# ETAPA 7 — Adicionar SQLite

## Objetivo

Salvar as análises realizadas pela aplicação.

## Informações armazenadas

```text
id
nome_arquivo
data_analise
kpi_principal
variacao
diagnostico
causas
plano_acao
```

## Modelo

```text
business_analysis
│
├── id
├── filename
├── created_at
├── main_kpi
├── variation
├── diagnosis
├── root_causes
└── action_plan
```

## Fluxo

```text
Gemini
   ↓
Diagnóstico
   ↓
Database Service
   ↓
SQLite
```

## Resultado esperado

As análises realizadas ficam armazenadas no banco de dados.

---

# ETAPA 8 — Exibir Histórico de Análises

## Objetivo

Permitir que o usuário consulte diagnósticos realizados anteriormente.

## Interface

```text
📊 Dashboard

Nova análise

📚 Histórico
------------------------
01/10/2026
Queda de faturamento

28/09/2026
Queda de conversão

25/09/2026
Aumento de churn
```

## Funcionalidades

- Listar análises;
- Visualizar diagnóstico;
- Visualizar KPIs;
- Visualizar plano de ação;
- Ordenar análises por data.

## Resultado esperado

O usuário consegue consultar análises anteriores sem precisar reenviar os arquivos.

---

# ETAPA 9 — Melhorar UX/UI

## Objetivo

Melhorar a experiência do usuário e deixar a aplicação mais organizada e profissional.

## Melhorias

### Loading

```python
with st.spinner("Analisando seus indicadores..."):
    ...
```

### Cards de KPI

```text
┌──────────────┐
│ Faturamento  │
│ R$ 98.000    │
│ ↓ -21,6%     │
└──────────────┘
```

### Status

```text
🟢 Normal
🟡 Atenção
🔴 Crítico
```

### Organização da resposta

```text
📊 Indicadores

⚠️ Anomalias

🔎 Diagnóstico

🎯 Causas prováveis

🚀 Plano de ação
```

## Resultado esperado

Aplicação mais clara, organizada e profissional.

---

# ETAPA 10 — Otimização de Tokens e Custos

## Objetivo

Reduzir o consumo desnecessário da Gemini API.

## Estratégias

### Limitar dados enviados

Evitar enviar a planilha completa para a IA quando não for necessário.

```text
CSV completo
     ↓
Pandas
     ↓
KPI Analyzer
     ↓
Informações relevantes
     ↓
Gemini
```

### Limitar saída

Definir limite de tokens para a resposta da Gemini.

### Reutilizar análises

Antes de realizar uma nova chamada:

```text
Existe análise equivalente no banco?
          ↓
       SIM → reutilizar
          ↓
       NÃO
          ↓
      Gemini API
```

## Resultado esperado

```text
Menos requisições
        +
Menos tokens
        +
Menor custo
```

---

# ETAPA 11 — Testes e Validações

## Objetivo

Garantir que o MVP funcione corretamente antes da publicação.

## Testes de arquivos

Validar:

```text
CSV válido
Excel válido
Arquivo vazio
Arquivo inválido
Colunas ausentes
Valores nulos
Valores não numéricos
```

## Testes do KPI Analyzer

Validar:

```text
Variação positiva
Variação negativa
Sem variação
Queda significativa
Aumento significativo
```

## Testes da Gemini API

Validar:

```text
API funcionando
API indisponível
API Key inválida
Resposta vazia
Erro de conexão
```

## Testes SQLite

Validar:

```text
Salvar análise
Consultar análise
Listar histórico
```

## Resultado esperado

MVP validado e preparado para publicação.

---

# ETAPA 12 — Deploy

## Objetivo

Disponibilizar a aplicação para utilização externa.

## Fluxo

```text
GitHub
   ↓
Deploy
   ↓
Streamlit
   ↓
Aplicação online
```

## Validações antes do deploy

```text
.env não está no Git
        ↓
API Key protegida
        ↓
requirements.txt atualizado
        ↓
README atualizado
        ↓
Testes realizados
```

## Resultado esperado

Aplicação disponível através de uma URL pública.