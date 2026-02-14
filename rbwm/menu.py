"""
Menu abstraction for different menu programs.
"""
import subprocess


MENU_CONFIGS = {
    "dmenu": {
        "cmd": "dmenu -l 10 -i -p '{prompt}'",
        "description": "Classic dmenu (X11)"
    },
    "bemenu": {
        "cmd": "bemenu -l 10 -i -p '{prompt}'",
        "description": "bemenu (Wayland/X11)"
    },
    "wmenu": {
        "cmd": "wmenu -i -p '{prompt}'",
        "description": "wmenu (Wayland)"
    },
    "rofi": {
        "cmd": "rofi -dmenu -i -p '{prompt}'",
        "description": "rofi (X11/Wayland)"
    },
    "fuzzel": {
        "cmd": "fuzzel --dmenu -p '{prompt}'",
        "description": "fuzzel (Wayland)"
    },
    "tofi": {
        "cmd": "tofi --prompt '{prompt}'",
        "description": "tofi (Wayland)"
    },
}


def select_from_menu_raw(menu_cmd, items, prompt="Select"):
    """Show menu using specific menu command without config."""
    cmd_template = MENU_CONFIGS.get(menu_cmd, {}).get("cmd", menu_cmd)
    cmd = cmd_template.format(prompt=prompt)
    
    input_text = "\n".join(items) if items else ""
    result = subprocess.run(
        cmd,
        shell=True,
        input=input_text,
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def select_from_menu(items, prompt="Select"):
    """Show menu with items and return selection."""
    from .config import CONFIG
    
    menu_cmd = CONFIG.get_menu_cmd()
    return select_from_menu_raw(menu_cmd, items, prompt)
