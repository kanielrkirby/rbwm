#!/usr/bin/env python3
"""
rbwm - Bitwarden menu
Main entry point
"""
import sys
from .config import CONFIG, ConfigError
from .system import System
from .menu import select_from_menu, prompt_for_input
from .vault import (
    ensure_unlocked, lock, sync, get_entries, get_entry_fields,
    add_entry, edit_entry, remove_entry
)
from .inject import type_text, press_tab, press_enter


def select_entry(entries, prompt="Select entry"):
    """Helper to select an entry from a list."""
    if not entries:
        return None
    choice = select_from_menu([e["display"] for e in entries], prompt)
    return next((e for e in entries if e["display"] == choice), None) if choice else None


def action_details(entries):
    """Handle [Details] menu choice."""
    login_entries = [e for e in entries if e.get("type") != "Note"]
    
    entry = select_entry(login_entries)
    if not entry:
        return
    
    fields = get_entry_fields(entry["name"])
    if not fields:
        return
    
    field_choice = select_from_menu([f["display"] for f in fields], "Select field")
    if not field_choice:
        return
    
    field = next((f for f in fields if f["display"] == field_choice), None)
    if field:
        type_text(field["value"])


def action_notes(entries):
    """Handle [Notes] menu choice."""
    from .vault import get_entry_data
    
    note_entries = [e for e in entries if e.get("type") == "Note"]
    entry = select_entry(note_entries, "Select note")
    
    if entry:
        data = get_entry_data(entry["name"])
        notes = data.get("notes", "")
        if notes:
            type_text(notes)


def action_sync():
    """Handle [Sync] menu choice."""
    sync()


def action_lock():
    """Handle [Lock] menu choice."""
    lock()


def action_add():
    """Handle [Add] menu choice."""
    from .password import password_menu
    
    new_entry = {"name": "", "username": "", "password": "", "uri": "", "folder": "", "notes": ""}
    
    while True:
        fields = []
        for k, v in new_entry.items():
            if k == "password" and v:
                fields.append(f"{k}: {'*' * len(v)}")
            else:
                fields.append(f"{k}: {v if v else '(empty)'}")
        fields.append("[Save]")
        fields.append("[Discard]")
        
        field_choice = select_from_menu(fields, "Add Entry - Select field to edit")
        if not field_choice or field_choice == "[Discard]":
            return
        
        if field_choice == "[Save]":
            if not new_entry["name"]:
                continue  # Need at least a name
            add_entry(
                new_entry["name"],
                new_entry["username"],
                new_entry["password"],
                new_entry["uri"],
                new_entry["folder"],
                new_entry["notes"]
            )
            return
        
        field_name = field_choice.split(":")[0].strip()
        
        # Use password menu for password field
        if field_name == "password":
            value = password_menu()
        else:
            value = prompt_for_input(f"Enter {field_name}")
        
        if value is not None:
            new_entry[field_name] = value


def action_edit(entries):
    """Handle [Edit] menu choice."""
    from .vault import get_entry_data
    from .password import password_menu
    
    login_entries = [e for e in entries if e.get("type") != "Note"]
    entry = select_entry(login_entries, "Select entry to edit")
    if not entry:
        return
    
    # Get current data
    data = get_entry_data(entry["name"])
    entry_data = data.get("data", {}) or {}
    edit_fields = {
        "username": entry_data.get("username") or "",
        "password": entry_data.get("password") or "",
        "uri": entry_data.get("uris", [{}])[0].get("uri", "") if entry_data.get("uris") else "",
        "folder": data.get("folder") or "",
        "notes": data.get("notes") or ""
    }
    
    while True:
        fields = []
        for k, v in edit_fields.items():
            if k == "password" and v:
                fields.append(f"{k}: {'*' * len(v)}")
            else:
                fields.append(f"{k}: {v if v else '(empty)'}")
        fields.append("[Save]")
        fields.append("[Discard]")
        
        field_choice = select_from_menu(fields, f"Edit {entry['name']} - Select field")
        if not field_choice or field_choice == "[Discard]":
            return
        
        if field_choice == "[Save]":
            edit_entry(
                entry["name"],
                edit_fields["username"],
                edit_fields["password"],
                edit_fields["uri"],
                edit_fields["folder"],
                edit_fields["notes"]
            )
            return
        
        field_name = field_choice.split(":")[0].strip()
        
        # Use password menu for password field
        if field_name == "password":
            value = password_menu()
        else:
            current = edit_fields.get(field_name, "")
            prompt_text = f"Enter {field_name}"
            if current and len(current) <= 30:
                prompt_text += f" (current: {current})"
            elif current:
                prompt_text += f" (current: {current[:30]}...)"
            
            value = prompt_for_input(prompt_text)
        
        if value is not None and value != "":
            edit_fields[field_name] = value


def action_remove(entries):
    """Handle [Remove] menu choice."""
    login_entries = [e for e in entries if e.get("type") != "Note"]
    entry = select_entry(login_entries, "Select entry to remove")
    if entry:
        remove_entry(entry["name"])


def action_autofill(entries, choice):
    """Handle direct entry selection for autofill."""
    from .vault import get_entry_data
    
    login_entries = [e for e in entries if e.get("type") != "Note"]
    entry = next((e for e in login_entries if e["display"] == choice), None)
    if not entry:
        return
    
    data = get_entry_data(entry["name"])
    entry_data = data.get("data", {}) or {}
    username = entry_data.get("username") or ""
    password = entry_data.get("password") or ""
    
    if username and password:
        type_text(username)
        press_tab()
        type_text(password)
        press_enter()
    elif username:
        type_text(username)
    elif password:
        type_text(password)


def main():
    # Handle setup command
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        CONFIG._setup_cli()
        return
    
    try:
        CONFIG.load()
        
        if not ensure_unlocked():
            return
        
        entries = get_entries()
        login_entries = [e for e in entries if e.get("type") != "Note"]
        
        MENU_ACTIONS = {
            "[Details]": lambda: action_details(entries),
            "[Notes]": lambda: action_notes(entries),
            "[Sync]": action_sync,
            "[Add]": action_add,
            "[Edit]": lambda: action_edit(entries),
            "[Remove]": lambda: action_remove(entries),
            "[Lock]": action_lock,
        }
        
        menu_items = list(MENU_ACTIONS.keys()) + [e["display"] for e in login_entries]
        choice = select_from_menu(menu_items, "Bitwarden")
        
        if not choice:
            return
        
        if choice in MENU_ACTIONS:
            MENU_ACTIONS[choice]()
        else:
            action_autofill(entries, choice)
    
    except ConfigError as e:
        System.notify(str(e))


if __name__ == "__main__":
    main()
