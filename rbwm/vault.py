"""Bitwarden vault operations via rbw."""
import subprocess
import json


def is_unlocked() -> bool:
    """Check if vault is unlocked."""
    return subprocess.run(["rbw", "unlocked"], capture_output=True).returncode == 0


def unlock() -> bool:
    """Unlock vault using configured pinentry."""
    from .config import CONFIG
    import os
    
    # Get pinentry and set in environment for rbw to use
    pinentry_cmd = CONFIG.get_pinentry_cmd()
    env = os.environ.copy()
    env["PINENTRY_PROGRAM"] = pinentry_cmd
    
    result = subprocess.run(["rbw", "unlock"], env=env)
    return result.returncode == 0


def ensure_unlocked() -> bool:
    """Ensure vault is unlocked, prompting if needed."""
    if is_unlocked():
        return True
    return unlock()


def lock():
    """Lock the vault."""
    subprocess.run(["rbw", "lock"], capture_output=True)


def sync():
    """Sync with Bitwarden servers."""
    subprocess.run(["rbw", "sync"], capture_output=True)


def get_entries():
    """Get all vault entries."""
    result = subprocess.run(["rbw", "list", "--raw"], capture_output=True, text=True)
    output = result.stdout.strip()
    all_entries = json.loads(output) if output else []
    
    entries = []
    for item in all_entries:
        name = item.get("name", "")
        user = item.get("user", "")
        folder = item.get("folder", "")
        entry_type = item.get("type", "")
        display = name
        if user:
            display += f" ({user})"
        if folder:
            display += f" [{folder}]"
        entries.append({
            "display": display,
            "name": name,
            "user": user,
            "folder": folder,
            "type": entry_type
        })
    return entries


def get_entry_data(name):
    """Get full data for an entry."""
    result = subprocess.run(
        ["rbw", "get", "--raw", name],
        capture_output=True,
        text=True
    )
    output = result.stdout.strip()
    if not output:
        return {}
    try:
        return json.loads(output)
    except Exception:
        return {}


def get_entry_fields(entry_name):
    """Get displayable fields for an entry."""
    data = get_entry_data(entry_name)
    entry_data = data.get("data", {})
    if not entry_data:
        return []
    
    fields = []
    
    for key, value in entry_data.items():
        if value is None or value == "" or value == []:
            continue
        
        if key == "password":
            fields.append({"display": "password", "value": value})
        
        elif key == "totp":
            result = subprocess.run(
                ["rbw", "code", entry_name],
                capture_output=True,
                text=True
            )
            totp = result.stdout.strip()
            if totp:
                fields.append({"display": "totp", "value": totp})
        
        elif isinstance(value, str):
            display = f"{key}: {value[:50]}..." if len(value) > 50 else f"{key}: {value}"
            fields.append({"display": display, "value": value})
    
    return fields
