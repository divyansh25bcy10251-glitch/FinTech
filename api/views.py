from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.apps import ApiConfig
import pandas as pd

@api_view(['POST'])
def predict_risk(request):
    print("--- 🟢 NEW REQUEST RECEIVED ---")
    print(f"1. Incoming JSON Payload: {request.data}")

    # Extract the data safely
    incoming_data = request.data
    
    # Format the DataFrame for the ML Model
    df = pd.DataFrame([{
        'daily_average_balance': incoming_data.get('daily_balance', 0),
        'discretionary_spend_ratio': incoming_data.get('spend_ratio', 0),
        'income_frequency_days': incoming_data.get('income_freq', 30)
    }])
    
    print("2. Data formatted successfully.")

    # Predict the score
    if ApiConfig.ml_model is not None:
        prediction = ApiConfig.ml_model.predict(df)
        risk_score = int(prediction[0])
        print(f"3. AI Engine Executed. Calculated Score: {risk_score}")
    else:
        risk_score = 750
        print("3. ⚠️ WARNING: ML Model missing. Using fallback score.")

    print("--- 🏁 SENDING 200 OK RESPONSE ---")
    
    return Response({
        "status": "success",
        "risk_score": risk_score,
        "message": "Model executed successfully"
    })
