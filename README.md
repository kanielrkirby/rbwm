# rbwm - Bitwarden Menu

A lightweight menu interface for [rbw](https://github.com/doy/rbw) (unofficial Bitwarden CLI) that works with your favorite menu program (dmenu, bemenu, rofi, wmenu, fuzzel, or tofi).

## Features

- **Quick autofill**: Select a login entry to automatically type username + tab + password + enter
- **Field details**: View and type individual fields from any entry (username, password, custom fields)
- **TOTP support**: Generate and type 2FA codes on demand
- **Secure notes**: Access and type secure note contents
- **Full CRUD operations**: Add, edit, and remove entries directly from the menu
- **Vault management**: Sync with Bitwarden servers and lock/unlock vault
- **Cross-platform**: Works on both X11 and Wayland
- **Smart detection**: Auto-detects available menu programs and display protocols
- **Clipboard restoration**: Temporarily uses clipboard for typing, then restores original contents

## Dependencies

### Required
- **Python 3** (no external Python packages required)
- **[rbw](https://github.com/doy/rbw)** - Unofficial Bitwarden CLI client
- **At least one menu program**:
  - X11: `dmenu`, `rofi`, or `bemenu`
  - Wayland: `bemenu`, `wmenu`, `fuzzel`, `tofi`, or `rofi`
- **Clipboard & input tools**:
  - X11: `xclip` or `xsel`, plus `xdotool`
  - Wayland: `wl-clipboard` and `wtype`

### Optional
- **pinentry program** for password prompts: `pinentry-dmenu`, `pinentry-curses`, `pinentry-gnome3`, `pinentry-qt`, or `pinentry`

## Installation

### Nix Flakes

```bash
# Run directly
nix run github:kanielrkirby/rbwm

# Install to profile
nix profile install github:kanielrkirby/rbwm
```

### Manual

```bash
# Clone the repository
git clone https://github.com/kanielrkirby/rbwm
cd rbwm

# Run directly as Python module
python3 -m rbwm

# Or install to PATH
mkdir -p ~/.local/bin
cat > ~/.local/bin/rbwm << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add rbwm module to path
rbwm_path = os.path.expanduser("~/path/to/rbwm")
sys.path.insert(0, rbwm_path)

from rbwm.__main__ import main
main()
EOF
chmod +x ~/.local/bin/rbwm
```

## Configuration

On first run, rbwm launches a configuration wizard (GUI or CLI depending on your environment) to select:

- **Menu program**: Choose from dmenu, bemenu, rofi, wmenu, fuzzel, tofi, or set to "auto" for automatic detection
- **Pinentry program**: Select which pinentry to use for vault unlock prompts

Configuration is saved to `~/.config/rbwm/config`. You can:
- Edit the file manually
- Re-run the wizard: `rbwm setup`
- Delete the config file to trigger wizard on next run

**Smart fallback**: If your configured menu program is unavailable, rbwm will automatically detect and use an alternative (Wayland-aware) while notifying you once per session.

## Usage

Run `rbwm` to open the menu interface.

### Main Menu Options

- **Login entries**: Select any login to autofill username + tab + password + enter
- **[Details]**: Browse and type individual fields from login entries (passwords, usernames, TOTP codes, custom fields)
- **[Notes]**: Access and type secure note contents
- **[Sync]**: Sync vault with Bitwarden servers
- **[Add]**: Create a new vault entry with interactive field-by-field input
- **[Edit]**: Modify existing entries by selecting fields to update
- **[Remove]**: Delete an entry from the vault
- **[Lock]**: Lock the vault

### Auto-Unlock

If the vault is locked, rbwm will automatically prompt for your master password using the configured pinentry program.

### Keybinding Example

Bind rbwm to a hotkey in your window manager or compositor. For example with sxhkd:

```
super + p
    rbwm
```

Or with Hyprland:

```
bind = SUPER, P, exec, rbwm
```

## How It Works

1. **Queries rbw** for vault entries via `rbw list --raw`
2. **Presents menu** using your configured menu program
3. **Types credentials** by temporarily copying to clipboard and simulating Shift+Insert
4. **Restores clipboard** to previous contents immediately after typing

The clipboard restoration ensures your original clipboard contents are preserved, and credentials never remain in clipboard history.

## Architecture

- **`__main__.py`**: Entry point and main menu logic
- **`vault.py`**: All rbw interactions (unlock, list, get entries, TOTP generation)
- **`menu.py`**: Menu program abstraction with unified interface
- **`inject.py`**: Text injection via clipboard + keyboard simulation (X11/Wayland)
- **`config.py`**: Configuration management with wizard and smart fallback
- **`system.py`**: System utilities (command detection, notifications)

## Security

- **No persistent clipboard storage**: Credentials are typed via temporary clipboard copy with immediate restoration
- **No logging**: Passwords and sensitive data are never logged or written to disk by rbwm
- **Vault unlock required**: All operations require rbw vault to be unlocked
- **Uses rbw security model**: Inherits rbw's encryption and security guarantees

## Troubleshooting

**"No menu program found"**: Install at least one supported menu program (dmenu, bemenu, rofi, wmenu, fuzzel, or tofi).

**"No pinentry program found"**: Install a pinentry variant. `pinentry-curses` works universally but `pinentry-dmenu` provides a better menu-integrated experience.

**Vault won't unlock**: Ensure rbw is properly configured (`rbw config`) and you can manually unlock with `rbw unlock`.

**Text not typing correctly**: Verify clipboard and input tools are installed:
- X11: `xclip` or `xsel`, plus `xdotool`
- Wayland: `wl-clipboard` and `wtype`

## License

MIT

## Credits

Built for use with [rbw](https://github.com/doy/rbw) by doy.
