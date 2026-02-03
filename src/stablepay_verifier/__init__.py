"""
StablePay Verifier - Verify stablecoin payments on-chain.

No custody. No fees. Just truth.
"""

__version__ = "0.1.0"
__app_name__ = "stablepay"

from stablepay_verifier.models import PaymentResult, PaymentStatus, VerifyRequest
from stablepay_verifier.verifier import verify_payment

__all__ = [
    "verify_payment",
    "PaymentResult",
    "PaymentStatus",
    "VerifyRequest",
]
