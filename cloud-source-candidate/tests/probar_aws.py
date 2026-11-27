from sagemaker_cliente import predecir_aws

datos = [
    {
        "usuario": "U7",
        "contexto": "audio",
        "producto": "P17",
        "categoria": "audio",
        "precio_usd": 29,
        "coincide": 1,
    },
    {
        "usuario": "U7",
        "contexto": "audio",
        "producto": "P28",
        "categoria": "movil",
        "precio_usd": 216,
        "coincide": 0,
    },
]

predicciones = predecir_aws(datos)
print("Conexion con SageMaker exitosa")
print("Predicciones desde AWS:")
for dato, score in zip(datos, predicciones):
    print(dato["producto"], ":", score)
