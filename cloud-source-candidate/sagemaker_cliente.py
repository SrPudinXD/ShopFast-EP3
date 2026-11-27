import boto3
import json
import os

REGION_NAME = os.getenv("AWS_REGION", "us-east-2")
ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "shopfast-endpoint-v1")

cliente = boto3.client(
    "sagemaker-runtime",
    region_name=REGION_NAME,
)


def predecir_aws(datos):
    respuesta = cliente.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Accept="application/json",
        Body=json.dumps({"instances": datos}),
    )
    resultado = json.loads(
        respuesta["Body"].read().decode("utf-8")
    )
    return resultado["predictions"]
