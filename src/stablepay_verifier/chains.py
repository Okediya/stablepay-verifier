"""
Chain and token configurations for StablePay Verifier.
"""

from stablepay_verifier.models import ChainConfig, TokenConfig

# Supported blockchain networks
CHAINS: dict[str, ChainConfig] = {
    "polygon": ChainConfig(
        name="Polygon",
        chain_id=137,
        default_rpc="https://polygon-rpc.com",
        block_time=2.0,
        explorer_url="https://polygonscan.com",
    ),
    "ethereum": ChainConfig(
        name="Ethereum",
        chain_id=1,
        default_rpc="https://eth.llamarpc.com",
        block_time=12.0,
        explorer_url="https://etherscan.io",
    ),
    "arbitrum": ChainConfig(
        name="Arbitrum One",
        chain_id=42161,
        default_rpc="https://arb1.arbitrum.io/rpc",
        block_time=0.25,
        explorer_url="https://arbiscan.io",
    ),
    "base": ChainConfig(
        name="Base",
        chain_id=8453,
        default_rpc="https://mainnet.base.org",
        block_time=2.0,
        explorer_url="https://basescan.org",
    ),
    "optimism": ChainConfig(
        name="Optimism",
        chain_id=10,
        default_rpc="https://mainnet.optimism.io",
        block_time=2.0,
        explorer_url="https://optimistic.etherscan.io",
    ),
}

# Token contract addresses per chain
# Format: TOKENS[chain][symbol] = TokenConfig
TOKENS: dict[str, dict[str, TokenConfig]] = {
    "polygon": {
        "USDC": TokenConfig(
            symbol="USDC",
            name="USD Coin",
            address="0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
            decimals=6,
        ),
        "USDT": TokenConfig(
            symbol="USDT",
            name="Tether USD",
            address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
            decimals=6,
        ),
        "DAI": TokenConfig(
            symbol="DAI",
            name="Dai Stablecoin",
            address="0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
            decimals=18,
        ),
    },
    "ethereum": {
        "USDC": TokenConfig(
            symbol="USDC",
            name="USD Coin",
            address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            decimals=6,
        ),
        "USDT": TokenConfig(
            symbol="USDT",
            name="Tether USD",
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            decimals=6,
        ),
        "DAI": TokenConfig(
            symbol="DAI",
            name="Dai Stablecoin",
            address="0x6B175474E89094C44Da98b954EesfdC1D3709CEc",
            decimals=18,
        ),
    },
    "arbitrum": {
        "USDC": TokenConfig(
            symbol="USDC",
            name="USD Coin",
            address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            decimals=6,
        ),
        "USDT": TokenConfig(
            symbol="USDT",
            name="Tether USD",
            address="0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
            decimals=6,
        ),
    },
    "base": {
        "USDC": TokenConfig(
            symbol="USDC",
            name="USD Coin",
            address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            decimals=6,
        ),
    },
    "optimism": {
        "USDC": TokenConfig(
            symbol="USDC",
            name="USD Coin",
            address="0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
            decimals=6,
        ),
        "USDT": TokenConfig(
            symbol="USDT",
            name="Tether USD",
            address="0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
            decimals=6,
        ),
    },
}

# ERC20 Transfer event signature
TRANSFER_EVENT_SIGNATURE = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# ERC20 ABI (minimal for transfer events)
ERC20_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def get_chain_config(chain: str) -> ChainConfig | None:
    """Get chain configuration by name."""
    return CHAINS.get(chain.lower())


def get_token_config(chain: str, symbol: str) -> TokenConfig | None:
    """Get token configuration for a chain."""
    chain_tokens = TOKENS.get(chain.lower(), {})
    return chain_tokens.get(symbol.upper())


def get_supported_chains() -> list[str]:
    """Get list of supported chain names."""
    return list(CHAINS.keys())


def get_supported_tokens(chain: str) -> list[str]:
    """Get list of supported tokens for a chain."""
    return list(TOKENS.get(chain.lower(), {}).keys())
