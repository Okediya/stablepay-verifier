"""Tests for CLI interface."""

from typer.testing import CliRunner

from stablepay_verifier.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""
    
    def test_version(self) -> None:
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "StablePay Verifier" in result.stdout
    
    def test_help(self) -> None:
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "verify" in result.stdout.lower()
    
    def test_info_command(self) -> None:
        """Test info command."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Polygon" in result.stdout
        assert "USDC" in result.stdout
    
    def test_verify_missing_address(self) -> None:
        """Test verify without address."""
        result = runner.invoke(app, ["verify", "--amount", "100"])
        assert result.exit_code != 0
    
    def test_verify_missing_amount(self) -> None:
        """Test verify without amount."""
        result = runner.invoke(app, [
            "verify",
            "--address", "0x742d35cc6634c0532925a3b844bc9e7595f3a382",
        ])
        assert result.exit_code != 0
    
    def test_verify_invalid_address(self) -> None:
        """Test verify with invalid address."""
        result = runner.invoke(app, [
            "verify",
            "--address", "invalid",
            "--amount", "100",
        ])
        assert result.exit_code == 10  # EXIT_ERROR
        assert "invalid" in result.stdout.lower() or "error" in result.stdout.lower()
