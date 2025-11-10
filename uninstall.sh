#!/bin/bash
# Uninstallation script for oNotes

echo "Uninstalling oNotes..."
echo "====================="
echo ""

# Try pipx first (recommended method)
if command -v pipx &> /dev/null; then
    pipx uninstall onotes
else
    # Fallback to pip if pipx not available
    pip3 uninstall -y onotes
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ oNotes uninstalled successfully!"
    echo ""
    echo "Your notes data is still stored in: ~/.notes_tui/"
    echo "To remove your data, run: rm -rf ~/.notes_tui/"
    echo ""
else
    echo ""
    echo "❌ Uninstallation failed or oNotes was not installed."
    exit 1
fi
