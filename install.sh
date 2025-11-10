#!/bin/bash
# Installation script for oNotes

echo "Installing oNotes..."
echo "===================="
echo ""

# Check if pipx is available
if ! command -v pipx &> /dev/null; then
    echo "pipx is not installed. Installing pipx..."
    sudo apt update && sudo apt install -y pipx

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install pipx."
        echo ""
        echo "Please install pipx manually:"
        echo "  sudo apt install pipx"
        exit 1
    fi

    # Ensure pipx path is set up
    pipx ensurepath

    # Also manually add to PATH in .bashrc if not already there
    if ! grep -q '.local/bin' ~/.bashrc; then
        echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
    fi

    echo ""
    echo "⚠️  Please run 'source ~/.bashrc' and then run this script again."
    exit 0
fi

# Ensure pipx is in PATH for this session
export PATH="$PATH:$HOME/.local/bin"

# Also add to .bashrc if not already there
if ! grep -q '.local/bin' ~/.bashrc; then
    echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
fi

# Install using pipx
pipx install -e .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ oNotes installed successfully!"
    echo ""

    # Password protection setup
    echo "Password Protection Setup"
    echo "========================="
    echo "⚠️  WARNING: There is NO password recovery!"
    echo "If you forget your password, you'll need to delete ~/.notes_tui/auth.json"
    echo ""
    read -p "Do you want to enable password protection? (y/n): " -n 1 -r
    echo ""

    # Create data directory if it doesn't exist
    mkdir -p ~/.notes_tui

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # User wants password protection
        echo ""
        read -s -p "Enter password: " PASSWORD
        echo ""
        read -s -p "Confirm password: " PASSWORD_CONFIRM
        echo ""

        if [ "$PASSWORD" = "$PASSWORD_CONFIRM" ]; then
            # Hash the password using Python
            PASSWORD_HASH=$(python3 -c "import hashlib; print(hashlib.sha256('$PASSWORD'.encode()).hexdigest())")

            # Create auth.json with password enabled
            echo "{\"password_hash\": \"$PASSWORD_HASH\", \"enabled\": true}" > ~/.notes_tui/auth.json
            echo ""
            echo "✅ Password protection enabled!"
        else
            echo ""
            echo "❌ Passwords don't match. Skipping password protection."
            echo "{\"enabled\": false}" > ~/.notes_tui/auth.json
        fi
    else
        # User skipped password protection
        echo "{\"enabled\": false}" > ~/.notes_tui/auth.json
        echo "✅ Password protection skipped."
    fi

    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "IMPORTANT: To use the 'onotes' command, either:"
    echo "  1. Restart your terminal, OR"
    echo "  2. Run: source ~/.bashrc"
    echo ""
    echo "If you still get 'command not found', run:"
    echo "  export PATH=\"\$PATH:\$HOME/.local/bin\""
    echo ""
    echo "Then try: onotes"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Please check the errors above."
    exit 1
fi
