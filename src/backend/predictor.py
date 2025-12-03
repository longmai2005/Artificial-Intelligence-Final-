import numpy as np
import os
from tensorflow.keras.models import load_model

class EnergyPredictor:  # <--- Python cần tìm thấy dòng này
    def __init__(self, model_path='models/lstm_model.h5'):
        self.model_path = model_path
        self.model = None
        self.load_model_if_exists()

    def load_model_if_exists(self):
        if os.path.exists(self.model_path):
            try:
                self.model = load_model(self.model_path)
            except:
                self.model = None

    def predict_next_24h(self, history_data):
        # Chế độ giả lập (Mock mode) để chạy web khi chưa train AI
        if len(history_data) > 0:
            last_val = history_data[-1]
        else:
            last_val = 1.0
            
        predictions = []
        for i in range(24):
            noise = np.random.normal(0, 0.1)
            trend = np.sin(i / 4) * 0.5
            pred = last_val + trend + noise
            predictions.append(max(0.1, pred))
        return predictions