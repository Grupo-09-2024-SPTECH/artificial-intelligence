import mysql.connector
from datetime import datetime

def get_conn(env='dev'):
    # Função para obter a conexão com o banco de dados, dependendo do ambiente (dev ou prd)

    if env == 'dev':
        # Conectar ao banco de dados MySQL no ambiente de desenvolvimento
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="urubu100",
            database="adoptaidb"
        )
    elif env == 'prd':
        # Conectar ao banco de dados MySQL no ambiente de produção
        conn = mysql.connector.connect(
            host="adoptaidb.c9v2lvhlu1ya.us-east-1.rds.amazonaws.com",
            user="admin",
            password="urubu100",
            database="adoptaidb"
        )
    return conn

# Função para inserir dados na tabela tb_modelo
def insert_model(cursor, nome_modelo, nome_base):

    # Verifica se o modelo já existe na tabela
    select_query = f"SELECT * FROM tb_modelo WHERE nome_modelo LIKE '{nome_modelo}'"
    cursor.execute(select_query)

    response = cursor.fetchall()

    if (len(response) == 0):
        # Se o modelo não existir, cria um novo registro
        insert_query = '''
            INSERT INTO tb_modelo (nome_modelo, nome_base)
            VALUES (%s, %s)
        '''
        cursor.execute(insert_query, (nome_modelo, nome_base))
        return cursor.lastrowid # Retorna o ID do novo modelo inserido
    else:
        # Caso o modelo já exista, retorna o ID do modelo existente
        return response[0][0]

# Função para inserir dados na tabela tb_execucao
def insert_execution(cursor, fk_modelo, vl_accuracy, vl_mae, vl_qwk, dt_inicio_exec, dt_fim_exec):
    # Converte os timestamps para o formato datetime do MySQL
    dt_inicio_exec = datetime.fromtimestamp(dt_inicio_exec).strftime('%Y-%m-%d %H:%M:%S')
    dt_fim_exec = datetime.fromtimestamp(dt_fim_exec).strftime('%Y-%m-%d %H:%M:%S')

    insert_query = '''
        INSERT INTO tb_execucao (fk_modelo, vl_accuracy, vl_mae, vl_qwk, dt_inicio_exec, dt_fim_exec)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (fk_modelo, vl_accuracy, vl_mae, vl_qwk, dt_inicio_exec, dt_fim_exec))
    return cursor.lastrowid # Retorna o ID da nova execução inserida

# Função para inserir dados na tabela tb_hiperparametro
def insert_hyperparameter(cursor, fk_execucao, nome_parametro, vl_parametro):
        # Insere um novo hiperparâmetro relacionado à execução específica
        insert_query = '''INSERT INTO tb_hiperparametro (fk_execucao, nome_parametro, vl_parametro)
        VALUES (%s, %s, %s)'''
        cursor.execute(insert_query, (fk_execucao, nome_parametro, vl_parametro))

# Função para inserir dados na tabela tb_desempenho
def insert_performance(cursor, fk_execucao, vl_precision, vl_recall, vl_f1_score):
    # Verifica se há valores de precisão para inserir
    if (len(vl_precision) > 0):
        for i in range(len(vl_precision)):
            # Insere o desempenho de cada classe na tabela tb_desempenho
            insert_query = '''
                INSERT INTO tb_desempenho (fk_execucao, tp_classe, vl_precision, vl_recall, vl_f1_score)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (fk_execucao, i, vl_precision[i], vl_recall[i], vl_f1_score[i]))

# Função principal para inserir todos os valores nas tabelas correspondentes
def insert_values(model, execution, hyperparam, performance, env='dev'):
    # Estabelece conexão com o banco de dados com base no ambiente
    conn = get_conn(env=env)
    cursor = conn.cursor()

    print(f'Executando em {env}')

    try:
        # Inserindo dados na tabela tb_modelo
        id_model = insert_model(cursor, model['nome_modelo'], model['nome_fonte'])

        for i in range(len(execution['accuracy'])):
            # Inserindo dados na tabela tb_execucao
            id_execution = insert_execution(
                cursor, 
                id_model, 
                execution['accuracy'][i], 
                execution['mae'][i], 
                execution['qwk'][i], 
                execution['start_time'][i], 
                execution['end_time'][i]
                )

            # Inserindo dados na tabela tb_desempenho
            insert_performance(cursor, id_execution, performance['precision_values'][i], performance['recall_values'][i], performance['f1_values'][i])
            for j in range(len(list(hyperparam.keys()))):
                # Inserindo dados na tabela tb_hiperparametro
                param = list(hyperparam.keys())[j]
                insert_hyperparameter(cursor, id_execution, param, hyperparam[param][i])

        # Commit das alterações no banco de dados
        conn.commit()
        print(f'Registros inseridos em {env}')
    except Exception:
        # Caso ocorra algum erro, uma mensagem será exibida
        print(f'Erro ao inserir em {env}')
    finally:
        # Fecha a conexão com o banco de dados
        conn.close()