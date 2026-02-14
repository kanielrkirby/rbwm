"""
Configuration management for rbwm.
"""
import os
import subprocess
from pathlib import Path
from .system import System


class ConfigError(Exception):
    """User-facing configuration error."""
    pass


MENU_PROGRAMS = ["dmenu", "bemenu", "rofi", "wmenu", "fuzzel", "tofi"]
PINENTRY_PROGRAMS = ["pinentry-dmenu", "pinentry-curses", "pinentry-gnome3", "pinentry-qt", "pinentry"]


class Config:
    APP_NAME = "rbwm"
    
    def __init__(self):
        self._config = None
        self._menu_fallback_confirmed = False
        self._pinentry_fallback_confirmed = False
    
    @staticmethod
    def get_dir() -> Path:
        """Get config directory, creating if needed."""
        base = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
        path = Path(base) / Config.APP_NAME
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def config_file(self) -> Path:
        return self.get_dir() / 'config'
    
    def load(self):
        """Load configuration from file or run setup."""
        if not self.config_file.exists():
            self._config = self._setup()
        else:
            self._config = {}
            with open(self.config_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        self._config[key.strip()] = value.strip()
        
        return self._config
    
    def get_menu_cmd(self):
        """Get menu command with fallback logic."""
        configured = self._config.get("MENU_CMD")
        
        if configured == "auto" or not System.has_command(configured):
            wayland = os.environ.get("WAYLAND_DISPLAY")
            order = (
                ["fuzzel", "tofi", "wmenu", "bemenu", "rofi", "dmenu"] 
                if wayland 
                else MENU_PROGRAMS
            )
            
            menu_cmd = None
            for menu in order:
                if System.has_command(menu):
                    menu_cmd = menu
                    break
            
            if not menu_cmd:
                raise ConfigError(f"No menu program found. Install one of: {', '.join(MENU_PROGRAMS)}")
            
            # Confirmation prompt if we fell back (only once per session)
            if configured and configured != "auto" and not self._menu_fallback_confirmed:
                from .menu import select_from_menu_raw
                select_from_menu_raw(menu_cmd, ["Ok"], f"{configured} not found, using {menu_cmd}")
                self._menu_fallback_confirmed = True
            
            return menu_cmd
        
        return configured
    
    def get_pinentry_cmd(self):
        """Get pinentry command with fallback logic."""
        configured = self._config.get("PINENTRY_CMD")
        
        if not System.has_command(configured):
            pinentry_cmd = None
            for cmd in PINENTRY_PROGRAMS:
                if System.has_command(cmd):
                    pinentry_cmd = cmd
                    break
            
            if not pinentry_cmd:
                raise ConfigError(f"No pinentry program found. Install one of: {', '.join(PINENTRY_PROGRAMS)}")
            
            # Confirmation prompt before using fallback (only once per session)
            if not self._pinentry_fallback_confirmed:
                from .menu import select_from_menu_raw
                # Get menu_cmd WITHOUT triggering its fallback confirmation
                menu_configured = self._config.get("MENU_CMD")
                if menu_configured == "auto" or not System.has_command(menu_configured):
                    import os
                    wayland = os.environ.get("WAYLAND_DISPLAY")
                    order = (
                        ["fuzzel", "tofi", "wmenu", "bemenu", "rofi", "dmenu"] 
                        if wayland 
                        else MENU_PROGRAMS
                    )
                    menu_cmd = None
                    for menu in order:
                        if System.has_command(menu):
                            menu_cmd = menu
                            break
                    if not menu_cmd:
                        raise ConfigError(f"No menu program found. Install one of: {', '.join(MENU_PROGRAMS)}")
                else:
                    menu_cmd = menu_configured
                
                select_from_menu_raw(menu_cmd, ["Ok"], f"{configured} not found, using {pinentry_cmd}")
                self._pinentry_fallback_confirmed = True
            
            return pinentry_cmd
        
        return configured
    
    def _setup(self):
        """Run configuration wizard."""
        # Check if we're in a graphical environment
        has_display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        
        if has_display:
            return self._setup_gui()
        else:
            return self._setup_cli()
    
    def _setup_cli(self):
        """CLI-based configuration wizard."""
        print("rbwm configuration wizard")
        print("=" * 40)
        
        # Detect available menu programs
        menu_options = {
            "dmenu": "Classic dmenu (X11)",
            "bemenu": "bemenu (Wayland/X11)",
            "wmenu": "wmenu (Wayland)",
            "rofi": "rofi (X11/Wayland)",
            "fuzzel": "fuzzel (Wayland)",
            "tofi": "tofi (Wayland)",
        }
        
        # Check which are available
        menu_status = []
        for menu, desc in menu_options.items():
            is_available = subprocess.run(["which", menu], capture_output=True).returncode == 0
            menu_status.append((menu, desc, is_available))
        
        available_menus = [m for m, d, avail in menu_status if avail]
        
        if not available_menus:
            print("ERROR: No supported menu program found!")
            print("Please install one of: dmenu, bemenu, wmenu, rofi, fuzzel, tofi")
            import sys
            sys.exit(1)
        
        print("\nMenu programs:\n")
        idx_map = {}
        current_idx = 1
        for menu, desc, is_available in menu_status:
            if is_available:
                print(f"  {current_idx}. {menu} - {desc}\n")
                idx_map[current_idx] = menu
                current_idx += 1
            else:
                print(f"     {menu} - {desc} (not installed)\n")
        print(f"  {current_idx}. auto - Auto-detect\n")
        idx_map[current_idx] = 'auto'
        
        while True:
            choice = input(f"\nSelect menu program (1-{current_idx}) or enter custom command: ").strip()
            # Try as number first
            try:
                idx = int(choice)
                if idx in idx_map:
                    menu_cmd = idx_map[idx]
                    break
            except ValueError:
                # Not a number - accept as custom command
                if choice:
                    menu_cmd = choice
                    break
            print("Invalid choice, try again.")
        
        # Pinentry selection
        pinentry_options = [
            "pinentry-dmenu",
            "pinentry-curses", 
            "pinentry-gnome3",
            "pinentry-qt",
            "pinentry"
        ]
        
        # Check which are available
        pinentry_status = []
        for pe in pinentry_options:
            is_available = subprocess.run(["which", pe], capture_output=True).returncode == 0
            pinentry_status.append((pe, is_available))
        
        available_pinentry = [pe for pe, avail in pinentry_status if avail]
        
        if not available_pinentry:
            print("\nWARNING: No pinentry program found!")
            pinentry_cmd = "pinentry"
        else:
            print("\nPinentry programs:\n")
            idx_map = {}
            current_idx = 1
            for pe, is_available in pinentry_status:
                if is_available:
                    print(f"  {current_idx}. {pe}\n")
                    idx_map[current_idx] = pe
                    current_idx += 1
                else:
                    print(f"     {pe} (not installed)\n")
            
            while True:
                choice = input(f"\nSelect pinentry program (1-{len(available_pinentry)}) or enter custom command: ").strip()
                # Try as number first
                try:
                    idx = int(choice)
                    if idx in idx_map:
                        pinentry_cmd = idx_map[idx]
                        break
                except ValueError:
                    # Not a number - accept as custom command
                    if choice:
                        pinentry_cmd = choice
                        break
                print("Invalid choice, try again.")
        
        # Write config
        config_content = f"""# ============================================
# rbwm - Bitwarden Menu Configuration
# ============================================
#
# This file configures the menu program and pinentry program used by rbwm.
# Run 'rbwm setup' to reconfigure.
#

# Menu program for displaying selections
# Options: dmenu, bemenu, rofi, wmenu, fuzzel, tofi, auto
# Set to 'auto' to automatically detect available menu programs
MENU_CMD={menu_cmd}

# Pinentry program for password prompts when unlocking vault
# Options: pinentry-dmenu, pinentry-curses, pinentry-gnome3, pinentry-qt, pinentry
PINENTRY_CMD={pinentry_cmd}
"""
        
        with open(self.config_file, "w") as f:
            f.write(config_content)
        
        print(f"\nConfiguration saved to {self.config_file}")
        
        return {"MENU_CMD": menu_cmd, "PINENTRY_CMD": pinentry_cmd}
    
    def _setup_gui(self):
        """GUI-based configuration using first available menu."""
        # Find first available menu for the wizard
        wizard_menus = ["dmenu", "bemenu", "rofi", "wmenu", "fuzzel", "tofi"]
        wizard_menu = None
        for menu in wizard_menus:
            if subprocess.run(["which", menu], capture_output=True).returncode == 0:
                wizard_menu = menu
                break
        
        if not wizard_menu:
            return self._setup_cli()
        
        def simple_menu(items, prompt):
            """Simple menu for wizard."""
            if wizard_menu == "rofi":
                cmd = f"rofi -dmenu -p '{prompt}'"
            elif wizard_menu == "fuzzel":
                cmd = f"fuzzel --dmenu -p '{prompt}'"
            elif wizard_menu == "wmenu":
                cmd = f"wmenu -p '{prompt}'"
            elif wizard_menu == "tofi":
                cmd = f"tofi --prompt '{prompt}'"
            else:
                # dmenu and bemenu support -l
                cmd = f"{wizard_menu} -l 15 -i -p '{prompt}'"
            
            result = subprocess.run(
                cmd,
                shell=True,
                input="\n".join(items),
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        
        # Menu selection - show all with availability markers
        all_menus = ["dmenu", "bemenu", "wmenu", "rofi", "fuzzel", "tofi"]
        menu_options = []
        for menu in all_menus:
            is_available = subprocess.run(["which", menu], capture_output=True).returncode == 0
            if is_available:
                menu_options.append(menu)
            else:
                menu_options.append(f"{menu} (not installed)")
        
        menu_options.append("auto")
        
        menu_choice = simple_menu(menu_options, "Select menu")
        if not menu_choice:
            import sys
            sys.exit(1)
        
        # Strip "(not installed)" suffix if present
        menu_cmd = menu_choice.replace(" (not installed)", "")
        
        # Pinentry selection
        all_pinentry = ["pinentry-dmenu", "pinentry-curses", "pinentry-gnome3", "pinentry-qt", "pinentry"]
        pinentry_options = []
        for pe in all_pinentry:
            is_available = subprocess.run(["which", pe], capture_output=True).returncode == 0
            if is_available:
                pinentry_options.append(pe)
            else:
                pinentry_options.append(f"{pe} (not installed)")
        
        pinentry_choice = simple_menu(pinentry_options, "Select pinentry") if pinentry_options else "pinentry"
        
        # Strip "(not installed)" suffix if present
        pinentry_cmd = pinentry_choice.replace(" (not installed)", "") if pinentry_choice else "pinentry"
        
        # Write config
        config_content = f"""# ============================================
# rbwm - Bitwarden Menu Configuration
# ============================================
#
# This file configures the menu program and pinentry program used by rbwm.
# Run 'rbwm setup' to reconfigure.
#

# Menu program for displaying selections
# Options: dmenu, bemenu, rofi, wmenu, fuzzel, tofi, auto
# Set to 'auto' to automatically detect available menu programs
MENU_CMD={menu_cmd}

# Pinentry program for password prompts when unlocking vault
# Options: pinentry-dmenu, pinentry-curses, pinentry-gnome3, pinentry-qt, pinentry
PINENTRY_CMD={pinentry_cmd}
"""
        
        with open(self.config_file, "w") as f:
            f.write(config_content)
        
        return {"MENU_CMD": menu_cmd, "PINENTRY_CMD": pinentry_cmd}


# Singleton instance
CONFIG = Config()
