# GAP Protocol - AI Agent Runtime

## Available Commands
```bash
uv run gap-cli              # CLI tool for GAP operations
./scripts/start_services.sh  # Start FastAPI service on port 8000
uv sync                      # Install/update dependencies
uv run pytest               # Run test suite
```

## Restrictions
- Never modify files in `.archive/`
- Use `git mv` for all file moves
- Run `uv sync` after `pyproject.toml` changes
- Port 8000 must be available for service

## Environment
- Python 3.11+ required
- UV package manager for dependencies
- See `structure.yaml` for project layout
- See `README.md` for complete documentation