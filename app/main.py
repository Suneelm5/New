"""Minimal AI payment gateway starter API.

This starter focuses on:
- accepting Google Pay and Paytm as supported payment methods,
- adding Google Pay UPI collect + status flow,
- adding AI-driven fraud checks and customer features,
- queueing merchant payouts to wallet addresses.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .payments import PaymentGateway

app = FastAPI(title="AI Payment Gateway Starter", version="0.4.0")
gateway = PaymentGateway()


class PaymentIntentRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in minor units (e.g., cents/paise)")
    currency: str = Field(min_length=3, max_length=3)
    customer_id: str
    payment_method: str = Field(description="google_pay, google_pay_upi, or paytm")
    upi_vpa: str | None = None
    metadata: dict = Field(default_factory=dict)


class FeatureRequest(BaseModel):
    customer_id: str
    monthly_spend: float = 0
    failed_payments_30d: int = 0
    support_tickets_30d: int = 0


class WalletPayoutRequest(BaseModel):
    merchant_id: str
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    wallet_address: str
    network: str = "OP"


class GooglePayUpiCollectRequest(BaseModel):
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    customer_id: str
    upi_vpa: str


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


@app.post("/v1/google-pay-upi/collect")
def google_pay_upi_collect(payload: GooglePayUpiCollectRequest) -> dict:
    try:
        return gateway.create_google_pay_upi_collect(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/google-pay-upi/status/{collect_id}")
def google_pay_upi_status(collect_id: str) -> dict:
    try:
        return gateway.get_google_pay_upi_status(collect_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/ai/customer-insights")
def customer_insights(payload: FeatureRequest) -> dict:
    return gateway.generate_customer_ai_features(payload.model_dump())


@app.post("/v1/payouts/wallet")
def wallet_payout(payload: WalletPayoutRequest) -> dict:
    try:
        return gateway.request_wallet_payout(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
