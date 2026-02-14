"""System utilities for rbwm."""
import subprocess
import shutil


class System:
    @staticmethod
    def has_command(cmd: str) -> bool:
        """Check if command exists in PATH."""
        return shutil.which(cmd) is not None
    
    @staticmethod
    def notify(message: str, title: str = "rbwm"):
        """Show notification via notify-send."""
        if System.has_command("notify-send"):
            subprocess.run(
                ["notify-send", title, message], 
                capture_output=True
            )
