import time
from sklearn.ensemble import RandomForestClassifier
from preprocessing import preparar_datos
from sklearn.model_selection import train_test_split

def benchmark_hpc():
    X, y, df = preparar_datos('data/datos_norte_andino.csv')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modelo secuencial
    modelo_seq = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=1
    )

    start = time.time()
    modelo_seq.fit(X_train, y_train)
    tiempo_seq = time.time() - start

    # Modelo paralelo (OpenMP)
    modelo_par = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    start = time.time()
    modelo_par.fit(X_train, y_train)
    tiempo_par = time.time() - start

    reduccion = (1 - tiempo_par / tiempo_seq) * 100

    return {
        "tiempo_secuencial": round(tiempo_seq, 4),
        "tiempo_paralelo": round(tiempo_par, 4),
        "reduccion": round(reduccion, 2)
    }

