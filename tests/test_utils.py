"""Tests for utility functions."""

from datetime import timedelta

import pytest

from stablepay_verifier.utils import (
    calculate_tolerance_range,
    estimate_blocks_from_time,
    format_address,
    format_amount,
    is_valid_address,
    parse_time_window,
    token_to_wei,
    wei_to_token,
)


class TestParseTimeWindow:
    """Tests for parse_time_window function."""
    
    def test_parse_hours(self) -> None:
        """Test parsing hour time windows."""
        assert parse_time_window("1h") == timedelta(hours=1)
        assert parse_time_window("24h") == timedelta(hours=24)
        assert parse_time_window("168h") == timedelta(hours=168)
    
    def test_parse_days(self) -> None:
        """Test parsing day time windows."""
        assert parse_time_window("1d") == timedelta(days=1)
        assert parse_time_window("7d") == timedelta(days=7)
        assert parse_time_window("30d") == timedelta(days=30)
    
    def test_parse_minutes(self) -> None:
        """Test parsing minute time windows."""
        assert parse_time_window("30m") == timedelta(minutes=30)
        assert parse_time_window("60m") == timedelta(minutes=60)
    
    def test_case_insensitive(self) -> None:
        """Test case insensitivity."""
        assert parse_time_window("24H") == timedelta(hours=24)
        assert parse_time_window("7D") == timedelta(days=7)
    
    def test_invalid_format(self) -> None:
        """Test invalid formats raise ValueError."""
        with pytest.raises(ValueError):
            parse_time_window("invalid")
        
        with pytest.raises(ValueError):
            parse_time_window("24")
        
        with pytest.raises(ValueError):
            parse_time_window("h24")


class TestEstimateBlocks:
    """Tests for estimate_blocks_from_time function."""
    
    def test_basic_estimation(self) -> None:
        """Test basic block estimation."""
        # 1 hour with 2 second blocks = 1800 blocks
        assert estimate_blocks_from_time(timedelta(hours=1), 2.0) == 1800
    
    def test_minimum_one_block(self) -> None:
        """Test minimum is 1 block."""
        assert estimate_blocks_from_time(timedelta(seconds=0.1), 2.0) == 1


class TestFormatAddress:
    """Tests for format_address function."""
    
    def test_short_address(self) -> None:
        """Test address shortening."""
        address = "0x742d35cc6634c0532925a3b844bc9e7595f3a382"
        result = format_address(address, 4)
        assert result == "0x742d...a382"
    
    def test_already_short(self) -> None:
        """Test short addresses aren't modified."""
        short = "0x1234"
        assert format_address(short, 10) == short


class TestFormatAmount:
    """Tests for format_amount function."""
    
    def test_basic_formatting(self) -> None:
        """Test basic amount formatting."""
        assert format_amount(100.0) == "100.00"
        assert format_amount(1000.5) == "1,000.50"
    
    def test_custom_decimals(self) -> None:
        """Test custom decimal places."""
        assert format_amount(100.123, 1) == "100.1"
        assert format_amount(100.123, 4) == "100.1230"


class TestWeiConversion:
    """Tests for wei/token conversion functions."""
    
    def test_wei_to_token_usdc(self) -> None:
        """Test USDC conversion (6 decimals)."""
        # 100 USDC = 100,000,000 smallest units
        assert wei_to_token(100_000_000, 6) == 100.0
    
    def test_wei_to_token_dai(self) -> None:
        """Test DAI conversion (18 decimals)."""
        # 1 DAI = 10^18 wei
        assert wei_to_token(10**18, 18) == 1.0
    
    def test_token_to_wei_usdc(self) -> None:
        """Test token to wei for USDC."""
        assert token_to_wei(100.0, 6) == 100_000_000
    
    def test_token_to_wei_dai(self) -> None:
        """Test token to wei for DAI."""
        assert token_to_wei(1.0, 18) == 10**18


class TestIsValidAddress:
    """Tests for is_valid_address function."""
    
    def test_valid_addresses(self) -> None:
        """Test valid addresses."""
        assert is_valid_address("0x742d35cc6634c0532925a3b844bc9e7595f3a382")
        assert is_valid_address("0x0000000000000000000000000000000000000000")
    
    def test_invalid_addresses(self) -> None:
        """Test invalid addresses."""
        assert not is_valid_address("")
        assert not is_valid_address(None)  # type: ignore
        assert not is_valid_address("invalid")
        assert not is_valid_address("0x123")
        assert not is_valid_address("742d35cc6634c0532925a3b844bc9e7595f3a382")


class TestToleranceRange:
    """Tests for calculate_tolerance_range function."""
    
    def test_one_percent_tolerance(self) -> None:
        """Test 1% tolerance."""
        min_val, max_val = calculate_tolerance_range(100.0, 0.01)
        assert min_val == 99.0
        assert max_val == 101.0
    
    def test_five_percent_tolerance(self) -> None:
        """Test 5% tolerance."""
        min_val, max_val = calculate_tolerance_range(100.0, 0.05)
        assert min_val == 95.0
        assert max_val == 105.0
