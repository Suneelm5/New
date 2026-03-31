"""Payment and AI feature primitives for the starter service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from random import Random


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    status: str
    transaction_id: str


class PaymentGateway:
    """Simple orchestrator supporting Google Pay and Paytm."""

    supported_methods = ["google_pay", "paytm"]

    def create_payment_intent(self, payload: dict) -> dict:
        method = payload["payment_method"].lower().strip()
        if method not in self.supported_methods:
            raise ValueError("Unsupported payment method. Use google_pay or paytm.")

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

    def _send_to_provider(self, method: str, payload: dict) -> ProviderResult:
        """Mock provider layer; replace with official SDK/API integrations."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        digest = sha256(f"{payload['customer_id']}-{payload['amount']}-{ts}".encode()).hexdigest()[:12]
        if method == "google_pay":
            return ProviderResult("google_pay", "authorized", f"gpay_{digest}")
        return ProviderResult("paytm", "authorized", f"paytm_{digest}")

    def _fraud_score(self, payload: dict) -> int:
        seed = f"{payload['customer_id']}|{payload['amount']}|{payload['currency']}"
        return Random(seed).randint(5, 95)

    @staticmethod
    def _next_action(fraud_score: int) -> str:
        if fraud_score < 35:
            return "auto_capture"
        if fraud_score < 70:
            return "require_3ds_or_otp"
        return "manual_review"
