import time
import json
from functools import wraps
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.predictions = []
        self.response_times = []
        self.errors = []
    
    def record_prediction(self, input_data, prediction, response_time):
        self.predictions.append({
            'timestamp': datetime.now().isoformat(),
            'input': input_data,
            'prediction': prediction,
            'response_time_ms': response_time * 1000
        })
        self.response_times.append(response_time)
    
    def record_error(self, error_type, error_message):
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': str(error_message)
        })
    
    def get_stats(self):
        if not self.response_times:
            return {
                'total_predictions': 0,
                'avg_response_time_ms': 0,
                'total_errors': len(self.errors)
            }
        
        return {
            'total_predictions': len(self.predictions),
            'avg_response_time_ms': sum(self.response_times) / len(self.response_times) * 1000,
            'min_response_time_ms': min(self.response_times) * 1000,
            'max_response_time_ms': max(self.response_times) * 1000,
            'total_errors': len(self.errors),
            'last_prediction': self.predictions[-1] if self.predictions else None
        }
    
    def save_metrics(self, filepath='metrics_log.json'):
        with open(filepath, 'w') as f:
            json.dump({
                'stats': self.get_stats(),
                'predictions': self.predictions[-100:],  # Últimas 100
                'errors': self.errors[-50:]  # Últimos 50 errores
            }, f, indent=2)

def measure_time(metrics_collector):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                return result, elapsed
            except Exception as e:
                metrics_collector.record_error(type(e).__name__, str(e))
                raise
        return wrapper
    return decorator