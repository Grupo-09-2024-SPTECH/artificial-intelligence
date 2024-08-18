import boto3
import pandas as pd
from io import StringIO
import sys

# Adiciona o diretório pai ao sys.path para permitir a importação do módulo 'credentials'
sys.path.append('..')
import util.credentials as u # Importa credenciais AWS do módulo 'credentials'

def s3_csv_to_df(bucket_name):
    # Cria uma sessão do boto3 utilizando as credenciais fornecidas
    session = boto3.Session(
        aws_access_key_id= u.aws_access_key_id,
        aws_secret_access_key= u.aws_secret_access_key,
        aws_session_token= u.aws_session_token
    )

    # Cria um cliente S3 utilizando a sessão criada
    s3_client = session.client('s3')

    try:
        # Lista os objetos no bucket S3 especificado
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        # Verifica se o bucket está vazio
        if 'Contents' not in response:
            print('Bucket vazio')
        else:
            # Ordena os objetos por data de modificação, do mais recente para o mais antigo
            sorted_objects = sorted(response['Contents'], key=lambda obj: obj['LastModified'], reverse=True)

            # Seleciona o objeto mais recente
            latest_object = sorted_objects[0]

            # Obtém a chave (nome) do arquivo mais recente
            object_key = latest_object['Key']
            print(f'Último arquivo adicionado: {object_key}')

            # Faz o download do objeto mais recente do S3
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

            # Lê o conteúdo do objeto e decodifica de bytes para string
            content = response['Body'].read().decode('utf-8')

            # Usa StringIO para converter a string em um objeto que pode ser lido pelo pandas
            data = StringIO(content)

            # Lê o conteúdo do arquivo CSV em um DataFrame do pandas
            df = pd.read_csv(data)
    
    # Captura exceções e exibe uma mensagem de erro
    except Exception as e:
        print(f'Erro ao processar o arquivo do S3: {e}')
        
    # Retorna a chave do objeto e o DataFrame contendo os dados do CSV
    return [object_key,df]