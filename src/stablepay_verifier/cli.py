"""
CLI interface for StablePay Verifier.
"""

import json
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from stablepay_verifier import __version__
from stablepay_verifier.chains import (
    CHAINS,
    TOKENS,
    get_supported_chains,
    get_supported_tokens,
)
from stablepay_verifier.models import PaymentStatus, VerifyRequest
from stablepay_verifier.utils import format_address, format_amount, format_timestamp
from stablepay_verifier.verifier import VerificationError, verify_payment

# Initialize Typer app and Rich console
app = typer.Typer(
    name="stablepay",
    help="🔍 Verify stablecoin payments on-chain. No custody. No fees. Just truth.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# Exit codes
EXIT_PAID = 0
EXIT_NOT_PAID = 1
EXIT_PARTIAL = 2
EXIT_PENDING = 3
EXIT_ERROR = 10
EXIT_RPC_ERROR = 11


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]StablePay Verifier[/bold blue] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """
    🔍 StablePay Verifier - Verify stablecoin payments on-chain.
    
    No custody. No fees. Just truth.
    """
    pass


@app.command()
def verify(
    address: str = typer.Option(
        ...,
        "--address",
        "-a",
        help="Receiver wallet address (0x...)",
    ),
    amount: float = typer.Option(
        ...,
        "--amount",
        "-m",
        help="Expected payment amount",
    ),
    token: str = typer.Option(
        "USDC",
        "--token",
        "-t",
        help="Token symbol (USDC, USDT, DAI)",
    ),
    chain: str = typer.Option(
        "polygon",
        "--chain",
        "-c",
        help="Blockchain network (polygon, ethereum, arbitrum, base, optimism)",
    ),
    rpc: Optional[str] = typer.Option(
        None,
        "--rpc",
        "-r",
        help="Custom RPC endpoint URL",
    ),
    time_window: str = typer.Option(
        "24h",
        "--time-window",
        "-w",
        help="Time window to search (e.g., 1h, 24h, 7d)",
    ),
    sender: Optional[str] = typer.Option(
        None,
        "--sender",
        "-s",
        help="Filter by sender address",
    ),
    min_confirmations: int = typer.Option(
        12,
        "--min-confirmations",
        help="Minimum block confirmations required",
    ),
    tolerance: float = typer.Option(
        0.01,
        "--tolerance",
        help="Amount tolerance as decimal (0.01 = 1%%)",
    ),
    output_format: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Output format: text or json",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Minimal output (just status)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show debug information",
    ),
) -> None:
    """
    Verify a stablecoin payment was received.
    
    Examples:
    
        stablepay verify -a 0x742d35... -m 100
        
        stablepay verify -a 0x742d35... -m 50 -t USDT -c ethereum
        
        stablepay verify -a 0x742d35... -m 100 --time-window 7d
    """
    try:
        # Create verification request
        request = VerifyRequest(
            address=address,
            amount=amount,
            token=token,
            chain=chain,
            rpc=rpc,
            sender=sender,
            time_window=time_window,
            min_confirmations=min_confirmations,
            tolerance=tolerance,
        )
    except ValueError as e:
        _handle_error(str(e), "INVALID_INPUT", output_format, quiet)
        raise typer.Exit(EXIT_ERROR)
    
    # Show progress if not quiet
    if not quiet and output_format == "text":
        console.print(f"\n[dim]Verifying {token} payment on {chain.title()}...[/dim]")
    
    # Perform verification
    try:
        result = verify_payment(request)
    except VerificationError as e:
        _handle_error(e.message, e.code, output_format, quiet)
        exit_code = EXIT_RPC_ERROR if e.code == "RPC_ERROR" else EXIT_ERROR
        raise typer.Exit(exit_code)
    except Exception as e:
        _handle_error(f"Unexpected error: {str(e)}", "UNKNOWN_ERROR", output_format, quiet)
        raise typer.Exit(EXIT_ERROR)
    
    # Output results
    if output_format == "json":
        _output_json(result)
    elif quiet:
        _output_quiet(result)
    else:
        _output_rich(result, verbose)
    
    # Set exit code based on status
    exit_code = {
        PaymentStatus.PAID: EXIT_PAID,
        PaymentStatus.NOT_PAID: EXIT_NOT_PAID,
        PaymentStatus.PARTIAL: EXIT_PARTIAL,
        PaymentStatus.PENDING: EXIT_PENDING,
    }.get(result.status, EXIT_ERROR)
    
    raise typer.Exit(exit_code)


@app.command()
def info() -> None:
    """
    Show supported chains and tokens.
    """
    console.print("\n[bold blue]Supported Chains & Tokens[/bold blue]\n")
    
    for chain_name, chain_config in CHAINS.items():
        table = Table(title=f"🔗 {chain_config.name} ({chain_name})", show_header=True)
        table.add_column("Token", style="cyan")
        table.add_column("Name", style="dim")
        table.add_column("Contract Address", style="dim")
        
        tokens = TOKENS.get(chain_name, {})
        for symbol, token_config in tokens.items():
            table.add_row(
                symbol,
                token_config.name,
                format_address(token_config.address, 6),
            )
        
        if not tokens:
            table.add_row("[dim]No tokens configured[/dim]", "", "")
        
        console.print(table)
        console.print()
    
    console.print("[dim]Tip: Use --chain and --token to specify the network and token.[/dim]")
    console.print("[dim]Default: USDC on Polygon[/dim]\n")


def _handle_error(message: str, code: str, output_format: str, quiet: bool) -> None:
    """Handle and display errors."""
    if output_format == "json":
        console.print(json.dumps({
            "status": "ERROR",
            "error_code": code,
            "message": message,
        }))
    elif quiet:
        console.print(f"ERROR: {message}", style="red")
    else:
        console.print()
        console.print(Panel(
            f"[red bold]Error:[/red bold] {message}\n\n"
            f"[dim]Error Code: {code}[/dim]",
            title="❌ Verification Failed",
            border_style="red",
        ))


def _output_json(result) -> None:
    """Output result as JSON."""
    output = {
        "status": result.status.value,
        "expected_amount": result.expected_amount,
        "matched_amount": result.matched_amount,
        "transaction_hash": result.transaction_hash,
        "block_number": result.block_number,
        "timestamp": result.timestamp.isoformat() if result.timestamp else None,
        "confirmations": result.confirmations,
        "sender": result.sender,
        "receiver": result.receiver,
        "token": result.token,
        "chain": result.chain,
        "transfer_count": len(result.transfers),
    }
    console.print(json.dumps(output, indent=2))


def _output_quiet(result) -> None:
    """Output minimal status."""
    console.print(result.status.value)


def _output_rich(result, verbose: bool) -> None:
    """Output rich formatted result."""
    console.print()
    
    # Determine status styling
    status_styles = {
        PaymentStatus.PAID: ("✅ PAYMENT VERIFIED", "green"),
        PaymentStatus.NOT_PAID: ("❌ NOT PAID", "red"),
        PaymentStatus.PARTIAL: ("⚠️ PARTIAL PAYMENT", "yellow"),
        PaymentStatus.PENDING: ("⏳ PENDING CONFIRMATION", "yellow"),
    }
    
    status_text, status_color = status_styles.get(
        result.status, ("❓ UNKNOWN", "dim")
    )
    
    # Build content
    lines = []
    lines.append(f"[bold]Status:[/bold]        {result.status.value}")
    lines.append(
        f"[bold]Amount:[/bold]        {format_amount(result.matched_amount)} {result.token} "
        f"[dim](expected: {format_amount(result.expected_amount)})[/dim]"
    )
    
    if result.sender:
        lines.append(f"[bold]From:[/bold]          {format_address(result.sender)}")
    lines.append(f"[bold]To:[/bold]            {format_address(result.receiver)}")
    
    if result.transaction_hash:
        lines.append(f"[bold]Transaction:[/bold]   {format_address(result.transaction_hash, 10)}")
    
    if result.block_number:
        lines.append(
            f"[bold]Block:[/bold]         {result.block_number} "
            f"[dim]({result.confirmations} confirmations)[/dim]"
        )
    
    if result.timestamp:
        lines.append(f"[bold]Time:[/bold]          {format_timestamp(result.timestamp)}")
    
    # Show chain info
    lines.append(f"[bold]Network:[/bold]       {result.chain.title()}")
    
    content = "\n".join(lines)
    
    console.print(Panel(
        content,
        title=status_text,
        border_style=status_color,
        padding=(1, 2),
    ))
    
    # Verbose: show all transfers
    if verbose and result.transfers:
        console.print("\n[bold]All Matching Transfers:[/bold]")
        table = Table(show_header=True)
        table.add_column("TX Hash", style="dim")
        table.add_column("Amount", justify="right")
        table.add_column("From", style="dim")
        table.add_column("Block", justify="right")
        table.add_column("Confirmations", justify="right")
        
        for transfer in result.transfers:
            conf_style = "green" if transfer.confirmations >= 12 else "yellow"
            table.add_row(
                format_address(transfer.tx_hash, 8),
                format_amount(transfer.amount),
                format_address(transfer.sender),
                str(transfer.block_number),
                f"[{conf_style}]{transfer.confirmations}[/{conf_style}]",
            )
        
        console.print(table)
    
    # Tips for NOT_PAID status
    if result.status == PaymentStatus.NOT_PAID:
        console.print()
        console.print("[dim]Tips:[/dim]")
        console.print("[dim]  • Try expanding the time window with --time-window 7d[/dim]")
        console.print("[dim]  • Verify the wallet address is correct[/dim]")
        console.print("[dim]  • Check if the payment was sent on the correct chain[/dim]")
    
    console.print()


if __name__ == "__main__":
    app()
