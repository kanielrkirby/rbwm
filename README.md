# rbwm - Bitwarden Menu

A simple dmenu/bemenu interface for [rbw](https://github.com/doy/rbw) (unofficial Bitwarden CLI).

## Features

- **Quick autofill**: Select an entry to automatically type username + tab + password + enter
- **Field selection**: View and type individual fields from entries
- **TOTP support**: Generate and type 2FA codes
- **Full CRUD**: Add, edit, remove entries directly from the menu
- **Notes support**: Store and retrieve secure notes
- **Sync**: Sync with Bitwarden servers
- **Lock/Unlock**: Manage vault lock state
- **Cross-platform clipboard**: Works with both X11 (xclip/xsel) and Wayland (wl-clipboard)

## Dependencies

### Required
- Python 3
- [rbw](https://github.com/doy/rbw) - Bitwarden CLI client
- **For X11**:
  - `dmenu`
  - `xclip` or `xsel`
  - `xdotool`
- **For Wayland**:
  - `bemenu`
  - `wl-clipboard`
  - `wtype`

### Optional
- Any pinentry program for password prompts (configured on first run)

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

# Run directly
python3 -m rbwm

# Or symlink to your PATH
echo '#!/usr/bin/env bash' > ~/.local/bin/rbwm
echo 'exec python3 -m rbwm "$@"' >> ~/.local/bin/rbwm
chmod +x ~/.local/bin/rbwm
```

## Configuration

On first run, rbwm will guide you through a configuration wizard to select:
- **Menu program**: dmenu, bemenu, rofi, wmenu, fuzzel, tofi, or auto-detect
- **Pinentry program**: for password prompts when unlocking the vault

Configuration is saved to `~/.config/rbwm/config` and can be edited manually or re-run the wizard by deleting the config file.

## Usage

Run `rbwm` to open the menu. The interface provides:

- **Direct selection**: Choose an entry to autofill username/password
- **[Details]**: View and type individual fields from an entry
- **[Notes]**: Access secure notes
- **[Sync]**: Sync with Bitwarden servers
- **[Add]**: Add a new entry
- **[Edit]**: Edit an existing entry
- **[Remove]**: Delete an entry
- **[Lock]/[Unlock]**: Manage vault state

### Keybinding Example

Add to your window manager config (e.g., sxhkd):

```
super + comma
    rbwm
```

## How It Works

1. Queries rbw for your vault entries
2. Presents them in dmenu/bemenu
3. On selection, automatically types credentials using xdotool/wtype
4. Restores previous clipboard contents after typing

## Security Notes

- Credentials are typed directly, never stored in clipboard permanently
- Previous clipboard contents are restored after use
- Requires rbw to be unlocked (prompts if locked)
- No passwords are logged or stored by this script

## License

MIT

## Credits

Built for use with [rbw](https://github.com/doy/rbw) by doy.
