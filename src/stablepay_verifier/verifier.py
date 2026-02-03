"""
Core payment verification logic for StablePay Verifier.
"""

from datetime import datetime, timezone
from typing import Optional

from web3 import Web3
from web3.exceptions import Web3Exception

from stablepay_verifier.chains import (
    ERC20_ABI,
    TRANSFER_EVENT_SIGNATURE,
    get_chain_config,
    get_token_config,
)
from stablepay_verifier.models import (
    PaymentResult,
    PaymentStatus,
    Transfer,
    VerifyRequest,
)
from stablepay_verifier.utils import (
    estimate_blocks_from_time,
    parse_time_window,
    wei_to_token,
)


class VerificationError(Exception):
    """Custom exception for verification errors."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


def verify_payment(request: VerifyRequest) -> PaymentResult:
    """
    Verify a stablecoin payment on-chain.
    
    Args:
        request: VerifyRequest with payment details
    
    Returns:
        PaymentResult with verification status and details
    
    Raises:
        VerificationError: If verification fails due to configuration or network issues
    """
    # Get chain configuration
    chain_config = get_chain_config(request.chain)
    if chain_config is None:
        raise VerificationError(
            f"Chain '{request.chain}' is not supported. "
            f"Supported chains: polygon, ethereum, arbitrum, base, optimism",
            code="UNSUPPORTED_CHAIN"
        )
    
    # Get token configuration
    token_config = get_token_config(request.chain, request.token)
    if token_config is None:
        raise VerificationError(
            f"Token '{request.token}' not found on {request.chain}. "
            f"Check the token symbol or provide a contract address.",
            code="UNSUPPORTED_TOKEN"
        )
    
    # Connect to RPC
    rpc_url = request.rpc or chain_config.default_rpc
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
        if not w3.is_connected():
            raise VerificationError(
                f"Failed to connect to RPC endpoint: {rpc_url}",
                code="RPC_ERROR"
            )
    except Exception as e:
        raise VerificationError(
            f"RPC connection error: {str(e)}",
            code="RPC_ERROR"
        )
    
    # Determine block range
    try:
        current_block = w3.eth.block_number
    except Web3Exception as e:
        raise VerificationError(
            f"Failed to get current block number: {str(e)}",
            code="RPC_ERROR"
        )
    
    # Calculate from_block based on time window or explicit value
    if request.from_block is not None:
        from_block = request.from_block
    else:
        time_delta = parse_time_window(request.time_window)
        blocks_to_search = estimate_blocks_from_time(time_delta, chain_config.block_time)
        from_block = max(0, current_block - blocks_to_search)
    
    to_block = request.to_block or current_block
    
    # Validate block range
    max_block_range = 100000
    if to_block - from_block > max_block_range:
        raise VerificationError(
            f"Block range too large ({to_block - from_block} blocks). "
            f"Maximum is {max_block_range} blocks. Narrow your search.",
            code="RANGE_TOO_LARGE"
        )
    
    # Prepare address for event filtering
    receiver_address = Web3.to_checksum_address(request.address)
    token_address = Web3.to_checksum_address(token_config.address)
    
    # Build event filter for Transfer events
    # Transfer(address indexed from, address indexed to, uint256 value)
    # Topic[0] = event signature
    # Topic[1] = from address (optional filter)
    # Topic[2] = to address (our receiver)
    
    topics = [
        TRANSFER_EVENT_SIGNATURE,  # Transfer event signature
        None,  # from: any sender (or filtered below)
        "0x" + receiver_address[2:].lower().zfill(64),  # to: our receiver (padded)
    ]
    
    # Add sender filter if specified
    if request.sender:
        sender_address = Web3.to_checksum_address(request.sender)
        topics[1] = "0x" + sender_address[2:].lower().zfill(64)
    
    # Fetch Transfer events
    try:
        logs = w3.eth.get_logs({
            "address": token_address,
            "topics": topics,
            "fromBlock": from_block,
            "toBlock": to_block,
        })
    except Web3Exception as e:
        error_msg = str(e).lower()
        if "rate" in error_msg or "limit" in error_msg:
            raise VerificationError(
                "RPC rate limit exceeded. Try again later or use a custom RPC endpoint.",
                code="RATE_LIMITED"
            )
        raise VerificationError(
            f"Failed to fetch transfer events: {str(e)}",
            code="RPC_ERROR"
        )
    
    # Process transfer logs
    transfers: list[Transfer] = []
    total_received = 0
    
    for log in logs:
        # Decode the transfer amount from data
        raw_amount = int(log["data"].hex(), 16)
        amount = wei_to_token(raw_amount, token_config.decimals)
        
        # Get sender from topics[1]
        sender_topic = log["topics"][1].hex()
        sender = Web3.to_checksum_address("0x" + sender_topic[-40:])
        
        # Calculate confirmations
        block_number = log["blockNumber"]
        confirmations = current_block - block_number
        
        # Skip if not enough confirmations
        if confirmations < request.min_confirmations:
            # Still add to transfers but mark as pending
            transfers.append(Transfer(
                tx_hash=log["transactionHash"].hex(),
                block_number=block_number,
                sender=sender.lower(),
                receiver=receiver_address.lower(),
                amount=amount,
                raw_amount=raw_amount,
                confirmations=confirmations,
            ))
            continue
        
        # Verify transaction success
        try:
            receipt = w3.eth.get_transaction_receipt(log["transactionHash"])
            if receipt["status"] != 1:
                continue  # Skip failed transactions
        except Web3Exception:
            continue  # Skip if we can't get receipt
        
        # Get block timestamp
        try:
            block = w3.eth.get_block(block_number)
            timestamp = datetime.fromtimestamp(block["timestamp"], tz=timezone.utc)
        except Web3Exception:
            timestamp = None
        
        transfer = Transfer(
            tx_hash=log["transactionHash"].hex(),
            block_number=block_number,
            sender=sender.lower(),
            receiver=receiver_address.lower(),
            amount=amount,
            raw_amount=raw_amount,
            timestamp=timestamp,
            confirmations=confirmations,
        )
        transfers.append(transfer)
        total_received += amount
    
    # Determine payment status
    tolerance_amount = request.amount * request.tolerance
    min_acceptable = request.amount - tolerance_amount
    
    # Check for pending transfers (not enough confirmations)
    pending_amount = sum(t.amount for t in transfers if t.confirmations < request.min_confirmations)
    confirmed_amount = total_received
    
    if confirmed_amount >= min_acceptable:
        status = PaymentStatus.PAID
    elif confirmed_amount > 0:
        status = PaymentStatus.PARTIAL
    elif pending_amount >= min_acceptable:
        status = PaymentStatus.PENDING
    else:
        status = PaymentStatus.NOT_PAID
    
    # Get the most recent confirmed transfer for result details
    confirmed_transfers = [t for t in transfers if t.confirmations >= request.min_confirmations]
    latest_transfer: Optional[Transfer] = None
    if confirmed_transfers:
        latest_transfer = max(confirmed_transfers, key=lambda t: t.block_number)
    
    return PaymentResult(
        status=status,
        expected_amount=request.amount,
        matched_amount=confirmed_amount,
        transaction_hash=latest_transfer.tx_hash if latest_transfer else None,
        block_number=latest_transfer.block_number if latest_transfer else None,
        timestamp=latest_transfer.timestamp if latest_transfer else None,
        confirmations=latest_transfer.confirmations if latest_transfer else 0,
        sender=latest_transfer.sender if latest_transfer else None,
        receiver=request.address.lower(),
        token=request.token,
        chain=request.chain,
        transfers=transfers,
    )
