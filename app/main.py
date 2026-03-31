"""Minimal AI payment gateway starter API.

This starter focuses on:
- accepting Google Pay and Paytm as supported payment methods,
- adding AI-driven fraud checks and customer features,
- exposing simple endpoints that can be extended for production.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .payments import PaymentGateway

app = FastAPI(title="AI Payment Gateway Starter", version="0.2.0")
gateway = PaymentGateway()


class PaymentIntentRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in minor units (e.g., cents/paise)")
    currency: str = Field(min_length=3, max_length=3)
    customer_id: str
    payment_method: str = Field(description="google_pay or paytm")
    metadata: dict = Field(default_factory=dict)


class FeatureRequest(BaseModel):
    customer_id: str
    monthly_spend: float = 0
    failed_payments_30d: int = 0
    support_tickets_30d: int = 0


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/v1/payment-methods")
def payment_methods() -> dict:
    return {"supported": gateway.supported_methods}


@app.post("/v1/payment_intents")
def create_payment_intent(payload: PaymentIntentRequest) -> dict:
    try:
        return gateway.create_payment_intent(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/ai/customer-insights")
def customer_insights(payload: FeatureRequest) -> dict:
    return gateway.generate_customer_ai_features(payload.model_dump())
