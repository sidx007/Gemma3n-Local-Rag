# Contributing to Offline RAG Assistant

Thank you for your interest in contributing to the Offline RAG Assistant! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template if available
3. Provide detailed information:
   - OS and Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs

### Submitting Pull Requests

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Make** your changes
4. **Test** your changes thoroughly
5. **Commit** with clear messages: `git commit -m "Add: description of changes"`
6. **Push** to your fork: `git push origin feature/your-feature-name`
7. **Submit** a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/offline-rag-assistant.git
cd offline-rag-assistant

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if available)
pip install -r requirements-dev.txt
```

## 📋 Code Standards

### Python Code Style
- Follow PEP 8
- Use descriptive variable names
- Add docstrings for functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### JavaScript Code Style
- Use const/let instead of var
- Use semicolons consistently
- Use meaningful variable names
- Follow ES6+ standards
- Add comments for complex logic

### Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Use imperative mood: "Fix bug" not "Fixes bug"
- Limit first line to 50 characters
- Reference issues: "Fix #123: resolve login error"

## 🧪 Testing

- Test your changes locally before submitting
- Ensure the RAG system works with sample PDFs
- Test both frontend and backend functionality
- Check for memory leaks with large documents

## 📖 Documentation

- Update README.md if you add new features
- Add docstrings to new functions
- Update API documentation for new endpoints
- Include usage examples

## 🚀 Feature Requests

- Open an issue with the "enhancement" label
- Describe the problem you're trying to solve
- Explain your proposed solution
- Consider implementation complexity

## ❓ Questions

- Check existing documentation first
- Search closed issues
- Open a discussion for general questions
- Tag maintainers for urgent issues

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- GitHub contributors section

Thank you for helping make this project better! 🎉
