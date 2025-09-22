# GAP Protocol - Project Rules

These are non-negotiable constraints that must be followed in the GAP Protocol project.

## File Management Rules

### R1: Archive Preservation
- **Rule**: Files in `.archive/` are READ-ONLY
- **Reason**: Historical preservation and attribution
- **Enforcement**: Never modify, only add new archives

### R2: File Movement
- **Rule**: Always use `git mv` for moving files
- **Reason**: Preserves git history and attribution
- **Enforcement**: No copy-delete operations

### R3: Configuration Files
- **Rule**: `pyproject.toml` and `.python-version` must remain at root
- **Reason**: UV package manager requirement
- **Enforcement**: These files control the Python environment

## Code Rules

### R4: Import Style
- **Rule**: Use absolute imports from `src/` 
- **Example**: `from src.gap import GAPProtocol`
- **Reason**: Clarity and consistency
- **Enforcement**: No relative imports between packages

### R5: Python Version
- **Rule**: Maintain Python 3.11+ compatibility
- **Reason**: Modern features and UV support
- **Enforcement**: Test with Python 3.11 minimum

## Service Rules

### R6: Port Allocation
- **Rule**: FastAPI service MUST use port 8000
- **Reason**: Documentation and integration consistency
- **Enforcement**: Hardcoded in service and docs

### R7: API Compatibility
- **Rule**: REST API endpoints cannot be removed or changed
- **Reason**: External integrations depend on them
- **Enforcement**: Only additions allowed, use versioning for changes

## Documentation Rules

### R8: Single Source of Truth
- **Rule**: Information exists in exactly ONE location
- **Reason**: Prevents contradictions and maintenance burden
- **Enforcement**: Use references, not duplication

### R9: AGENTS.md Size
- **Rule**: AGENTS.md must be under 30 lines
- **Reason**: Token efficiency for AI consumption
- **Enforcement**: Move details to README.md

## Development Rules

### R10: Dependency Management
- **Rule**: All dependencies through UV and pyproject.toml
- **Reason**: Reproducible builds
- **Enforcement**: No manual pip installs

### R11: Test Before Archive
- **Rule**: Ensure functionality works before archiving old versions
- **Reason**: Maintain working state
- **Enforcement**: Run tests before major changes

## Security Rules

### R12: No Secrets
- **Rule**: Never commit API keys, passwords, or tokens
- **Reason**: Security
- **Enforcement**: Use environment variables

## Modification of Rules

These rules can only be modified through:
1. Documentation of the compelling reason
2. Impact assessment
3. Migration plan if needed
4. Update of all affected documentation

Date Established: January 2024
Last Updated: January 2024