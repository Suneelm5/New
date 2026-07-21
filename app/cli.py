"""CLI for local AI payment gateway operations."""

from __future__ import annotations

import argparse
import json

from .payments import PaymentGateway


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aipg", description="AI Payment Gateway CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("methods", help="Show supported payment methods")

    pay = sub.add_parser("create-intent", help="Create a payment intent")
    pay.add_argument("--amount", type=int, required=True)
    pay.add_argument("--currency", type=str, required=True)
    pay.add_argument("--customer-id", type=str, required=True)
    pay.add_argument("--payment-method", type=str, choices=["google_pay", "google_pay_upi", "paytm"], required=True)
    pay.add_argument("--upi-vpa", type=str)

    upi_collect = sub.add_parser("gpay-upi-collect", help="Create Google Pay UPI collect")
    upi_collect.add_argument("--amount", type=int, required=True)
    upi_collect.add_argument("--currency", type=str, required=True)
    upi_collect.add_argument("--customer-id", type=str, required=True)
    upi_collect.add_argument("--upi-vpa", type=str, required=True)

    upi_status = sub.add_parser("gpay-upi-status", help="Get Google Pay UPI collect status")
    upi_status.add_argument("--collect-id", type=str, required=True)

    insights = sub.add_parser("insights", help="Generate customer AI insights")
    insights.add_argument("--customer-id", type=str, required=True)
    insights.add_argument("--monthly-spend", type=float, default=0)
    insights.add_argument("--failed-payments-30d", type=int, default=0)
    insights.add_argument("--support-tickets-30d", type=int, default=0)

    payout = sub.add_parser("wallet-payout", help="Queue wallet payout")
    payout.add_argument("--merchant-id", type=str, required=True)
    payout.add_argument("--amount", type=float, required=True)
    payout.add_argument("--currency", type=str, required=True)
    payout.add_argument("--wallet-address", type=str, required=True)
    payout.add_argument("--network", type=str, default="OP")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    gateway = PaymentGateway()

    if args.command == "methods":
        result = {"supported": gateway.supported_methods}
    elif args.command == "create-intent":
        result = gateway.create_payment_intent(
            {
                "amount": args.amount,
                "currency": args.currency.upper(),
                "customer_id": args.customer_id,
                "payment_method": args.payment_method,
                "upi_vpa": args.upi_vpa,
                "metadata": {},
            }
        )
    elif args.command == "gpay-upi-collect":
        result = gateway.create_google_pay_upi_collect(
            {
                "amount": args.amount,
                "currency": args.currency.upper(),
                "customer_id": args.customer_id,
                "upi_vpa": args.upi_vpa,
            }
        )
    elif args.command == "gpay-upi-status":
        result = gateway.get_google_pay_upi_status(args.collect_id)
    elif args.command == "insights":
        result = gateway.generate_customer_ai_features(
            {
                "customer_id": args.customer_id,
                "monthly_spend": args.monthly_spend,
                "failed_payments_30d": args.failed_payments_30d,
                "support_tickets_30d": args.support_tickets_30d,
            }
        )
    elif args.command == "wallet-payout":
        result = gateway.request_wallet_payout(
            {
                "merchant_id": args.merchant_id,
                "amount": args.amount,
                "currency": args.currency.upper(),
                "wallet_address": args.wallet_address,
                "network": args.network,
            }
        )
    else:
        parser.error("Unknown command")
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
