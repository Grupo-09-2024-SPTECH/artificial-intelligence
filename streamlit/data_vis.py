import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector
import env  # Importa o arquivo env.py para as credenciais do banco de dados

# ------------------ BANCO -----------------------
conn = mysql.connector.connect(
    host=env.DB_HOST,
    user=env.DB_USER,
    password=env.DB_PASSWORD,
    database=env.DB_NAME
)

cursor = conn.cursor()
query = "SELECT * FROM vw_modelo_desempenho"
cursor.execute(query)
rows = cursor.fetchall()
columns = [i[0] for i in cursor.description]
df_original = pd.DataFrame(rows, columns=columns)

# Fechar a conexão
cursor.close()
conn.close()

# Aplicar ajustes no DataFrame, se necessário
df = df_original.copy()
df['nome_modelo'] = df['nome_modelo'].replace('Decision Tree (Entropy)', 'Decision Tree') 
df['nome_modelo'] = df['nome_modelo'].replace('SVC Linear - gamma Scale', 'SVC Linear')

# --------------- Criar Filtros ---------------
# Filtro para a coluna 'nome_modelo'
modelos_disponiveis = df['nome_modelo'].unique()

# Iniciar com apenas um modelo selecionado (primeiro da lista)
modelo_inicial = [modelos_disponiveis[0]] if len(modelos_disponiveis) > 0 else []

modelos_selecionados = st.multiselect('Selecione o(s) modelo(s):', modelos_disponiveis, default=modelo_inicial)

# Filtro para a coluna 'nome_base'
bases_disponiveis = df['nome_base'].unique()
base_selecionada = st.selectbox('Selecione a base:', bases_disponiveis)

parametros_selecionados = {}
for modelo in modelos_selecionados:
    # Obter os valores únicos de `vl_parametro` para o modelo selecionado
    valores_parametro = df[df['nome_modelo'] == modelo]['vl_parametro'].unique()
    # Usar select para selecionar um único parâmetro
    parametros_selecionados[modelo] = st.selectbox(f'Selecione um parâmetro para {modelo}:', valores_parametro)

# Aplicar Filtros ao DataFrame
df_filtrado = df[
    (df['nome_modelo'].isin(modelos_selecionados)) &
    (df['nome_base'] == base_selecionada) &
    (df.apply(lambda x: x['nome_modelo'] in parametros_selecionados and x['vl_parametro'] == parametros_selecionados[x['nome_modelo']], axis=1))
]


# --------------- Checkbox para Seleção de Métricas ---------------
st.write("Selecione as métricas que deseja visualizar:")

# Lista das métricas disponíveis
metricas = ['vl_accuracy', 'vl_f1_score', 'vl_precision', 'vl_recall']
metricas_selecionadas = []

# Loop para gerar um checkbox para cada métrica
for metrica in metricas:
    if st.checkbox(metrica, value=True):
        metricas_selecionadas.append(metrica)

# --------------- Gráficos Separados por Classe ---------------
if metricas_selecionadas and not df_filtrado.empty:
    # Obter as classes únicas
    classes_unicas = df_filtrado['tp_classe'].unique()
    
    for classe in classes_unicas:
        st.write(f"## Gráfico para a Classe: {classe}")
        # Filtrar pelo tipo de classe
        df_classe = df_filtrado[df_filtrado['tp_classe'] == classe]

        # Configurar o tamanho do gráfico
        plt.figure(figsize=(12, 6))
        
        # Definir posição e largura das barras
        n_metricas = len(metricas_selecionadas)
        largura_barras = 0.2
        posicoes = list(range(len(df_classe['nome_modelo'].unique())))  # Número de modelos únicos

        # Desenhar as barras para cada métrica
        for i, metrica in enumerate(metricas_selecionadas):
            barras = plt.bar(
                [p + i * largura_barras for p in posicoes], 
                df_classe.groupby('nome_modelo')[metrica].mean(),  # Média da métrica para cada modelo
                width=largura_barras
            )

            # Adicionar os valores acima das barras
            for barra in barras:
                yval = barra.get_height()  # Altura da barra
                plt.text(
                    barra.get_x() + barra.get_width() / 2,  # Posição x (centro da barra)
                    yval,  # Posição y (altura da barra)
                    round(yval, 2),  # Valor a ser exibido (arredondado a 2 casas decimais)
                    ha='center',  # Alinhamento horizontal
                    va='bottom'   # Alinhamento vertical
                )

        # Configurar o eixo x com os nomes dos modelos
        plt.xticks([p + largura_barras * (n_metricas - 1) / 2 for p in posicoes], df_classe['nome_modelo'].unique())

        # Exibir os parâmetros selecionados para cada modelo no título
        parametros_str = ', '.join([f"{modelo}: {parametros_selecionados[modelo]}" for modelo in modelos_selecionados])
        
        # Legenda e rótulos
        plt.xlabel('Modelos')
        plt.ylabel('Valor da Métrica')
        plt.title(f'Comparação de Métricas para Modelos Selecionados - Parâmetros: {parametros_str} - Classe: {classe}')
        plt.legend(metricas_selecionadas, loc='upper left', bbox_to_anchor=(1, 1))

        # Exibir gráfico no Streamlit
        st.pyplot(plt.gcf())