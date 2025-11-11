#!/usr/bin/env python3
"""
TUI Notes Application - A terminal-based notes app inspired by macOS Notes
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import Header, Footer, TextArea, ListView, ListItem, Label, Static, Input, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen


# Data directory setup
DATA_DIR = Path.home() / ".notes_tui"
DATA_DIR.mkdir(exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.json"
AUTH_FILE = DATA_DIR / "auth.json"


class PasswordManager:
    """Handles password authentication"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def password_exists() -> bool:
        """Check if a password has been set"""
        return AUTH_FILE.exists()

    @staticmethod
    def set_password(password: str) -> None:
        """Set the password (first time setup)"""
        password_hash = PasswordManager.hash_password(password)
        with open(AUTH_FILE, 'w') as f:
            json.dump({"password_hash": password_hash, "enabled": True}, f)

    @staticmethod
    def skip_password() -> None:
        """Skip password protection (no password mode)"""
        with open(AUTH_FILE, 'w') as f:
            json.dump({"enabled": False}, f)

    @staticmethod
    def is_password_enabled() -> bool:
        """Check if password protection is enabled"""
        if not AUTH_FILE.exists():
            return False

        with open(AUTH_FILE, 'r') as f:
            data = json.load(f)

        return data.get("enabled", False)

    @staticmethod
    def verify_password(password: str) -> bool:
        """Verify a password against the stored hash"""
        if not AUTH_FILE.exists():
            return False

        with open(AUTH_FILE, 'r') as f:
            data = json.load(f)

        # If password protection is disabled, always return True
        if not data.get("enabled", False):
            return True

        password_hash = PasswordManager.hash_password(password)
        return password_hash == data.get("password_hash")


class NoteData:
    """Handles note data persistence"""

    def __init__(self):
        self.data = self.load()

    def load(self):
        """Load notes from JSON file"""
        if NOTES_FILE.exists():
            with open(NOTES_FILE, 'r') as f:
                return json.load(f)
        return {
            "folders": ["All Notes", "Personal", "Work"],
            "notes": []
        }

    def save(self):
        """Save notes to JSON file"""
        with open(NOTES_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_note(self, title: str, content: str, folder: str):
        """Add a new note"""
        note = {
            "id": len(self.data["notes"]) + 1,
            "title": title or "Untitled Note",
            "content": content,
            "folder": folder,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        self.data["notes"].append(note)
        self.save()
        return note

    def update_note(self, note_id: int, title: str, content: str):
        """Update an existing note"""
        for note in self.data["notes"]:
            if note["id"] == note_id:
                note["title"] = title or "Untitled Note"
                note["content"] = content
                note["modified"] = datetime.now().isoformat()
                self.save()
                return note
        return None

    def delete_note(self, note_id: int):
        """Delete a note"""
        self.data["notes"] = [n for n in self.data["notes"] if n["id"] != note_id]
        self.save()

    def get_notes_by_folder(self, folder: str):
        """Get all notes in a folder"""
        if folder == "All Notes":
            return self.data["notes"]
        return [n for n in self.data["notes"] if n["folder"] == folder]

    def add_folder(self, folder_name: str):
        """Add a new folder"""
        if folder_name and folder_name not in self.data["folders"]:
            self.data["folders"].append(folder_name)
            self.save()
            return True
        return False

    def delete_folder(self, folder_name: str):
        """Delete a folder and move its notes to 'All Notes'"""
        # Can't delete "All Notes" folder
        if folder_name == "All Notes":
            return False

        if folder_name in self.data["folders"]:
            # Move all notes from this folder to "All Notes" (or delete them)
            for note in self.data["notes"]:
                if note["folder"] == folder_name:
                    note["folder"] = "Personal"  # Move to Personal folder

            # Remove the folder
            self.data["folders"].remove(folder_name)
            self.save()
            return True
        return False


class FolderList(ListView):
    """Left panel: Folder list"""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, folders: list[str], **kwargs):
        super().__init__(**kwargs)
        self.folders = folders

    def on_mount(self):
        """Populate folder list when mounted"""
        for folder in self.folders:
            # Use star icon for "All Notes" to distinguish it as the main directory
            icon = "⭐" if folder == "All Notes" else "📁"
            self.append(ListItem(Label(f"{icon} {folder}")))

    def refresh_folders(self, folders: list[str]):
        """Refresh the folder list"""
        self.folders = folders
        self.clear()
        for folder in self.folders:
            # Use star icon for "All Notes" to distinguish it as the main directory
            icon = "⭐" if folder == "All Notes" else "📁"
            self.append(ListItem(Label(f"{icon} {folder}")))


class NoteListItem(ListItem):
    """Custom list item for notes with title and preview"""

    def __init__(self, note: dict, **kwargs):
        super().__init__(**kwargs)
        self.note = note

    def compose(self) -> ComposeResult:
        """Create the note preview"""
        title = self.note["title"]
        preview = self.note["content"][:50].replace("\n", " ")
        modified = datetime.fromisoformat(self.note["modified"]).strftime("%b %d, %Y")

        yield Static(f"[bold]{title}[/bold]")
        yield Static(f"[dim]{modified}[/dim]")
        yield Static(f"[dim]{preview}...[/dim]" if len(self.note["content"]) > 50 else f"[dim]{preview}[/dim]")


class NoteListView(ListView):
    """Middle panel: List of notes"""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    current_folder = reactive("All Notes")

    def __init__(self, note_data: NoteData, **kwargs):
        super().__init__(**kwargs)
        self.note_data = note_data

    def refresh_notes(self, folder: str):
        """Refresh the note list for a given folder"""
        self.current_folder = folder
        self.clear()
        notes = self.note_data.get_notes_by_folder(folder)

        if not notes:
            self.append(ListItem(Label("[dim]No notes in this folder[/dim]")))
        else:
            for note in reversed(notes):  # Most recent first
                self.append(NoteListItem(note))


class NoteEditor(TextArea):
    """Right panel: Note editor"""

    current_note_id: reactive[Optional[int]] = reactive(None)
    MAX_LINE_LENGTH = 80

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_line_numbers = False
        self._wrapping = False  # Flag to prevent infinite loop

    def _check_and_wrap_current_line(self) -> None:
        """Check current line and wrap if it exceeds MAX_LINE_LENGTH"""
        if self._wrapping:
            return

        cursor = self.cursor_location
        current_line_index = cursor[0]

        # Get all lines
        lines = self.text.split('\n')

        if current_line_index >= len(lines):
            return

        current_line = lines[current_line_index]

        # If current line exceeds limit, wrap it
        if len(current_line) > self.MAX_LINE_LENGTH:
            self._wrapping = True

            # Find the last space before MAX_LINE_LENGTH
            wrap_point = current_line.rfind(' ', 0, self.MAX_LINE_LENGTH)

            if wrap_point == -1:
                # No space found, force wrap at MAX_LINE_LENGTH
                wrap_point = self.MAX_LINE_LENGTH

            # Split the line
            first_part = current_line[:wrap_point].rstrip()
            second_part = current_line[wrap_point:].lstrip()

            # Calculate cursor position on new line
            old_cursor_col = cursor[1]
            spaces_stripped = len(current_line[wrap_point:]) - len(second_part)

            # If cursor was after the wrap point, move it to the new line
            if old_cursor_col > len(first_part):
                # Calculate position relative to the wrapped text
                new_cursor_col = old_cursor_col - wrap_point - spaces_stripped
                new_cursor_col = max(0, new_cursor_col)
            else:
                # Cursor stays at end of first line
                new_cursor_col = len(second_part)

            # Replace the current line with wrapped version
            lines[current_line_index] = first_part
            lines.insert(current_line_index + 1, second_part)

            # Update the text
            new_text = '\n'.join(lines)
            self.load_text(new_text)

            # Move cursor to appropriate position on new line
            self.cursor_location = (current_line_index + 1, new_cursor_col)

            self._wrapping = False

    def load_note(self, note: dict):
        """Load a note into the editor"""
        self.current_note_id = note["id"]
        self.load_text(note["content"])

    def clear_editor(self):
        """Clear the editor"""
        self.current_note_id = None
        self.load_text("")


class PasswordScreen(ModalScreen):
    """Modal screen for password entry"""

    CSS = """
    PasswordScreen {
        align: center middle;
    }

    #password-dialog {
        width: 50;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1;
    }

    #warning-label {
        color: $warning;
        margin: 0;
    }

    #password-input {
        margin: 0;
    }

    #password-message {
        color: $text;
        margin: 0;
    }

    #error-message {
        color: $error;
        margin: 0;
        height: 1;
    }

    #button-container {
        height: 1;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, is_first_time: bool = False):
        super().__init__()
        self.error_message = ""

    def compose(self) -> ComposeResult:
        with Container(id="password-dialog"):
            yield Label("🔒 Enter Password", id="password-message")
            yield Input(placeholder="Password", password=True, id="password-input")
            yield Label("", id="error-message")

            with Center(id="button-container"):
                yield Button("Unlock", variant="primary", id="submit-btn")
                yield Button("Exit", variant="default", id="exit-btn")

    def on_mount(self):
        """Focus the input when mounted"""
        self.query_one(Input).focus()

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks"""
        if event.button.id == "submit-btn":
            password = self.query_one(Input).value

            if not password:
                self.query_one("#error-message", Label).update("Password cannot be empty")
                return

            # Verify the password
            if PasswordManager.verify_password(password):
                self.dismiss(True)
            else:
                self.query_one("#error-message", Label).update("❌ Incorrect password")
                self.query_one(Input).value = ""
        else:
            # Exit button pressed
            self.dismiss(False)

    def on_input_submitted(self, event: Input.Submitted):
        """Handle Enter key in input"""
        password = event.value

        if not password:
            self.query_one("#error-message", Label).update("Password cannot be empty")
            return

        if PasswordManager.verify_password(password):
            self.dismiss(True)
        else:
            self.query_one("#error-message", Label).update("❌ Incorrect password")
            self.query_one(Input).value = ""


class FolderInputScreen(ModalScreen):
    """Modal screen for creating a new folder"""

    CSS = """
    FolderInputScreen {
        align: center middle;
    }

    #folder-dialog {
        width: 50;
        height: 11;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #folder-input {
        margin: 1 0;
    }

    #button-container {
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="folder-dialog"):
            yield Label("Enter folder name:")
            yield Input(placeholder="Folder name", id="folder-input")
            with Center(id="button-container"):
                yield Button("Create", variant="primary", id="create-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self):
        """Focus the input when mounted"""
        self.query_one(Input).focus()

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks"""
        if event.button.id == "create-btn":
            folder_name = self.query_one(Input).value.strip()
            self.dismiss(folder_name)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted):
        """Handle Enter key in input"""
        folder_name = event.value.strip()
        self.dismiss(folder_name)


class FolderDeleteConfirmScreen(ModalScreen):
    """Modal screen for confirming folder deletion"""

    CSS = """
    FolderDeleteConfirmScreen {
        align: center middle;
    }

    #delete-dialog {
        width: 60;
        height: 15;
        border: thick $error 80%;
        background: $surface;
        padding: 1 2;
    }

    #warning-message {
        margin: 1 0;
        color: $warning;
    }

    #button-container {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, folder_name: str, note_count: int):
        super().__init__()
        self.folder_name = folder_name
        self.note_count = note_count

    def compose(self) -> ComposeResult:
        with Container(id="delete-dialog"):
            yield Label(f"Delete folder '{self.folder_name}'?")
            if self.note_count > 0:
                yield Label(
                    f"⚠️  This folder contains {self.note_count} note(s)!",
                    id="warning-message"
                )
                yield Label("Notes will be moved to 'Personal' folder.")
            else:
                yield Label("This folder is empty.")
            with Center(id="button-container"):
                yield Button("Delete", variant="error", id="delete-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks"""
        if event.button.id == "delete-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)


class NotesApp(App):
    """Main TUI Notes Application"""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #folders {
        width: 20%;
        min-width: 20;
        max-width: 30;
        border-right: solid $accent;
        padding: 1;
    }

    #note-list {
        width: 30%;
        min-width: 25;
        max-width: 40;
        border-right: solid $accent;
        padding: 1;
    }

    #editor-container {
        width: 1fr;
        padding: 1;
    }

    #editor-placeholder {
        height: 100%;
        align: center middle;
        color: $text-muted;
    }

    #title-input {
        height: 3;
        margin-bottom: 1;
        border: solid $accent;
    }

    NoteEditor {
        height: 1fr;
        width: 100%;
    }

    NoteListItem {
        height: auto;
        padding: 1;
    }

    ListView {
        height: 100%;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $accent 20%;
    }

    ListItem.-selected {
        background: $accent;
    }
    """

    TITLE = "Notes"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+n", "new_note", "New Note"),
        Binding("ctrl+f", "new_folder", "New Folder"),
        Binding("ctrl+s", "save_note", "Save"),
        Binding("ctrl+d", "delete_note", "Delete"),
        Binding("tab", "focus_next", "Next Panel", show=False),
        Binding("shift+tab", "focus_previous", "Previous Panel", show=False),
        Binding("1", "focus_folders", "Folders", show=False),
        Binding("2", "focus_notes", "Notes", show=False),
        Binding("3", "focus_editor", "Editor", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.note_data = NoteData()
        self.current_folder = "All Notes"

    def compose(self) -> ComposeResult:
        """Create the app layout"""
        yield Header()

        with Horizontal():
            # Left panel: Folders
            self.folder_list = FolderList(
                self.note_data.data["folders"],
                id="folders"
            )
            yield self.folder_list

            # Middle panel: Note list
            self.note_list = NoteListView(
                self.note_data,
                id="note-list"
            )
            yield self.note_list

            # Right panel: Editor
            with Vertical(id="editor-container"):
                # Placeholder shown when no note is selected
                with Center(id="editor-placeholder"):
                    yield Label("📝 Select a note or press Ctrl+N to create one")

                # Title and editor (hidden initially)
                self.title_input = Input(placeholder="Note title...", id="title-input")
                self.title_input.display = False
                yield self.title_input

                self.editor = NoteEditor()
                self.editor.display = False
                yield self.editor

        yield Footer()

    def on_mount(self):
        """Initialize the app"""
        # Check if password protection is enabled
        password_enabled = PasswordManager.is_password_enabled()

        def handle_password_result(authenticated: bool):
            if authenticated:
                # Password correct
                self.note_list.refresh_notes(self.current_folder)
                self.folder_list.index = 0
                self.folder_list.focus()
            else:
                # User pressed Exit or authentication failed
                self.exit()

        # Show password screen only if password is enabled
        if password_enabled:
            self.push_screen(PasswordScreen(is_first_time=False), handle_password_result)
        else:
            # No password protection, go straight to app
            self.note_list.refresh_notes(self.current_folder)
            self.folder_list.index = 0
            self.folder_list.focus()

    def show_editor(self):
        """Show the editor and title input, hide placeholder"""
        placeholder = self.query_one("#editor-placeholder")
        placeholder.display = False
        self.title_input.display = True
        self.editor.display = True

    def hide_editor(self):
        """Hide the editor and title input, show placeholder"""
        placeholder = self.query_one("#editor-placeholder")
        placeholder.display = True
        self.title_input.display = False
        self.editor.display = False
        self.editor.clear_editor()
        self.title_input.value = ""

    def on_list_view_selected(self, event: ListView.Selected):
        """Handle selection in folder or note list"""
        if event.list_view.id == "folders":
            # Folder selected
            folder_index = event.list_view.index
            if folder_index is not None:
                self.current_folder = self.note_data.data["folders"][folder_index]
                self.note_list.refresh_notes(self.current_folder)
                self.hide_editor()

        elif event.list_view.id == "note-list":
            # Note selected
            item = event.item
            if isinstance(item, NoteListItem):
                self.show_editor()
                self.editor.load_note(item.note)
                self.title_input.value = item.note["title"]
                self.title_input.focus()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text changes in the editor to auto-wrap long lines"""
        if event.text_area == self.editor:
            self.editor._check_and_wrap_current_line()

    def action_new_note(self):
        """Create a new note"""
        note = self.note_data.add_note(
            title="Untitled Note",
            content="",
            folder=self.current_folder
        )
        self.note_list.refresh_notes(self.current_folder)
        self.show_editor()
        self.editor.load_note(note)
        # Start with empty title field so user can just type
        self.title_input.value = ""
        self.title_input.placeholder = "Enter note title..."
        self.title_input.focus()
        self.notify("New note created")

    def action_new_folder(self):
        """Create a new folder"""
        def check_folder_name(folder_name: str | None):
            if folder_name:
                if self.note_data.add_folder(folder_name):
                    self.folder_list.refresh_folders(self.note_data.data["folders"])
                    self.notify(f"Folder '{folder_name}' created")
                else:
                    self.notify("Folder already exists or invalid name", severity="warning")

        self.push_screen(FolderInputScreen(), check_folder_name)

    def action_save_note(self):
        """Save the current note"""
        if self.editor.current_note_id is not None:
            content = self.editor.text
            # Get title from the title input field
            title = self.title_input.value.strip() or "Untitled Note"

            self.note_data.update_note(
                self.editor.current_note_id,
                title,
                content
            )
            self.note_list.refresh_notes(self.current_folder)
            self.notify("Note saved")
        else:
            self.notify("No note selected", severity="warning")

    def action_delete_note(self):
        """Delete the current note or folder (context-aware)"""
        # Check if folders panel is focused - delete folder
        if self.folder_list.has_focus:
            if self.folder_list.index is not None:
                folder_to_delete = self.note_data.data["folders"][self.folder_list.index]

                # Can't delete "All Notes"
                if folder_to_delete == "All Notes":
                    self.notify("Cannot delete 'All Notes' folder", severity="warning")
                    return

                # Count notes in this folder
                notes_in_folder = self.note_data.get_notes_by_folder(folder_to_delete)
                note_count = len(notes_in_folder)

                # Show confirmation dialog
                def handle_delete_confirmation(confirmed: bool):
                    if confirmed:
                        if self.note_data.delete_folder(folder_to_delete):
                            self.folder_list.refresh_folders(self.note_data.data["folders"])
                            # Switch to "All Notes" if we deleted the current folder
                            if self.current_folder == folder_to_delete:
                                self.current_folder = "All Notes"
                                self.folder_list.index = 0
                                self.note_list.refresh_notes(self.current_folder)
                                self.hide_editor()
                            else:
                                # Refresh the note list in case we were viewing "All Notes"
                                self.note_list.refresh_notes(self.current_folder)
                            self.notify(f"Folder '{folder_to_delete}' deleted")

                self.push_screen(
                    FolderDeleteConfirmScreen(folder_to_delete, note_count),
                    handle_delete_confirmation
                )
            else:
                self.notify("No folder selected", severity="warning")
            return

        # Otherwise, delete a note
        note_to_delete = None

        # First check if a note is loaded in the editor
        if self.editor.current_note_id is not None:
            note_to_delete = self.editor.current_note_id
        # Otherwise, check if a note is highlighted in the note list
        elif self.note_list.index is not None:
            highlighted_item = self.note_list.children[self.note_list.index]
            if isinstance(highlighted_item, NoteListItem):
                note_to_delete = highlighted_item.note["id"]

        if note_to_delete is not None:
            self.note_data.delete_note(note_to_delete)
            self.note_list.refresh_notes(self.current_folder)
            self.hide_editor()
            self.notify("Note deleted")
        else:
            self.notify("No note selected", severity="warning")

    def action_focus_folders(self):
        """Focus the folder list"""
        self.folder_list.focus()

    def action_focus_notes(self):
        """Focus the note list"""
        self.note_list.focus()

    def action_focus_editor(self):
        """Focus the editor"""
        self.editor.focus()


def main():
    """Run the application"""
    app = NotesApp()
    app.run()


if __name__ == "__main__":
    main()
