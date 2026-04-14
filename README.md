# AI Payment Gateway (Google Pay + Paytm) Starter

This project is a runnable starter API for a payment gateway that:
- accepts **Google Pay** and **Paytm**,
- applies AI-style fraud scoring before authorization,
- generates customer AI insights (churn risk, upsell score, next best action),
- queues merchant earnings payout requests to wallet addresses (including Opera wallet-compatible EVM addresses).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```


## Install CLI

Run after creating your virtualenv:

```bash
pip install -r requirements.txt
```

Use the CLI:

```bash
python -m app.cli methods
python -m app.cli create-intent --amount 1999 --currency INR --customer-id cust_1 --payment-method paytm
python -m app.cli insights --customer-id cust_1 --monthly-spend 900 --failed-payments-30d 1 --support-tickets-30d 0
python -m app.cli wallet-payout --merchant-id m_001 --amount 250 --currency USD --wallet-address 0x1234567890abcdef1234567890abcdef12345678 --network OP
```

## Launch with Docker (quick project launch)

```bash
docker compose up --build
```

API docs: `http://127.0.0.1:8000/docs`

## Endpoints
- `GET /health`
- `GET /v1/payment-methods`
- `POST /v1/payment_intents`
- `POST /v1/ai/customer-insights`
- `POST /v1/payouts/wallet`

## Wallet payout example

```json
{
  "merchant_id": "m_001",
  "amount": 1250.75,
  "currency": "USD",
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "network": "OP"
}
```

## Important limitation
I can prepare the project and payout flow, but I cannot personally launch your live business accounts, sign in to Google AI Studio, or transfer real money to your wallet from here.

To use Google AI Studio yourself:
1. Open https://aistudio.google.com/
2. Sign in with your Google account
3. Create an API key
4. Integrate the key in your backend AI services

See full plan in [`docs/AI_PAYMENT_GATEWAY_SYSTEM.md`](docs/AI_PAYMENT_GATEWAY_SYSTEM.md).
