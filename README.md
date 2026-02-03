# 🔍 StablePay Verifier

> Verify stablecoin payments on-chain. No custody. No fees. Just truth.

[![PyPI](https://img.shields.io/pypi/v/stablepay-verifier)](https://pypi.org/project/stablepay-verifier/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)

## Why StablePay?

✅ **Read-only** - Never touches your funds  
✅ **Open-source** - Audit every line of code  
✅ **BYO-RPC** - Use your own node for privacy  
✅ **Global** - Works anywhere with internet  
✅ **Simple** - PAID or NOT PAID, that's it  

## Quick Start

```bash
# Install
pip install stablepay-verifier

# Verify a payment
stablepay verify -a 0x742d35... -m 100

# Output
✅ PAYMENT VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Status:        PAID
  Amount:        100.00 USDC
  Transaction:   0x1234...abcd
  Block:         52345678 (150 confirmations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Installation

### From PyPI (Recommended)

```bash
pip install stablepay-verifier
```

### From Source

```bash
git clone https://github.com/Okediya/stablepay-verifier.git
cd stablepay-verifier
pip install -e .
```

### With Poetry

```bash
git clone https://github.com/Okediya/stablepay-verifier.git
cd stablepay-verifier
poetry install
```

## Usage

### Basic Verification

```bash
# Verify 100 USDC payment on Polygon (default)
stablepay verify --address 0x742d35cc6634c0532925a3b844bc9e7595f3a382 --amount 100

# Short form
stablepay verify -a 0x742d35... -m 100
```

### Different Tokens & Chains

```bash
# USDT on Ethereum
stablepay verify -a 0x... -m 50 --token USDT --chain ethereum

# DAI on Arbitrum
stablepay verify -a 0x... -m 1000 -t DAI -c arbitrum
```

### Time Window

```bash
# Search last 7 days
stablepay verify -a 0x... -m 100 --time-window 7d

# Search last 1 hour
stablepay verify -a 0x... -m 100 -w 1h
```

### Custom RPC (BYO-RPC)

```bash
# Use your own RPC endpoint for privacy/reliability
stablepay verify -a 0x... -m 100 --rpc https://your-rpc-endpoint.com
```

### JSON Output (for scripts)

```bash
# Get JSON output
stablepay verify -a 0x... -m 100 --output json

# Use with jq
stablepay verify -a 0x... -m 100 -o json | jq '.status'
```

### Filter by Sender

```bash
# Only count payments from a specific address
stablepay verify -a 0x... -m 100 --sender 0xabc123...
```

## Supported Chains & Tokens

| Chain | USDC | USDT | DAI |
|-------|:----:|:----:|:---:|
| Polygon | ✅ | ✅ | ✅ |
| Ethereum | ✅ | ✅ | ✅ |
| Arbitrum | ✅ | ✅ | ❌ |
| Base | ✅ | ❌ | ❌ |
| Optimism | ✅ | ✅ | ❌ |

Run `stablepay info` to see all supported chains and tokens.

## Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | PAID | Payment verified |
| 1 | NOT_PAID | No matching payment |
| 2 | PARTIAL | Partial payment |
| 3 | PENDING | Awaiting confirmations |
| 10 | ERROR | Invalid input |
| 11 | RPC_ERROR | Network error |

Use exit codes in scripts:

```bash
stablepay verify -a 0x... -m 100 -q && echo "Payment received!"
```

## Configuration

### Command Line Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--address` | `-a` | Required | Receiver wallet address |
| `--amount` | `-m` | Required | Expected payment amount |
| `--token` | `-t` | USDC | Token symbol |
| `--chain` | `-c` | polygon | Blockchain network |
| `--rpc` | `-r` | Auto | Custom RPC endpoint |
| `--time-window` | `-w` | 24h | Search time window |
| `--sender` | `-s` | Any | Filter by sender |
| `--min-confirmations` | | 12 | Required confirmations |
| `--tolerance` | | 0.01 | Amount tolerance (1%) |
| `--output` | `-o` | text | Output format |
| `--quiet` | `-q` | | Minimal output |
| `--verbose` | `-v` | | Debug info |

## Use Cases

### Freelancers
Verify client payments before delivering work:
```bash
stablepay verify -a $MY_WALLET -m 500 -w 24h
```

### E-commerce Integration
Check payments in your backend:
```python
from stablepay_verifier import verify_payment, VerifyRequest

result = verify_payment(VerifyRequest(
    address="0x...",
    amount=99.99,
    token="USDC",
    chain="polygon",
))

if result.is_paid:
    process_order()
```

### Automated Systems
Use in CI/CD or cron jobs:
```bash
#!/bin/bash
if stablepay verify -a $WALLET -m $AMOUNT -q; then
    echo "Payment confirmed, proceeding..."
    ./next_step.sh
else
    echo "Payment not found"
    exit 1
fi
```

## BYO-RPC Model

Public RPCs have rate limits and privacy concerns. For production use, we recommend using your own RPC endpoint:

- [Alchemy](https://www.alchemy.com/) - Free tier available
- [Infura](https://infura.io/) - Free tier available
- [QuickNode](https://www.quicknode.com/) - Free tier available
- Self-hosted node

```bash
stablepay verify -a 0x... -m 100 --rpc https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
```

## Development

### Setup

```bash
git clone https://github.com/Okediya/stablepay-verifier.git
cd stablepay-verifier
poetry install --with dev
```

### Run Tests

```bash
poetry run pytest
```

### Lint & Format

```bash
poetry run ruff check .
poetry run ruff format .
```

### Type Check

```bash
poetry run mypy src
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Security

This tool is **read-only** and never requests private keys or signing capabilities. It only queries public blockchain data.

If you find a security issue, please report it privately to security@example.com.

---

**Built with ❤️ for the global stablecoin community**
