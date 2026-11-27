from pathlib import Path
import zipfile
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
import joblib
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
with zipfile.ZipFile(ROOT / "ShopFast_datos.zip") as archive:
    data = pd.read_csv(archive.open("impresiones.csv")).merge(
        pd.read_csv(archive.open("catalogo.csv")), on="producto", validate="many_to_one")
data["fecha"] = pd.to_datetime(data.ts_impresion, utc=True)
data["clic"] = data.ts_clic.notna().astype(int)
data["coincide"] = (data.contexto == data.categoria).astype(int)
features = ["usuario", "contexto", "producto", "categoria", "precio_usd", "coincide"]
train = data[data.fecha.dt.day <= 18].copy()
val = data[data.fecha.dt.day.between(19, 23)].copy()
test = data[data.fecha.dt.day >= 24].copy()
train = train[train.fecha + pd.Timedelta(minutes=10) <= val.fecha.min()]
val = val[val.fecha + pd.Timedelta(minutes=10) <= test.fecha.min()]
cat, num = features[:4], features[4:]

def pipeline(model):
    return Pipeline([("prep", ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ("num", StandardScaler(), num)])), ("modelo", model)])

def metrics(frame, scores, threshold):
    pred, target = np.asarray(scores) >= threshold, frame.clic.to_numpy()
    temp = frame[["sesion", "producto", "clic"]].copy()
    temp["score"] = scores
    ndcg, zero = [], 0
    for _, group in temp.groupby("sesion"):
        relevance = group.sort_values(["score", "producto"], ascending=[False, True]).clic.to_numpy()[:10]
        ideal = np.sort(group.clic.to_numpy())[::-1][:10]
        weights = 1 / np.log2(np.arange(2, 2 + len(relevance)))
        denominator = (ideal * weights).sum()
        if denominator:
            ndcg.append((relevance * weights).sum() / denominator)
        else:
            zero += 1
    return dict(accuracy=accuracy_score(target, pred),
        precision=precision_score(target, pred, zero_division=0),
        recall=recall_score(target, pred, zero_division=0),
        f1=f1_score(target, pred, zero_division=0),
        ndcg10=np.mean(ndcg) if ndcg else np.nan,
        sesiones=temp.sesion.nunique(), sin_positivos=zero, filas=len(frame))

pop = train.groupby("producto").clic.agg(["sum", "count"])
prior = train.clic.mean()
rates = (pop["sum"] + 10 * prior) / (pop["count"] + 10)
def baseline(frame):
    return frame.producto.map(rates).fillna(prior).to_numpy()

models = {
    "Popularidad": None,
    "Logistica": pipeline(LogisticRegression(max_iter=500, C=1, random_state=42)),
    "RandomForest": pipeline(RandomForestClassifier(n_estimators=100, max_depth=8,
        min_samples_leaf=10, random_state=42, n_jobs=2)),
    "XGBoost": pipeline(XGBClassifier(n_estimators=100, max_depth=3, learning_rate=.05,
        subsample=.8, colsample_bytree=.8, random_state=42, n_jobs=2, eval_metric="logloss"))}
rows, thresholds = [], {}
for name, model in models.items():
    if model is not None:
        model.fit(train[features], train.clic)
    scores = baseline(val) if model is None else model.predict_proba(val[features])[:, 1]
    threshold = max(np.arange(.02, .51, .01),
        key=lambda t: f1_score(val.clic, scores >= t, zero_division=0))
    thresholds[name] = float(threshold)
    rows.append(dict(modelo=name, particion="validacion", segmento="todos",
        umbral=threshold, **metrics(val, scores, threshold)))
winner = max((r for r in rows if r["modelo"] != "Popularidad"),
    key=lambda r: r["ndcg10"])["modelo"]
for name in ["Popularidad", winner]:
    model = models[name]
    scores = baseline(test) if model is None else model.predict_proba(test[features])[:, 1]
    known = test.usuario.isin(train.usuario).to_numpy()
    for segment, mask in [("todos", np.ones(len(test), dtype=bool)),
        ("conocidos", known), ("nuevos", ~known)]:
        if mask.any():
            rows.append(dict(modelo=name, particion="prueba", segmento=segment,
                umbral=thresholds[name], **metrics(test.loc[mask], scores[mask], thresholds[name])))
results = pd.DataFrame(rows)
results.to_csv(ROOT / "metricas.csv", index=False)
print(results.to_string(index=False))
print("Seleccion:", winner, "filas:", len(train), len(val), len(test))
joblib.dump({"pipeline": models[winner], "features": features,
    "umbral": thresholds[winner], "modelo": winner}, ROOT / "modelo.joblib")
for part in ["validacion", "prueba"]:
    subset = results[results.particion == part].query("segmento == 'todos'").set_index("modelo")
    axis = subset[["accuracy", "precision", "recall", "f1", "ndcg10"]].plot.bar(figsize=(10, 5), rot=0)
    axis.set_ylim(0, 1); axis.set_ylabel("Metrica"); axis.set_title("ShopFast - " + part)
    plt.tight_layout(); plt.savefig(ROOT / (part + ".png"), dpi=160); plt.close()
