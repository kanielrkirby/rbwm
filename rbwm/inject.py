"""Text injection via clipboard and keyboard simulation."""
import subprocess
import os


def type_text(text):
    """Type text by copying to clipboard and pasting."""
    wayland = os.environ.get("WAYLAND_DISPLAY")
    if wayland:
        original = subprocess.run(["wl-paste", "--primary"], capture_output=True, text=True).stdout
        subprocess.run(["wl-copy", "--primary"], input=text, text=True)
        subprocess.run(["wtype", "-M", "shift", "-k", "Insert", "-m", "shift"])
        subprocess.run(["wl-copy", "--primary"], input=original, text=True)
    else:
        has_xclip = subprocess.run(["which", "xclip"], capture_output=True).returncode == 0
        if has_xclip:
            original_primary = subprocess.run(["xclip", "-selection", "primary", "-o"], capture_output=True, text=True).stdout
            original_clipboard = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True).stdout
            subprocess.run(["xclip", "-selection", "primary"], input=text, text=True)
            subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True)
            subprocess.run(["xdotool", "key", "shift+Insert"])
            subprocess.run(["xclip", "-selection", "primary"], input=original_primary, text=True)
            subprocess.run(["xclip", "-selection", "clipboard"], input=original_clipboard, text=True)
        else:
            original_primary = subprocess.run(["xsel", "-p", "-o"], capture_output=True, text=True).stdout
            original_clipboard = subprocess.run(["xsel", "-b", "-o"], capture_output=True, text=True).stdout
            subprocess.run(["xsel", "-p", "-i"], input=text, text=True)
            subprocess.run(["xsel", "-b", "-i"], input=text, text=True)
            subprocess.run(["xdotool", "key", "shift+Insert"])
            subprocess.run(["xsel", "-p", "-i"], input=original_primary, text=True)
            subprocess.run(["xsel", "-b", "-i"], input=original_clipboard, text=True)


def press_tab():
    """Press Tab key."""
    wayland = os.environ.get("WAYLAND_DISPLAY")
    if wayland:
        subprocess.run(["wtype", "-k", "Tab"])
    else:
        subprocess.run(["xdotool", "key", "Tab"])


def press_enter():
    """Press Enter key."""
    wayland = os.environ.get("WAYLAND_DISPLAY")
    if wayland:
        subprocess.run(["wtype", "-k", "Return"])
    else:
        subprocess.run(["xdotool", "key", "Return"])
