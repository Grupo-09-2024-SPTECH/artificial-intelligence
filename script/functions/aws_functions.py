import boto3
import pandas as pd
from io import StringIO
import sys
sys.path.append('..')
import util.credentials as u


def s3_csv_to_df(bucket_name):
    session = boto3.Session(
        aws_access_key_id= u.aws_access_key_id,
        aws_secret_access_key= u.aws_secret_access_key,
        aws_session_token= u.aws_session_token
    )

    s3_client = session.client('s3')

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print('Bucket vazio')
        else:
            sorted_objects = sorted(response['Contents'], key=lambda obj: obj['LastModified'], reverse=True)
            latest_object = sorted_objects[0]

            object_key = latest_object['Key']
            print(f'Último arquivo adicionado: {object_key}')

            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body'].read().decode('utf-8')

            data = StringIO(content)
            df = pd.read_csv(data)
    except Exception as e:
        print(f'Erro ao processar o arquivo do S3: {e}')

    return [object_key,df]