# Contributing to oNotes

Thank you for your interest in contributing to oNotes!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/onotes.git
cd onotes
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app in development mode:
```bash
python notes.py
```

## Project Structure

- `notes.py` - Main application code
- `setup.py` - Package configuration
- `install.sh` - Installation script
- `uninstall.sh` - Uninstallation script
- `requirements.txt` - Python dependencies
- `README.md` - User documentation

## Making Changes

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Test thoroughly
4. Submit a pull request with a clear description of your changes

## Code Style

- Follow PEP 8 guidelines
- Add comments for complex logic
- Keep functions focused and single-purpose

## Testing

Before submitting:
- Test all keyboard shortcuts
- Verify password protection works (both enabled and disabled)
- Test folder and note creation/deletion
- Ensure text wrapping works correctly
- Test on different terminal sizes

## Reporting Issues

When reporting bugs, please include:
- Your OS and terminal emulator
- Steps to reproduce
- Expected vs actual behavior
- Any error messages or logs
