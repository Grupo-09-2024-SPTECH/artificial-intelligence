import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Função para remover colunas que provavelmente são IDs
def remove_ids(df):
    # Identifica colunas que possuem valores únicos em todas as linhas, geralmente indicativas de IDs
    colunas_unicas = [coluna for coluna in df.columns if df[coluna].nunique() == len(df)]

    # Remove as colunas identificadas como IDs
    dados_processados = df.drop(columns=colunas_unicas)
    return dados_processados

# Função para remover colunas com alta variabilidade, como descrições ou nomes
def remove_variable_columns(df):
    # Define o limite para o número de valores únicos em uma coluna, relativo ao tamanho do DataFrame
    limiar_valores_unicos = 0.7  # Exemplo: remove colunas onde mais de 70% dos valores são únicos

    # Identifica colunas que excedem o limite de valores únicos, geralmente descritivas
    colunas_descritivas = [coluna for coluna in df.columns if df[coluna].nunique() / len(df) > limiar_valores_unicos]

    # Remove as colunas descritivas identificadas
    dados_processados = df.drop(columns=colunas_descritivas)
    return dados_processados

# Função para ajustar valores categóricos
def adjust_categoric_values(df):
    
    # Seleciona dinamicamente as colunas categóricas do DataFrame
    colunas_categoricas = df.select_dtypes(include=['object']).columns

    # Inicializa o LabelEncoder, que converterá valores categóricos em valores numéricos
    label_encoder = LabelEncoder()

    # Itera sobre as colunas categóricas e aplica o LabelEncoder em cada uma
    for coluna in colunas_categoricas:
        df[coluna] = label_encoder.fit_transform(df[coluna])
    
    return df

# Função para aplicar todas as regras de limpeza e ajuste de dados
def apply_all_rules(df):
    # Aplica a remoção de colunas de IDs
    df = remove_ids(df)
    # Aplica a remoção de colunas com alta variabilidade
    df = remove_variable_columns(df)
    # Ajusta as colunas categóricas
    df = adjust_categoric_values(df)
    return df