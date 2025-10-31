from database import get_db
from models import ModelPrediction, ModelMetric

db = get_db()

# Check prediction types
all_predictions = db.query(ModelPrediction).all()
print(f'Total predictions: {len(all_predictions)}')

prediction_types = {}
for p in all_predictions:
    if p.prediction_type not in prediction_types:
        prediction_types[p.prediction_type] = 0
    prediction_types[p.prediction_type] += 1

print('Prediction types:')
for pt, count in prediction_types.items():
    print(f'  {pt}: {count}')

# Show sample predictions
predictions = db.query(ModelPrediction).limit(10).all()
print('\nSample predictions:')
for p in predictions[:5]:
    print(f'{p.prediction_type}: {p.predicted_value:.3f}')

# Check if there are risk predictions specifically
risk_predictions = db.query(ModelPrediction).filter(ModelPrediction.prediction_type == 'risk_assessment').limit(5).all()
print(f'\nRisk assessment predictions: {len(risk_predictions)}')
for p in risk_predictions:
    print(f'Risk for entity {p.entity_id}: {p.predicted_value:.3f}')

db.close()
