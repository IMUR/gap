# Release Process

## Version Numbering

GAP Protocol follows [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 0.1.0)
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality additions
- PATCH: Backwards-compatible bug fixes

Current version: **0.1.0** (Initial Release)

## Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] Code formatted (`uv run black .`)
- [ ] Linting clean (`uv run ruff check .`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Browser extension version updated in `manifest.json`

### Release Steps

1. **Update Version**:
   ```bash
   # Update version in pyproject.toml
   # Update version in extensions/chrome/manifest.json
   ```

2. **Create Release Branch**:
   ```bash
   git checkout -b release/v0.1.0
   ```

3. **Run Final Checks**:
   ```bash
   uv run black .
   uv run ruff check --fix .
   uv run pytest
   ```

4. **Build Artifacts**:
   ```bash
   # Build browser extension
   cd extensions
   ./build.sh chrome
   ```

5. **Commit Changes**:
   ```bash
   git add .
   git commit -m "chore: prepare release v0.1.0"
   ```

6. **Create Tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   ```

7. **Push to GitHub**:
   ```bash
   git push origin release/v0.1.0
   git push origin v0.1.0
   ```

8. **Create GitHub Release**:
   - Go to GitHub releases page
   - Click "Create new release"
   - Select tag v0.1.0
   - Title: "GAP Protocol v0.1.0"
   - Attach `build/gap-chrome-extension.zip`
   - Generate release notes
   - Publish release

### Post-Release

- [ ] Merge release branch to main
- [ ] Update development branch
- [ ] Announce release (if applicable)
- [ ] Close related issues/PRs

## Release Notes Template

```markdown
## GAP Protocol v0.1.0

### 🎉 Features
- Core GAP Protocol implementation
- FastAPI web service
- CLI tool with clipboard support
- Chrome browser extension
- ZED IDE integration
- UV package management

### 🐛 Bug Fixes
- (List any bug fixes)

### 📚 Documentation
- Complete README with examples
- API documentation
- Extension usage guide
- Contributing guidelines

### 🔧 Technical
- Python 3.11+ support
- Modular architecture
- Platform transformations for major AI services

### 📦 Installation

```bash
git clone https://github.com/yourusername/gap-protocol.git
cd gap-protocol
./scripts/install.sh
```

### 🙏 Acknowledgments
- Thanks to all contributors
- Special thanks to AI assistants who helped build this
```

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | TBD | Initial release with core functionality |

## Future Releases

### v0.2.0 (Planned)
- [ ] Firefox browser extension
- [ ] Test suite implementation
- [ ] Cloud service support
- [ ] Entity management UI

### v0.3.0 (Planned)
- [ ] Safari extension
- [ ] Mobile support
- [ ] Advanced context graphs
- [ ] Multi-language support