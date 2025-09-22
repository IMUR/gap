# Contributing to GAP Protocol

Thank you for your interest in contributing to GAP Protocol! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/IMUR/gap/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (if applicable)
   - Expected vs actual behavior
   - System information (Python version, OS, etc.)

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**:
   ```bash
   ./scripts/dev_setup.sh
   ```

4. **Make your changes**:
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

5. **Run quality checks**:
   ```bash
   # Format code
   uv run black .
   uv run ruff check --fix .
   
   # Run tests
   uv run pytest
   
   # Type checking
   uv run mypy src/
   ```

6. **Commit your changes**:
   ```bash
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue with..."
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)

## Development Guidelines

### Code Style

- Python code follows [Black](https://black.readthedocs.io/) formatting
- Use [Ruff](https://github.com/astral-sh/ruff) for linting
- Follow PEP 8 with 100-character line length
- Use type hints for all functions

### Project Structure

See [docs/governance/RULES.md](docs/governance/RULES.md) for project rules and constraints.

### Commit Messages

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

### Testing

- Write tests for all new functionality
- Place tests in `tests/` directory
- Use pytest for testing
- Aim for high test coverage

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions/classes
- Update CLAUDE.md if development process changes
- Keep documentation in `docs/` current

## Architecture Decisions

Before making significant changes, review:
- [docs/governance/DECISIONS.md](docs/governance/DECISIONS.md) - Architectural decisions
- [docs/governance/RULES.md](docs/governance/RULES.md) - Project constraints
- [docs/architecture/](docs/architecture/) - Technical design

## Areas for Contribution

### Priority Areas

1. **Test Coverage** - The `tests/` directory needs implementation
2. **Browser Extension** - Firefox and Safari support
3. **Platform Support** - Add more AI platform transformations
4. **Documentation** - Improve guides and examples

### Good First Issues

Look for issues labeled `good first issue` in our [issue tracker](https://github.com/IMUR/gap/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

## Community

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints

### Getting Help

- Open a [discussion](https://github.com/IMUR/gap/discussions) for questions
- Check existing documentation in `/docs`
- Review [examples](examples/) for usage patterns

## Recognition

Contributors will be acknowledged in:
- GitHub contributors list
- Project README acknowledgments
- Release notes for significant contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to GAP Protocol! 🎉