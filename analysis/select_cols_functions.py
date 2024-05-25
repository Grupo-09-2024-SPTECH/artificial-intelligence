import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Removendo IDs
def remove_ids(df):
    # Identificar colunas com apenas valores únicos (como IDs)
    colunas_unicas = [coluna for coluna in df.columns if df[coluna].nunique() == len(df)]

    # Remover as colunas com valores únicos
    dados_processados = df.drop(columns=colunas_unicas)
    return dados_processados

# Removendo colunas muito variadas (Descrições, Nomes)
def remove_variable_columns(df):
    # Definir o limiar para o número de valores únicos em relação ao tamanho do conjunto de dados
    limiar_valores_unicos = 0.5  # Por exemplo, 50% dos valores únicos

    # Identificar colunas descritivas com muitos valores únicos
    colunas_descritivas = [coluna for coluna in df.columns if df[coluna].nunique() / len(df) > limiar_valores_unicos]

    # Remover as colunas descritivas
    dados_processados = df.drop(columns=colunas_descritivas)
    return dados_processados

# Ajustando valores categóricos
def adjust_categoric_values(df):
    
    # Selecionar dinamicamente as colunas categóricas
    colunas_categoricas = df.select_dtypes(include=['object']).columns

    # Inicializar o LabelEncoder
    label_encoder = LabelEncoder()

    # Iterar sobre as colunas categóricas e aplicar LabelEncoder em cada uma
    for coluna in colunas_categoricas:
        df[coluna] = label_encoder.fit_transform(df[coluna])
    
    return df

# Aplicando todas as regras
def apply_all_rules(df):
    df = remove_ids(df)
    df = remove_variable_columns(df)
    df = adjust_categoric_values(df)
    return df