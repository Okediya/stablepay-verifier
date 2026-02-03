"""
Pydantic models for StablePay Verifier.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaymentStatus(str, Enum):
    """Payment verification status."""
    
    PAID = "PAID"
    NOT_PAID = "NOT_PAID"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


class ChainConfig(BaseModel):
    """Configuration for a blockchain network."""
    
    name: str
    chain_id: int
    default_rpc: str
    block_time: float = 2.0  # Average block time in seconds
    explorer_url: str = ""


class TokenConfig(BaseModel):
    """Configuration for a token on a specific chain."""
    
    symbol: str
    name: str
    address: str
    decimals: int = 6


class Transfer(BaseModel):
    """Represents a single token transfer event."""
    
    tx_hash: str
    block_number: int
    sender: str
    receiver: str
    amount: float  # Human-readable amount (after decimal conversion)
    raw_amount: int  # Raw amount in wei/smallest unit
    timestamp: Optional[datetime] = None
    confirmations: int = 0


class VerifyRequest(BaseModel):
    """Request parameters for payment verification."""
    
    address: str = Field(..., description="Receiver wallet address")
    amount: float = Field(..., gt=0, description="Expected payment amount")
    token: str = Field(default="USDC", description="Token symbol")
    chain: str = Field(default="polygon", description="Blockchain network")
    rpc: Optional[str] = Field(default=None, description="Custom RPC endpoint")
    sender: Optional[str] = Field(default=None, description="Filter by sender address")
    time_window: str = Field(default="24h", description="Time window to search")
    from_block: Optional[int] = Field(default=None, description="Starting block number")
    to_block: Optional[int] = Field(default=None, description="Ending block number")
    min_confirmations: int = Field(default=12, ge=0, description="Minimum confirmations")
    tolerance: float = Field(default=0.01, ge=0, le=1, description="Amount tolerance (0.01 = 1%)")
    
    @field_validator("address", "sender", mode="before")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate Ethereum address format."""
        if v is None:
            return None
        v = v.strip()
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid address format. Expected 0x followed by 40 hex characters.")
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("Invalid address format. Contains non-hexadecimal characters.")
        return v.lower()
    
    @field_validator("chain", mode="before")
    @classmethod
    def validate_chain(cls, v: str) -> str:
        """Normalize chain name."""
        return v.lower().strip()
    
    @field_validator("token", mode="before")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Normalize token symbol."""
        return v.upper().strip()
    
    @field_validator("time_window", mode="before")
    @classmethod
    def validate_time_window(cls, v: str) -> str:
        """Validate time window format."""
        v = v.lower().strip()
        if not any(v.endswith(unit) for unit in ["h", "d", "m"]):
            raise ValueError("Invalid time window format. Use: 1h, 24h, 7d, 30d")
        try:
            int(v[:-1])
        except ValueError:
            raise ValueError("Invalid time window format. Number must precede unit.")
        return v


class PaymentResult(BaseModel):
    """Result of a payment verification."""
    
    status: PaymentStatus
    expected_amount: float
    matched_amount: float = 0.0
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    confirmations: int = 0
    sender: Optional[str] = None
    receiver: str
    token: str
    chain: str
    transfers: list[Transfer] = Field(default_factory=list)
    error: Optional[str] = None
    
    @property
    def is_paid(self) -> bool:
        """Check if payment was verified."""
        return self.status == PaymentStatus.PAID
    
    @property
    def shortfall(self) -> float:
        """Calculate the remaining amount needed."""
        return max(0, self.expected_amount - self.matched_amount)
