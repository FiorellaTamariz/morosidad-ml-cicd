from flask import Flask, request, jsonify,render_template_string
import pickle
import json
import numpy as np
import pandas as pd
from benchmark_hpc import benchmark_hpc

app = Flask(__name__)

print("Cargando modelo...")
with open('models/modelo_morosidad.pkl', 'rb') as f:
    modelo = pickle.load(f)

with open('models/feature_names.json', 'r') as f:
    feature_names = json.load(f)

CATEGORIAS = {
    0: "Al día",
    1: "Mora leve",
    2: "Mora grave",
    3: "Mora crítica"
}

@app.route('/')
def home():
    return render_template_string("""
    <style>
        body { font-family: Arial; margin: 40px; max-width: 900px; }
        h1 { color: #0A5275; }
        .card { padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; }
        a { color: #0A5275; font-weight: bold; }
    </style>

    <h1>API de Predicción de Morosidad - Norte Andino SAC</h1>
    <p>Interfaz visual para pruebas rápidas</p>

    <div class="card">
        <h3>🔍 Predicción (POST)</h3>
        <p>Formulario para probar la predicción del modelo</p>
        <a href="/predict">Ir al formulario</a>
    </div>

    <div class="card">
        <h3>📊 Métricas del modelo (GET)</h3>
        <a href="/metrics">Ver métricas</a>
    </div>

    <div class="card">
        <h3>🩺 Estado del servicio (GET)</h3>
        <a href="/health">Ver estado</a>
    </div>

    <div class="card">
        <h3>📌 Ejemplo en cURL</h3>
        <pre>
curl -X POST http://localhost:5000/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "monto_original": 5000,
    "monto_actual": 3000,
    "ratio_deuda": 0.6,
    "dias_desde_vencimiento": 45
  }'
        </pre>
    </div>
    """)
@app.route('/health', methods=['GET'])
def health():
    if request.args.get("raw") == "1":
        return jsonify({
            'status': 'healthy',
            'model_loaded': modelo is not None
        })

    return render_template_string("""
    <style>
        body { font-family: Arial; margin: 40px; max-width: 600px; }
        h2 { color: #0A5275; }
        .card {
            background: #f6f8fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #d0d7de;
        }
        .ok { color: green; font-weight: bold; }
    </style>

    <h2>🩺 Estado del servicio (Health Check)</h2>

    <div class="card">
        <p><b>Estado:</b> <span class="ok">Healthy ✔</span></p>
        <p><b>Modelo cargado:</b> {{ cargado }}</p>
    </div>

    <p style="margin-top:20px;">Ver JSON: <a href="/health?raw=1">/health?raw=1</a></p>
    <p><a href="/">Volver al inicio</a></p>
    """, cargado="Sí" if modelo is not None else "No")

@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        with open('models/metricas.json', 'r') as f:
            metricas = json.load(f)
    except:
        if request.args.get("raw") == "1":
            return jsonify({'error': 'Métricas no disponibles'}), 404
        
        return render_template_string("""
        <h2 style="color:#A40000;">❌ Métricas no disponibles</h2>
        <p>El archivo <b>metricas.json</b> no se encontró.</p>
        <p><a href="/">Volver</a></p>
        """)

    # Si ?raw=1 → envío JSON puro
    if request.args.get("raw") == "1":
        return jsonify(metricas)

    # HTML Bonito
    return render_template_string("""
    <style>
        body { font-family: Arial; margin: 40px; max-width: 700px; }
        h2 { color: #0A5275; }
        .card { background: #f6f8fa; padding: 20px; border-radius: 10px; border: 1px solid #d0d7de; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border-bottom: 1px solid #ddd; }
        th { background: #e8eef3; text-align: left; }
    </style>

    <h2>📊 Métricas del Modelo</h2>

    <div class="card">
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            {% for key, value in metricas.items() %}
                <tr>
                    <td>{{ key }}</td>
                    <td>{{ value }}</td>
                </tr>
            {% endfor %}
        </table>
    </div>

    <p style="margin-top:20px;">Ver JSON: <a href="/metrics?raw=1">/metrics?raw=1</a></p>

    <p><a href="/">Volver al inicio</a></p>
    """, metricas=metricas)

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'GET':
        return render_template_string("""
        <style>
            body { font-family: Arial; margin: 40px; max-width: 500px; }
            h2 { color: #0A5275; }
            label { display: block; margin-top: 15px; font-weight: bold; }
            input { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #ccc; margin-top: 5px; }
            button { margin-top: 20px; padding: 12px; width: 100%; background-color: #0A5275; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
            button:hover { background-color: #083d57; }
            pre { background: #f0f0f0; padding: 15px; border-radius: 8px; }
        </style>

        <h2>🔍 Probar predicción de morosidad</h2>

        <form action="/predict" method="post">
            {% for feature in feature_names %}
                <label>{{ feature }}</label>
                <input name="{{ feature }}" type="number" step="any" required />
            {% endfor %}
            <button type="submit">Predecir</button>
        </form>

        <p style="margin-top:40px;">Volver a <a href="/">Inicio</a></p>
        """, feature_names=feature_names)

    # --------------------------
    #   POST (no tocado)
    # --------------------------
    try:
        datos = request.get_json(silent=True) or request.form.to_dict()

        # Convertir str→float si vienen del formulario
        for k in datos:
            try:
                datos[k] = float(datos[k])
            except:
                pass

        for feature in feature_names:
            if feature not in datos:
                return jsonify({'error': f'Falta el campo: {feature}'}), 400

        X_pred = pd.DataFrame([datos])[feature_names]
        
        prediccion = modelo.predict(X_pred)[0]
        probabilidades = modelo.predict_proba(X_pred)[0]

        respuesta = {
            'categoria_predicha': int(prediccion),
            'descripcion': CATEGORIAS[prediccion],
            'probabilidades': {
                CATEGORIAS[i]: float(prob) 
                for i, prob in enumerate(probabilidades)
            },
            'recomendacion': obtener_recomendacion(prediccion)
        }
        return jsonify(respuesta)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def obtener_recomendacion(categoria):
    recomendaciones = {
        0: "Cliente al día. Mantener seguimiento regular.",
        1: "Mora leve detectada. Enviar recordatorio de pago.",
        2: "Mora grave. Contactar urgentemente al cliente.",
        3: "Mora crítica. Iniciar proceso de cobranza inmediata."
    }
    return recomendaciones[categoria]


'''@app.route('/benchmark', methods=['GET'])
def benchmark():
    try:
        resultados = benchmark_hpc()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=False)


