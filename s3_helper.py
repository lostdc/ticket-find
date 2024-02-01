import os
import boto3
import time
import requests

def conectar_s3():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    return s3


def subir_imagen_s3(url, bucket_name, s3_file_path, s3_client):
    if url == 'predeterminado/sin_imagen.jpg':
        return
    respuesta = requests.get(url, stream=True)
    if respuesta.status_code == 200:
        respuesta.raw.decode_content = True
        s3_client.upload_fileobj(respuesta.raw, bucket_name, s3_file_path)
    time.sleep(1)
