import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import json
from preprocessing import preparar_datos

def entrenar_modelo():
    print("Cargando y preparando datos...")
    X, y, df = preparar_datos('data/datos_norte_andino.csv')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    print("\\n Entrenando Random Forest...")
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    modelo.fit(X_train, y_train)

    print("\\n Evaluando modelo...")
    y_pred = modelo.predict(X_test)
    
    print("\\n--- Reporte de Clasificación ---")
    print(classification_report(y_test, y_pred, 
                                target_names=['Al día', 'Leve', 'Grave', 'Crítica']))

    print("\\n Guardando modelo...")
    with open('models/modelo_morosidad.pkl', 'wb') as f:
        pickle.dump(modelo, f)
    
    with open('models/feature_names.json', 'w') as f:
        json.dump(list(X.columns), f)

    metricas = {
        'accuracy': float(modelo.score(X_test, y_test)),
        'n_estimators': 100,
        'max_depth': 10
    }
    
    with open('models/metricas.json', 'w') as f:
        json.dump(metricas, f, indent=2)
    
    print(f"\\nModelo entrenado con accuracy: {metricas['accuracy']:.2%}")
    print("Archivos guardados en /models")
    
    return modelo, metricas

if __name__ == "__main__":

    entrenar_modelo()
