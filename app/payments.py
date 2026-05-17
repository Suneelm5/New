"""Payment and AI feature primitives for the starter service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from random import Random
import re


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    status: str
    transaction_id: str


class PaymentGateway:
    """Simple orchestrator supporting Google Pay and Paytm."""

    supported_methods = ["google_pay", "paytm", "google_pay_upi"]
    _upi_vpa_pattern = re.compile(r"^[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}$")

    def create_payment_intent(self, payload: dict) -> dict:
        method = payload["payment_method"].lower().strip()
        if method not in self.supported_methods:
            raise ValueError("Unsupported payment method. Use google_pay, google_pay_upi, or paytm.")

        if method == "google_pay_upi":
            return self.create_google_pay_upi_collect(payload)

        fraud_score = self._fraud_score(payload)
        if fraud_score >= 80:
            return {
                "status": "blocked",
                "reason": "high_risk_transaction",
                "fraud_score": fraud_score,
            }

        provider_result = self._send_to_provider(method, payload)
        return {
            "status": provider_result.status,
            "provider": provider_result.provider,
            "transaction_id": provider_result.transaction_id,
            "fraud_score": fraud_score,
            "recommended_next_action": self._next_action(fraud_score),
        }

    def create_google_pay_upi_collect(self, payload: dict) -> dict:
        """Queue a Google Pay UPI collect request."""
        vpa = payload.get("upi_vpa", "").strip().lower()
        if not self._is_valid_vpa(vpa):
            raise ValueError("Invalid UPI VPA format. Example: name@okhdfcbank")

        if int(payload["amount"]) <= 0:
            raise ValueError("Amount must be greater than zero.")

        fraud_score = self._fraud_score(payload)
        collect_digest = sha256(
            f"{payload['customer_id']}|{payload['amount']}|{payload['currency']}|{vpa}".encode()
        ).hexdigest()[:14]

        status = "pending_user_approval" if fraud_score < 85 else "blocked"
        next_action = "await_upi_collect_approval" if status == "pending_user_approval" else "manual_review"

        return {
            "status": status,
            "provider": "google_pay_upi",
            "collect_id": f"gupi_{collect_digest}",
            "upi_vpa": vpa,
            "fraud_score": fraud_score,
            "recommended_next_action": next_action,
            "expires_in_seconds": 300,
        }

    def get_google_pay_upi_status(self, collect_id: str) -> dict:
        if not collect_id.startswith("gupi_"):
            raise ValueError("Invalid collect_id.")

        status_seed = sha256(collect_id.encode()).hexdigest()[-1]
        if status_seed in {"0", "1", "2", "3"}:
            payment_status = "success"
        elif status_seed in {"4", "5", "6"}:
            payment_status = "pending"
        else:
            payment_status = "failed"

        return {
            "collect_id": collect_id,
            "provider": "google_pay_upi",
            "payment_status": payment_status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_customer_ai_features(self, features: dict) -> dict:
        """Returns practical AI outputs for better conversion and retention."""
        monthly_spend = float(features.get("monthly_spend", 0))
        failed = int(features.get("failed_payments_30d", 0))
        tickets = int(features.get("support_tickets_30d", 0))

        churn_risk = max(0, min(100, round(failed * 12 + tickets * 8 - monthly_spend * 0.05)))
        upsell_score = max(0, min(100, round(monthly_spend * 0.08 - failed * 4)))

        recommendation = "offer_premium_plan" if upsell_score >= 65 else "offer_discount_coupon"
        support_priority = "high" if churn_risk >= 60 else "normal"

        return {
            "customer_id": features["customer_id"],
            "churn_risk": churn_risk,
            "upsell_score": upsell_score,
            "recommendation": recommendation,
            "support_priority": support_priority,
        }

    def request_wallet_payout(self, payload: dict) -> dict:
        """Queue earnings payout to a wallet address (example: Opera wallet EVM address)."""
        wallet_address = payload["wallet_address"].strip()
        network = payload.get("network", "OP").upper()

        if not self._looks_like_evm_address(wallet_address):
            raise ValueError("Invalid wallet address. Provide a valid EVM address (0x...).")
        if payload["amount"] <= 0:
            raise ValueError("Payout amount must be greater than zero.")

        payout_digest = sha256(
            f"{payload['merchant_id']}|{payload['amount']}|{payload['currency']}|{wallet_address}".encode()
        ).hexdigest()[:14]

        return {
            "status": "queued",
            "payout_id": f"po_{payout_digest}",
            "network": network,
            "wallet_address": wallet_address,
            "estimated_settlement": "T+1 business day",
            "note": "This starter queues payouts only. Connect a real custody/payout rail for live transfers.",
        }

    def _send_to_provider(self, method: str, payload: dict) -> ProviderResult:
        """Mock provider layer; replace with official SDK/API integrations."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        digest = sha256(f"{payload['customer_id']}-{payload['amount']}-{ts}".encode()).hexdigest()[:12]
        if method == "google_pay":
            return ProviderResult("google_pay", "authorized", f"gpay_{digest}")
        return ProviderResult("paytm", "authorized", f"paytm_{digest}")

    def _fraud_score(self, payload: dict) -> int:
        seed = f"{payload.get('customer_id','na')}|{payload['amount']}|{payload['currency']}"
        return Random(seed).randint(5, 95)

    def _is_valid_vpa(self, vpa: str) -> bool:
        return bool(self._upi_vpa_pattern.match(vpa))

    @staticmethod
    def _looks_like_evm_address(wallet_address: str) -> bool:
        return wallet_address.startswith("0x") and len(wallet_address) == 42

    @staticmethod
    def _next_action(fraud_score: int) -> str:
        if fraud_score < 35:
            return "auto_capture"
        if fraud_score < 70:
            return "require_3ds_or_otp"
        return "manual_review"
