# Contributing to Storage Monitor

Thank you for your interest in contributing to Storage Monitor! This document provides guidelines and information for contributors.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Include detailed steps to reproduce the bug
- Provide your Windows version and Python version
- Include any error messages or logs

### Suggesting Enhancements

- Use the GitHub issue tracker with the "enhancement" label
- Describe the feature and its benefits
- Consider implementation complexity

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the coding standards below
4. **Test your changes** thoroughly
5. **Commit your changes** with clear commit messages
6. **Push to your fork** and create a Pull Request

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/storage-monitor.git
   cd storage-monitor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install black flake8 pytest
   ```

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and reasonably sized

### Code Formatting

Use Black for code formatting:
```bash
black storage_monitor_*.py
```

### Linting

Use flake8 for linting:
```bash
flake8 storage_monitor_*.py
```

## Testing

- Test your changes on Windows 10/11
- Test both console and GUI versions
- Ensure the application doesn't crash with various file system scenarios
- Test with different user permission levels

## Pull Request Guidelines

1. **Clear title** describing the change
2. **Detailed description** of what was changed and why
3. **Screenshots** for UI changes
4. **Test results** showing the changes work as expected
5. **No breaking changes** without discussion

## Areas for Contribution

### High Priority
- Bug fixes and stability improvements
- Performance optimizations
- Better error handling
- Documentation improvements

### Medium Priority
- New features (with discussion first)
- UI/UX improvements
- Additional monitoring capabilities
- Export functionality

### Low Priority
- Code refactoring
- Additional themes
- Minor UI tweaks

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## Getting Help

- Check existing issues and discussions
- Ask questions in GitHub issues
- Be specific about what you need help with

## License

By contributing to Storage Monitor, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Storage Monitor! 🚀 