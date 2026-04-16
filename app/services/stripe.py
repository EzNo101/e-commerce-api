import stripe

from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    def construct_webhook_event(self, payload: bytes, signature: str) -> stripe.Event:
        return stripe.Webhook.construct_event(  # pyright: ignore[reportUnknownMemberType]
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

    def create_payment_intent(
        self,
        amount: int,
        currency: str,
        order_id: int,
        idempotency_key: str,
    ) -> stripe.PaymentIntent:
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={"order_id": str(order_id)},
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never",
            },
            idempotency_key=idempotency_key,
        )
