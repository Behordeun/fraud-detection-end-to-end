import json
from kafka import KafkaConsumer
import requests
import pandas as pd
from datetime import datetime

class FraudDetectionConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='fraud-transactions'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.api_url = "http://localhost:8000/predict"
        self.results = []
    
    def predict_fraud(self, transaction):
        """Send transaction to fraud detection API."""
        try:
            # Remove non-feature fields
            features = {k: v for k, v in transaction.items() 
                       if k not in ['timestamp', 'Class']}
            
            response = requests.post(self.api_url, json=features, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Prediction error: {e}")
        return None
    
    def process_stream(self):
        """Process incoming transaction stream."""
        print("Starting real-time fraud detection consumer...")
        
        for message in self.consumer:
            transaction = message.value
            timestamp = datetime.fromtimestamp(transaction.get('timestamp', 0))
            
            # Get fraud prediction
            prediction = self.predict_fraud(transaction)
            
            if prediction:
                result = {
                    'timestamp': timestamp,
                    'amount': transaction.get('Amount', 0),
                    'is_fraud': prediction['is_fraud'],
                    'fraud_probability': prediction['fraud_probability'],
                    'confidence': prediction['confidence']
                }
                
                self.results.append(result)
                
                # Alert on high-risk transactions
                if prediction['is_fraud'] and prediction['fraud_probability'] > 0.8:
                    print(f"🚨 HIGH RISK FRAUD DETECTED: {result}")
                
                # Save results periodically
                if len(self.results) % 100 == 0:
                    self.save_results()
    
    def save_results(self):
        """Save streaming results."""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(f"streaming_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
            print(f"Saved {len(self.results)} streaming predictions")

if __name__ == "__main__":
    consumer = FraudDetectionConsumer()
    consumer.process_stream()