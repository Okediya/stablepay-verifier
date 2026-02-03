"""Tests for chain and token configurations."""

from stablepay_verifier.chains import (
    CHAINS,
    TOKENS,
    get_chain_config,
    get_supported_chains,
    get_supported_tokens,
    get_token_config,
)


class TestChainConfig:
    """Tests for chain configuration functions."""
    
    def test_get_chain_config(self) -> None:
        """Test getting chain configuration."""
        config = get_chain_config("polygon")
        assert config is not None
        assert config.name == "Polygon"
        assert config.chain_id == 137
    
    def test_get_chain_config_case_insensitive(self) -> None:
        """Test chain config is case insensitive."""
        assert get_chain_config("POLYGON") is not None
        assert get_chain_config("Polygon") is not None
    
    def test_get_chain_config_unknown(self) -> None:
        """Test unknown chain returns None."""
        assert get_chain_config("unknown") is None
    
    def test_get_supported_chains(self) -> None:
        """Test getting list of supported chains."""
        chains = get_supported_chains()
        assert "polygon" in chains
        assert "ethereum" in chains
        assert "arbitrum" in chains
        assert len(chains) >= 5


class TestTokenConfig:
    """Tests for token configuration functions."""
    
    def test_get_token_config(self) -> None:
        """Test getting token configuration."""
        config = get_token_config("polygon", "USDC")
        assert config is not None
        assert config.symbol == "USDC"
        assert config.decimals == 6
    
    def test_get_token_config_case_insensitive(self) -> None:
        """Test token config is case insensitive."""
        assert get_token_config("polygon", "usdc") is not None
        assert get_token_config("POLYGON", "USDC") is not None
    
    def test_get_token_config_unknown(self) -> None:
        """Test unknown token returns None."""
        assert get_token_config("polygon", "UNKNOWN") is None
    
    def test_get_supported_tokens(self) -> None:
        """Test getting list of supported tokens."""
        tokens = get_supported_tokens("polygon")
        assert "USDC" in tokens
        assert "USDT" in tokens


class TestChainData:
    """Tests for chain data integrity."""
    
    def test_all_chains_have_rpcs(self) -> None:
        """Test all chains have default RPC URLs."""
        for name, config in CHAINS.items():
            assert config.default_rpc, f"{name} missing default RPC"
            assert config.default_rpc.startswith("http")
    
    def test_all_chains_have_tokens(self) -> None:
        """Test all chains have at least one token."""
        for chain in CHAINS:
            tokens = TOKENS.get(chain, {})
            assert len(tokens) >= 1, f"{chain} has no tokens"
    
    def test_usdc_on_all_chains(self) -> None:
        """Test USDC is available on all chains."""
        for chain in CHAINS:
            token = get_token_config(chain, "USDC")
            assert token is not None, f"USDC missing on {chain}"
            assert token.decimals == 6
