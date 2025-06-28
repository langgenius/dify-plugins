from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

SYMPTOM_DB = {
    "fever": ["Influenza", "COVID-19"],
    "cough": ["Common Cold", "COVID-19"],
    "fatigue": ["Anemia", "Flu"]
}

class SymptomRequest(BaseModel):
    symptoms: List[str]

@app.post("/analyze")
def analyze(data: SymptomRequest):
    score = {}
    for s in data.symptoms:
        for cond in SYMPTOM_DB.get(s.lower(), []):
            score[cond] = score.get(cond, 0) + 1
    sorted_conds = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return {
        "possible_conditions": [c[0] for c in sorted_conds[:3]],
        "disclaimer": "This is not medical advice."
    }
