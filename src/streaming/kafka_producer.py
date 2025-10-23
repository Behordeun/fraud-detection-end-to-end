import json
import time
import pandas as pd
from kafka import KafkaProducer
import numpy as np

class FraudDataProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='fraud-transactions'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic
    
    def generate_transaction(self):
        """Generate a realistic transaction."""
        # Load sample from real data
        try:
            df = pd.read_csv("data/raw/creditcard_2023.csv")
            sample = df.sample(1).iloc[0].to_dict()
            # Add timestamp
            sample['timestamp'] = time.time()
            return sample
        except:
            # Fallback to synthetic data
            return {
                'Time': np.random.uniform(0, 172800),
                **{f'V{i}': np.random.normal(0, 1) for i in range(1, 29)},
                'Amount': np.random.lognormal(3, 1.5),
                'timestamp': time.time()
            }
    
    def start_streaming(self, rate_per_second=10):
        """Start streaming transactions."""
        print(f"Starting fraud detection stream at {rate_per_second} transactions/second")
        
        while True:
            transaction = self.generate_transaction()
            self.producer.send(self.topic, transaction)
            time.sleep(1.0 / rate_per_second)

if __name__ == "__main__":
    producer = FraudDataProducer()
    producer.start_streaming()