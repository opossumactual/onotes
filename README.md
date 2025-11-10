# oNotes

A terminal-based notes application inspired by macOS Notes, built with Python and Textual.

Run with: `onotes`

## Features

- **Password Protection**: 🔒 Optional password security
  - Configure during installation: Choose to set a password or skip it
  - ⚠️ **NO PASSWORD RECOVERY** - You must remember it!
  - Password is hashed using SHA-256 and stored securely
  - Can skip password for easier access
- **Three-panel layout**: Folders, note list, and editor
- **Responsive design**: Layout adjusts automatically to terminal window size
- **Auto-wrapping**: Text automatically wraps at 80 characters per line (at word boundaries)
- **Separate title field**: Edit note titles independently from content
- **Folder organization**: Organize notes into folders, create custom folders
  - "All Notes" ⭐ shows all notes regardless of folder
  - Regular folders 📁 show only their specific notes
- **Auto-save**: Notes are automatically saved to `~/.notes_tui/notes.json`
- **Keyboard navigation**: Vim-style keybindings and shortcuts
- **Smart delete**: Delete notes from either the note list or editor

## Installation

### Option 1: Install as Command (Recommended)

Install oNotes so you can run it from anywhere with the `onotes` command.

The installer will automatically install `pipx` if needed:

```bash
git clone https://github.com/yourusername/onotes.git
cd onotes
chmod +x install.sh
bash install.sh
```

**Note:** If you get permission errors, use `bash install.sh` instead of `./install.sh`

If pipx was just installed, you'll need to restart your terminal or run:
```bash
source ~/.bashrc
```

Then run the installer again. After installation, you can run:
```bash
onotes
```

### Option 2: Run from Directory (No Installation)

If you want to run without installing or just want to try it out:

```bash
git clone https://github.com/yourusername/onotes.git
cd onotes
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python notes.py
```

**Quick run after setup:**
```bash
cd onotes
source venv/bin/activate
python notes.py
```

### Uninstalling

To remove oNotes:
```bash
cd onotes
bash uninstall.sh
```

Or manually:
```bash
pipx uninstall onotes
```

Your notes data will remain in `~/.notes_tui/` unless you manually delete it.

## Troubleshooting

### "Command not found" after installation

If you get `onotes: command not found` after installing:

**Quick Fix:**
```bash
export PATH="$PATH:$HOME/.local/bin"
onotes
```

**Permanent Fix:**
```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
onotes
```

Or simply restart your terminal.

### Permission Denied Errors

If you get "Permission denied" errors:
1. Use `bash scriptname.sh` instead of `./scriptname.sh`
2. Example: `bash install.sh` instead of `./install.sh`

### Can't Execute Scripts

If chmod doesn't work or you can't execute scripts:
```bash
# Instead of ./install.sh, use:
bash install.sh

# Instead of ./run.sh, use:
python3 notes.py
```

## Keyboard Shortcuts

### General
- `Ctrl+Q` - Quit the application
- `Ctrl+N` - Create a new note in the current folder
- `Ctrl+F` - Create a new folder
- `Ctrl+S` - Save the current note
- `Ctrl+D` - Delete the highlighted/selected note OR folder (context-aware)
- `Tab` / `Shift+Tab` - Switch between panels

### Quick Focus
- `1` - Jump to folders panel
- `2` - Jump to notes list panel
- `3` - Jump to editor panel

### Navigation (in lists)
- `↑` / `↓` or `j` / `k` - Move up/down
- `Enter` - Select folder or note

## How to Use

1. **Installation**: During installation, you'll be asked about password protection
   - **⚠️ WARNING: Password recovery is NOT possible!**
   - **Option 1 - Enable Password**: Set a password during install
     - Password will be required every time you open the app
     - You MUST remember it - there's no way to recover it
   - **Option 2 - Skip Password**: Choose 'n' when prompted
     - App will open immediately without asking for password
     - Choose this for convenience over security
2. **Getting Started**: When you launch `onotes`, you'll see a placeholder in the editor area
   - The editor is hidden until you select or create a note
   - This prevents accidentally typing into nowhere
3. **Select a folder**: Navigate the left panel and press Enter
4. **Create a folder**: Press `Ctrl+F` to create a new custom folder
5. **Delete a folder**: Navigate to the folders panel (press `1`), highlight a folder, and press `Ctrl+D`
   - A confirmation dialog will appear showing how many notes are in the folder
   - Notes in the deleted folder will be moved to the "Personal" folder (they won't be lost)
   - These notes will still appear in "All Notes" view (which shows all notes regardless of folder)
   - You cannot delete the "All Notes" folder
6. **Create a note**: Press `Ctrl+N` to create a new note in the current folder
   - The editor will appear when you create or select a note
7. **Edit a note**: Select a note from the middle panel
   - The title field at the top shows the note's title (you can edit it)
   - The editor below shows the note's content
8. **Save your changes**: Press `Ctrl+S` to save both title and content
9. **Delete a note**: Highlight a note in the list (or open it) and press `Ctrl+D`

## Data Storage

Notes are stored in: `~/.notes_tui/notes.json`
Password settings are stored in: `~/.notes_tui/auth.json`

**Security Note**:
- If you set a password, it's hashed using SHA-256 before storage
- The actual password is never saved, only the hash
- If you skipped password, auth.json contains `{"enabled": false}`
- Deleting auth.json resets password settings (run install script again to reconfigure)

## Tips

- **Password Management**:
  - ⚠️ **CRITICAL**: There is NO password recovery mechanism!
  - If you forget your password, you must delete `~/.notes_tui/auth.json` to reset
  - After deleting auth.json, run the install script again to set up password protection (or skip it)
  - To change password settings, delete `~/.notes_tui/auth.json` and reinstall
- The editor only appears when you select or create a note - this prevents accidentally typing into an empty void
- Give your notes descriptive titles using the title field at the top of the editor
- Navigate quickly using number keys (1, 2, 3) to jump between panels
- Press `Tab` to move between the title field and editor
- Vim users will feel at home with `j`/`k` navigation in lists
- `Ctrl+D` is context-aware: it deletes folders when focused on the folders panel, and notes when focused elsewhere
- Resize your terminal window at any time - the layout will adjust automatically
- Text automatically wraps at 80 characters per line, breaking at word boundaries
- You can still manually press Enter to create line breaks whenever you want
- When creating a new note, the title field starts empty with a placeholder - just start typing
- If you save without entering a title, it defaults to "Untitled Note"

## License

MIT License - feel free to use and modify as needed!
