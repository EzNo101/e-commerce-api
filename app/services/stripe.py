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
