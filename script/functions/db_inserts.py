import mysql.connector
from datetime import datetime

def get_conn(env='dev'):

    if env == 'dev':
        # Conectar ao banco de dados MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="urubu100",
            database="adoptaidb"
        )
    elif env == 'prd':
        # Conectar ao banco de dados MySQL
        conn = mysql.connector.connect(
            host="adoptaidb.c9v2lvhlu1ya.us-east-1.rds.amazonaws.com",
            user="admin",
            password="urubu100",
            database="adoptaidb"
        )
    return conn

# Função para inserir dados na tabela tb_modelo
def insert_model(cursor, nome_modelo, nome_base):
    insert_query = '''
        INSERT INTO tb_modelo (nome_modelo, nome_base)
        VALUES (%s, %s)
    '''
    cursor.execute(insert_query, (nome_modelo, nome_base))
    return cursor.lastrowid

# Função para inserir dados na tabela tb_execucao
def insert_execution(cursor, fk_modelo, vl_accuracy, dt_inicio_exec, dt_fim_exec):
    dt_inicio_exec = datetime.fromtimestamp(dt_inicio_exec).strftime('%Y-%m-%d %H:%M:%S')
    dt_fim_exec = datetime.fromtimestamp(dt_fim_exec).strftime('%Y-%m-%d %H:%M:%S')

    insert_query = '''
        INSERT INTO tb_execucao (fk_modelo, vl_accuracy, dt_inicio_exec, dt_fim_exec)
        VALUES (%s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (fk_modelo, vl_accuracy, dt_inicio_exec, dt_fim_exec))
    return cursor.lastrowid

# Função para inserir dados na tabela tb_hiperparametro
def insert_hyperparameter(cursor, fk_execucao, nome_parametro, vl_parametro):
        insert_query = '''INSERT INTO tb_hiperparametro (fk_execucao, nome_parametro, vl_parametro)
        VALUES (%s, %s, %s)'''
        cursor.execute(insert_query, (fk_execucao, nome_parametro, vl_parametro))

# Função para inserir dados na tabela tb_desempenho
def insert_performance(cursor, fk_execucao, vl_precision, vl_recall, vl_f1_score):
    if (len(vl_precision) > 0):
        for i in range(len(vl_precision)):
            insert_query = '''
                INSERT INTO tb_desempenho (fk_execucao, tp_classe, vl_precision, vl_recall, vl_f1_score)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (fk_execucao, i, vl_precision[i], vl_recall[i], vl_f1_score[i]))

def insert_values(model, execution, hyperparam, performance, env='dev'):
    # # connection
    conn = get_conn(env=env)
    cursor = conn.cursor()

    print(f'Executando em {env}')

    try:
        # Inserindo dados nas tabelas
        id_model = insert_model(cursor, model['nome_modelo'], model['nome_fonte'])

        for i in range(len(execution['accuracy'])):
            id_execution = insert_execution(cursor, id_model, execution['accuracy'][i], execution['start_time'], execution['end_time'])

            insert_performance(cursor, id_execution, performance['precision_values'][i], performance['recall_values'][i], performance['f1_values'][i])
            for j in range(len(list(hyperparam.keys()))):
                param = list(hyperparam.keys())[j]
                insert_hyperparameter(cursor, id_execution, param, hyperparam[param][i])

        # # Commit das alterações no banco de dados
        conn.commit()
    except Exception:
        print(f'Erro ao inserir em {env}')
    finally:
        conn.close()
        print('Registros inseridos')
