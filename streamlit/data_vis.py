import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector

#
# ------------------ BANCO -----------------------
#
conn = mysql.connector.connect(
    host="adoptaidb.c9v2lvhlu1ya.us-east-1.rds.amazonaws.com",
    user="admin",
    password="urubu100",
    database="adoptaidb"
)

cursor = conn.cursor()

query = "SELECT * FROM vw_modelo_desempenho"
cursor.execute(query)

rows = cursor.fetchall()
columns = [i[0] for i in cursor.description]
df_original = pd.DataFrame(rows, columns=columns)

df = df_original

df['nome_modelo'] = df['nome_modelo'].replace('Decision Tree (Entropy)', 'Decision Tree') 
df['nome_modelo'] = df['nome_modelo'].replace('SVC Linear - gamma Scale', 'SVC Linear')

cursor.close()
conn.close()



#
# ------------------ Exibição Comparativa -----------------------
#
st.title('Modelos de Previsão de adoção')

st.subheader('Dados da View: vw_modelo_desempenho')
st.dataframe(df_original)

best_accuracy_df = df.loc[df.groupby('nome_modelo')['vl_accuracy'].idxmax()].reset_index(drop=True)

metrics = ['vl_accuracy', 'vl_precision', 'vl_recall', 'vl_f1_score']
metric_labels = ['Acurácia', 'Precisão', 'Recall', 'F1 Score']

metric_data = best_accuracy_df.set_index('nome_modelo')[metrics]

st.subheader('Melhores scores por Modelo')
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(14, 10))
fig.tight_layout(pad=5.0) 

for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
    ax = axs[i // 2, i % 2]
    bars = ax.bar(metric_data.index, metric_data[metric])
    ax.set_title(label)
    ax.set_xlabel('Modelos')
    ax.set_ylabel('Valor')
    ax.set_ylim(0, 1)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
        
st.pyplot(fig)


df['data_inicio'] = pd.to_datetime(df['dt_inicio_exec'])
df['data_fim'] = pd.to_datetime(df['dt_fim_exec'])


df['diferenca'] = df['dt_fim_exec'] - df['dt_inicio_exec']


df['horas'] = df['diferenca'].dt.components['hours']
df['minutos'] = df['diferenca'].dt.components['minutes']
df['segundos'] = df['diferenca'].dt.components['seconds']


df['tempo_execucao'] = df.apply(lambda row: f"{int(row['horas']):02}:{int(row['minutos']):02}:{int(row['segundos']):02}", axis=1)

def tempo_para_segundos(tempo_str):
    h, m, s = map(int, tempo_str.split(':'))
    return h * 3600 + m * 60 + s

df['tempo_segundos'] = df['tempo_execucao'].apply(tempo_para_segundos)

# Encontrar o melhor tempo de execução para cada modelo
melhor_tempo_df = df.groupby('nome_modelo')['tempo_segundos'].min().reset_index()

# Criar o gráfico de barras
st.title('Comparação do Melhor Tempo de Execução entre Modelos')

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(melhor_tempo_df['nome_modelo'], melhor_tempo_df['tempo_segundos'], color='#8b008b')

# Adicionar rótulos de valor em cada barra
for i, valor in enumerate(melhor_tempo_df['tempo_segundos']):
    ax.text(i, valor + 0.1, f'{valor} s', ha='center', va='bottom')

ax.set_title('Tempo de Execução por Modelo')
ax.set_xlabel('Modelos')
ax.set_ylabel('Tempo de Execução (segundos)')
ax.set_ylim(0, melhor_tempo_df['tempo_segundos'].max() + 5)  # Ajusta o limite superior para melhor visualização

# Exibir o gráfico no Streamlit
st.pyplot(fig)

#
# ------------------ Exibição Interativa -----------------------
#

st.header("Escolha um modelo para visualizar as métricas:")
modelo_selecionado = st.selectbox('', df['nome_modelo'].unique())

# Filtrar o DataFrame para o modelo selecionado
df_modelo = df_original[df_original['nome_modelo'] == modelo_selecionado]

# Selecionar as colunas relevantes para exibição
df_metrica = df_modelo[['nome_modelo','id_execucao','tempo_execucao','vl_accuracy','tp_classe', 'vl_precision', 'vl_recall', 'vl_f1_score']]

# Exibir a tabela no Streamlit
st.subheader(f'Métricas de Desempenho para o Modelo {modelo_selecionado}')
st.dataframe(df_metrica)