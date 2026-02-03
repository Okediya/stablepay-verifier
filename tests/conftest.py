"""Pytest fixtures for StablePay Verifier tests."""

import pytest


@pytest.fixture
def valid_address() -> str:
    """Return a valid Ethereum address for testing."""
    return "0x742d35cc6634c0532925a3b844bc9e7595f3a382"


@pytest.fixture
def invalid_address() -> str:
    """Return an invalid Ethereum address."""
    return "0xinvalid"


@pytest.fixture
def sample_amount() -> float:
    """Return a sample payment amount."""
    return 100.0


@pytest.fixture
def sample_verify_request(valid_address: str, sample_amount: float):
    """Return a sample VerifyRequest."""
    from stablepay_verifier.models import VerifyRequest
    
    return VerifyRequest(
        address=valid_address,
        amount=sample_amount,
        token="USDC",
        chain="polygon",
    )
