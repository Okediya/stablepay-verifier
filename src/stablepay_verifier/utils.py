"""
Utility functions for StablePay Verifier.
"""

import re
from datetime import datetime, timedelta, timezone


def parse_time_window(window: str) -> timedelta:
    """
    Parse a time window string into a timedelta.
    
    Args:
        window: Time window string (e.g., "1h", "24h", "7d", "30m")
    
    Returns:
        timedelta representing the time window
    
    Raises:
        ValueError: If the format is invalid
    """
    window = window.lower().strip()
    match = re.match(r"^(\d+)([hdm])$", window)
    
    if not match:
        raise ValueError(f"Invalid time window format: {window}. Use: 1h, 24h, 7d, 30m")
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "m":
        return timedelta(minutes=value)
    else:
        raise ValueError(f"Unknown time unit: {unit}")


def estimate_blocks_from_time(
    time_delta: timedelta,
    block_time_seconds: float = 2.0
) -> int:
    """
    Estimate the number of blocks in a time period.
    
    Args:
        time_delta: Time period to estimate
        block_time_seconds: Average block time in seconds
    
    Returns:
        Estimated number of blocks
    """
    total_seconds = time_delta.total_seconds()
    return max(1, int(total_seconds / block_time_seconds))


def format_address(address: str, length: int = 8) -> str:
    """
    Format an address for display (shortened).
    
    Args:
        address: Full Ethereum address
        length: Number of characters to show on each end
    
    Returns:
        Shortened address (e.g., "0x1234...abcd")
    """
    if len(address) <= length * 2 + 2:
        return address
    return f"{address[:length+2]}...{address[-length:]}"


def format_amount(amount: float, decimals: int = 2) -> str:
    """
    Format an amount for display.
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places
    
    Returns:
        Formatted amount string
    """
    return f"{amount:,.{decimals}f}"


def wei_to_token(wei_amount: int, decimals: int = 6) -> float:
    """
    Convert wei/smallest unit to token amount.
    
    Args:
        wei_amount: Amount in smallest unit
        decimals: Token decimals
    
    Returns:
        Human-readable token amount
    """
    return wei_amount / (10 ** decimals)


def token_to_wei(token_amount: float, decimals: int = 6) -> int:
    """
    Convert token amount to wei/smallest unit.
    
    Args:
        token_amount: Human-readable token amount
        decimals: Token decimals
    
    Returns:
        Amount in smallest unit
    """
    return int(token_amount * (10 ** decimals))


def is_valid_address(address: str) -> bool:
    """
    Check if an address is a valid Ethereum address.
    
    Args:
        address: Address to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
    
    address = address.strip()
    if not address.startswith("0x"):
        return False
    
    if len(address) != 42:
        return False
    
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime | None) -> str:
    """
    Format a datetime for display.
    
    Args:
        dt: Datetime to format
    
    Returns:
        Formatted datetime string or "Unknown"
    """
    if dt is None:
        return "Unknown"
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def calculate_tolerance_range(
    amount: float,
    tolerance_percent: float = 0.01
) -> tuple[float, float]:
    """
    Calculate the acceptable payment range based on tolerance.
    
    Args:
        amount: Expected amount
        tolerance_percent: Tolerance as decimal (0.01 = 1%)
    
    Returns:
        Tuple of (minimum acceptable, maximum acceptable)
    """
    tolerance_amount = amount * tolerance_percent
    return (amount - tolerance_amount, amount + tolerance_amount)
