# AI Payment Gateway (Google Pay + Paytm) Starter

This project now includes a runnable starter API for a payment gateway that:
- accepts **Google Pay** and **Paytm**,
- applies AI-style fraud scoring before authorization,
- generates customer AI insights (churn risk, upsell score, next best action).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Endpoints
- `GET /health`
- `GET /v1/payment-methods`
- `POST /v1/payment_intents`
- `POST /v1/ai/customer-insights`

## Request example: create payment intent

```json
{
  "amount": 1999,
  "currency": "INR",
  "customer_id": "cust_123",
  "payment_method": "paytm",
  "metadata": {"order_id": "ord_1"}
}
```

## Note on "run Google AI Studio" and registration
I cannot sign in or register accounts for you directly. To use Google AI Studio:
1. Open https://aistudio.google.com/
2. Sign in with your Google account
3. Create an API key
4. Use that key in your backend for AI tasks (assistants, summarization, support copilots)

See detailed product/earning plan in [`docs/AI_PAYMENT_GATEWAY_SYSTEM.md`](docs/AI_PAYMENT_GATEWAY_SYSTEM.md).
