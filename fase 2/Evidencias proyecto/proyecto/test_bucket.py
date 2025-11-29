import boto3
from botocore.client import Config

# TUS DATOS (Tal cual los tienes en settings.py)
ACCESS_KEY = 'e82eb60d528d50998a99055f2eed02e2582c63e7'
SECRET_KEY = 'C0yi8F/31pgqAUPlS7sTfnpyiIK7/+YyM52Em99ZpyA='
BUCKET_NAME = 'docuflow-media'
ENDPOINT_URL = 'https://ax9zrboiubmf.compat.objectstorage.sa-santiago-1.oraclecloud.com'
REGION_NAME = 'sa-santiago-1'

def probar_conexion():
    print("--- INICIANDO PRUEBA DE CONEXIÓN A ORACLE S3 ---")
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=ENDPOINT_URL,
        region_name=REGION_NAME,
        config=Config(signature_version='s3v4')
    )

    try:
        # 1. Intentar listar archivos (Prueba de lectura/conexión)
        print("1. Intentando listar archivos en el bucket...")
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        print("   -> ¡Conexión EXITOSA! Se accedió al bucket.")
        
        if 'Contents' in response:
            print(f"   -> Archivos encontrados: {len(response['Contents'])}")
        else:
            print("   -> El bucket está vacío, pero accesible.")

        # 2. Intentar subir un archivo de prueba (Prueba de escritura)
        print("\n2. Intentando subir un archivo de prueba 'hola.txt'...")
        s3.put_object(Bucket=BUCKET_NAME, Key='hola.txt', Body=b'Hola desde Python!')
        print("   -> ¡Subida EXITOSA!")
        
        print("\nCONCLUSIÓN: Tus credenciales y el Bucket están PERFECTOS.")
        print("Si Django falla, el error está en settings.py, no en Oracle.")

    except Exception as e:
        print("\nX ERROR FATAL:")
        print(e)
        print("\nCONCLUSIÓN: El problema es de CREDENCIALES, PERMISOS o NOMBRE DEL BUCKET.")

if __name__ == "__main__":
    probar_conexion()