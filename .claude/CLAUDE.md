# Dutch Taker Bot

A Silverback bot that automatically takes (executes) flex dutch auctions on the blockchain.

## Tech Stack

- **Framework**: [Silverback SDK](https://docs.apeworx.io/silverback/stable)
- **Blockchain**: [Ape Framework](https://docs.apeworx.io/ape/stable)
- **Python**: 3.12+
- **Package Manager**: uv

## Project Structure

```
dutch-taker/
├── bot/
│   ├── __init__.py
│   ├── bot.py           # Main bot logic
│   ├── config.py        # Network config, addresses
│   └── tg.py            # Telegram notifications
├── .claude/
│   ├── CLAUDE.md
│   └── skills/
├── pyproject.toml
└── README.md
```

## Development Guidelines

### Principles

- **DRY** - Don't Repeat Yourself
- **KISS** - Keep It Simple, Stupid
- **Clean Code** - Self-documenting, minimal comments
- **Single Responsibility** - Each function does one thing well
- **Fail Fast** - Validate early, raise exceptions clearly

### Code Style

- Super clean and minimalistic
- Format: `ruff format .`
- Lint: `ruff check .`
- Type check: `mypy bot`
- Line length: 120 characters
- No unnecessary abstractions
- No premature optimization

### Risk Management

- Never hardcode secrets - use environment variables
- Implement configurable limits
- Use `CircuitBreaker` for emergency stops
- Test with print debugging before enabling transactions

## Running

```bash
silverback run --network ethereum:mainnet
```
