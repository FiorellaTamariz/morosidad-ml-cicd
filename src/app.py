from flask import Flask, request, jsonify,render_template_string
import pickle
import json
import numpy as np
import pandas as pd

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
    return jsonify({
        'status': 'healthy',
        'model_loaded': modelo is not None
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        with open('models/metricas.json', 'r') as f:
            metricas = json.load(f)
        return jsonify(metricas)
    except:
        return jsonify({'error': 'Métricas no disponibles'}), 404

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        datos = request.get_json()
        
        for feature in feature_names:
            if feature not in datos:
                return jsonify({
                    'error': f'Falta el campo: {feature}'
                }), 400
        
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

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=False)


