import os
import json
import joblib
import pandas as pd


def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "modelo.joblib"))


def input_fn(request_body, content_type):
    if content_type == "application/json":
        datos = json.loads(request_body)
        return pd.DataFrame(datos["instances"])
    raise ValueError("Formato no soportado")


def predict_fn(datos, modelo):
    caracteristicas = modelo["features"]
    probabilidades = modelo["pipeline"].predict_proba(
        datos[caracteristicas]
    )[:, 1]
    return probabilidades.tolist()


def output_fn(prediction, accept):
    return json.dumps({"predictions": prediction})
