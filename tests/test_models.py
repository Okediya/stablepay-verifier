"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from stablepay_verifier.models import (
    PaymentResult,
    PaymentStatus,
    Transfer,
    VerifyRequest,
)


class TestVerifyRequest:
    """Tests for VerifyRequest model."""
    
    def test_valid_request(self, valid_address: str) -> None:
        """Test creating a valid request."""
        request = VerifyRequest(
            address=valid_address,
            amount=100.0,
        )
        assert request.address == valid_address.lower()
        assert request.amount == 100.0
        assert request.token == "USDC"
        assert request.chain == "polygon"
    
    def test_address_validation_invalid_format(self) -> None:
        """Test address validation with invalid format."""
        with pytest.raises(ValidationError):
            VerifyRequest(
                address="invalid",
                amount=100.0,
            )
    
    def test_address_validation_wrong_length(self) -> None:
        """Test address validation with wrong length."""
        with pytest.raises(ValidationError):
            VerifyRequest(
                address="0x123",
                amount=100.0,
            )
    
    def test_address_validation_non_hex(self) -> None:
        """Test address validation with non-hex characters."""
        with pytest.raises(ValidationError):
            VerifyRequest(
                address="0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
                amount=100.0,
            )
    
    def test_amount_must_be_positive(self, valid_address: str) -> None:
        """Test that amount must be positive."""
        with pytest.raises(ValidationError):
            VerifyRequest(
                address=valid_address,
                amount=0,
            )
        
        with pytest.raises(ValidationError):
            VerifyRequest(
                address=valid_address,
                amount=-10,
            )
    
    def test_token_normalized_uppercase(self, valid_address: str) -> None:
        """Test token is normalized to uppercase."""
        request = VerifyRequest(
            address=valid_address,
            amount=100.0,
            token="usdc",
        )
        assert request.token == "USDC"
    
    def test_chain_normalized_lowercase(self, valid_address: str) -> None:
        """Test chain is normalized to lowercase."""
        request = VerifyRequest(
            address=valid_address,
            amount=100.0,
            chain="POLYGON",
        )
        assert request.chain == "polygon"
    
    def test_time_window_validation(self, valid_address: str) -> None:
        """Test time window format validation."""
        # Valid formats
        for window in ["1h", "24h", "7d", "30m"]:
            request = VerifyRequest(
                address=valid_address,
                amount=100.0,
                time_window=window,
            )
            assert request.time_window == window
        
        # Invalid formats
        with pytest.raises(ValidationError):
            VerifyRequest(
                address=valid_address,
                amount=100.0,
                time_window="invalid",
            )
    
    def test_tolerance_bounds(self, valid_address: str) -> None:
        """Test tolerance must be between 0 and 1."""
        # Valid tolerance
        request = VerifyRequest(
            address=valid_address,
            amount=100.0,
            tolerance=0.05,
        )
        assert request.tolerance == 0.05
        
        # Invalid tolerance
        with pytest.raises(ValidationError):
            VerifyRequest(
                address=valid_address,
                amount=100.0,
                tolerance=1.5,
            )


class TestPaymentResult:
    """Tests for PaymentResult model."""
    
    def test_is_paid_property(self, valid_address: str) -> None:
        """Test is_paid property."""
        result = PaymentResult(
            status=PaymentStatus.PAID,
            expected_amount=100.0,
            matched_amount=100.0,
            receiver=valid_address,
            token="USDC",
            chain="polygon",
        )
        assert result.is_paid is True
        
        result.status = PaymentStatus.NOT_PAID
        assert result.is_paid is False
    
    def test_shortfall_property(self, valid_address: str) -> None:
        """Test shortfall property."""
        result = PaymentResult(
            status=PaymentStatus.PARTIAL,
            expected_amount=100.0,
            matched_amount=75.0,
            receiver=valid_address,
            token="USDC",
            chain="polygon",
        )
        assert result.shortfall == 25.0
    
    def test_shortfall_when_overpaid(self, valid_address: str) -> None:
        """Test shortfall is 0 when overpaid."""
        result = PaymentResult(
            status=PaymentStatus.PAID,
            expected_amount=100.0,
            matched_amount=150.0,
            receiver=valid_address,
            token="USDC",
            chain="polygon",
        )
        assert result.shortfall == 0.0


class TestTransfer:
    """Tests for Transfer model."""
    
    def test_transfer_creation(self, valid_address: str) -> None:
        """Test creating a transfer."""
        transfer = Transfer(
            tx_hash="0x" + "a" * 64,
            block_number=12345678,
            sender=valid_address,
            receiver=valid_address,
            amount=100.0,
            raw_amount=100000000,
            confirmations=50,
        )
        assert transfer.amount == 100.0
        assert transfer.confirmations == 50
