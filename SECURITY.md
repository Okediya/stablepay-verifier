# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Model

StablePay Verifier is designed with security as a core principle:

### Read-Only Operations

- The tool **never** requests private keys
- The tool **never** signs transactions
- The tool **never** modifies blockchain state
- It only reads publicly available blockchain data

### No Custody

- We do not store or handle any funds
- We do not have access to your wallet
- All verification is done by querying public RPC endpoints

### BYO-RPC

- Users can bring their own RPC endpoints
- This ensures privacy of query data
- No reliance on centralized infrastructure

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately:

1. **DO NOT** create a public GitHub issue
2. Email security@example.com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

### Response Timeline

- **24 hours**: Initial acknowledgment
- **72 hours**: Preliminary assessment
- **7 days**: Fix development (for critical issues)
- **30 days**: Public disclosure (coordinated)

## Best Practices for Users

1. **Use your own RPC endpoint** for production use
2. **Verify the source** - clone from official repository
3. **Check releases** - use tagged releases, not main branch
4. **Review dependencies** - keep dependencies updated

## Dependencies

We regularly audit and update our dependencies:

- web3.py - Core blockchain interaction
- typer - CLI framework
- pydantic - Data validation
- rich - Terminal output

Run `pip audit` to check for known vulnerabilities.
