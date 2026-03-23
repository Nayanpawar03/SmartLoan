# smartloan-fis/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fis_engine import run_fis
from nn_model import predict_default_probability
from explainer import generate_explanation

app = FastAPI()


class CreditInput(BaseModel):
    payment_history: float
    credit_utilization: float
    debt_to_income_ratio: float
    monthly_income: float
    existing_emi: float
    credit_history_length: int
    num_inquiries: int


@app.post("/predict-credit-score")
def predict_credit_score(data: CreditInput):
    try:
        # Step 1: Run FIS to get fuzzy credit score
        fis_result = run_fis(
            payment_history=data.payment_history,
            credit_utilization=data.credit_utilization,
            debt_to_income_ratio=data.debt_to_income_ratio,
            monthly_income=data.monthly_income,
            existing_emi=data.existing_emi,
            credit_history_length=data.credit_history_length,
            num_inquiries=data.num_inquiries,
        )

        # Step 2: Predict default probability using trained ML model
        default_prob = predict_default_probability(
            fuzzy_credit_score=fis_result["fuzzy_credit_score"],
            debt_to_income_ratio=data.debt_to_income_ratio,
            credit_utilization=data.credit_utilization,
            existing_emi=data.existing_emi,
            monthly_income=data.monthly_income,
            credit_history_length=data.credit_history_length,
            num_inquiries=data.num_inquiries,
        )

        # Step 3: Generate human-readable explanation
        explanation = generate_explanation(
            fuzzy_credit_score=fis_result["fuzzy_credit_score"],
            debt_to_income_ratio=data.debt_to_income_ratio,
            credit_utilization=data.credit_utilization,
            existing_emi=data.existing_emi,
            monthly_income=data.monthly_income,
            credit_history_length=data.credit_history_length,
            num_inquiries=data.num_inquiries,
            default_probability=default_prob,
            risk_level=fis_result["risk_level"],
        )

        # Step 4: Build final response
        return {
            "fuzzy_credit_score": fis_result["fuzzy_credit_score"],
            "score_band": fis_result["score_band"],
            "risk_level": fis_result["risk_level"],
            "demographic_score": fis_result["demographic_score"],
            "financial_score": fis_result["financial_score"],
            "asset_score": fis_result["asset_score"],
            "default_probability": default_prob,
            "explanation": explanation,
            "reason_codes": [],  # kept for backward compatibility with Node.js
        }

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.get("/")
def root():
    return {"message": "SmartLoan FIS API is running"}
