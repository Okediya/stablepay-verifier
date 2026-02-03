# Contributing to StablePay Verifier

Thank you for your interest in contributing to StablePay Verifier! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and inclusive in all interactions. We welcome contributors of all backgrounds and experience levels.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/stablepay-verifier/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version)

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use cases

### Submitting Code

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following our coding standards
5. **Write tests** for new functionality
6. **Run the test suite**:
   ```bash
   poetry run pytest
   ```
7. **Lint your code**:
   ```bash
   poetry run ruff check .
   poetry run ruff format .
   ```
8. **Type check**:
   ```bash
   poetry run mypy src
   ```
9. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add support for new token"
   ```
10. **Push** to your fork
11. **Open a Pull Request**

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/stablepay-verifier.git
cd stablepay-verifier

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=stablepay_verifier

# Specific test file
poetry run pytest tests/test_models.py
```

## Coding Standards

### Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for public functions

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

### Pull Request Guidelines

- Keep PRs focused and small
- Include tests for new features
- Update documentation as needed
- Ensure CI passes

## Adding New Chains

To add support for a new blockchain:

1. Add chain config in `src/stablepay_verifier/chains.py`:
   ```python
   "newchain": ChainConfig(
       name="New Chain",
       chain_id=12345,
       default_rpc="https://rpc.newchain.io",
       block_time=2.0,
       explorer_url="https://explorer.newchain.io",
   ),
   ```

2. Add token addresses for the chain in `TOKENS`

3. Add tests in `tests/test_chains.py`

4. Update README to reflect the new chain

## Adding New Tokens

To add support for a new stablecoin:

1. Find the token contract address on each chain
2. Add to `TOKENS` in `src/stablepay_verifier/chains.py`
3. Verify the decimals (usually 6 for USDC/USDT, 18 for DAI)
4. Add tests

## Questions?

Feel free to open an issue for any questions about contributing!
