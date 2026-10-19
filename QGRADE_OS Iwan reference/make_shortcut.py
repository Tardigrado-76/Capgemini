"""Script para generar el acceso directo en el Escritorio para QUANTIGRADE - The Maestro Cockpit."""

import os
import subprocess
import sys


def create_desktop_shortcut():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INICIAR_QUANTIGRADE_MAESTRO.bat")
    shortcut_path = os.path.join(desktop, "QUANTIGRADE - The Maestro Cockpit.lnk")
    
    try:
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = bat_path
        shortcut.WorkingDirectory = os.path.dirname(bat_path)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        print(f"[OK] Acceso directo creado en: {shortcut_path}")
    except (OSError, RuntimeError, ImportError):
        # Fallback via PowerShell
        ps_script = f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_path}');$s.TargetPath='{bat_path}';$s.WorkingDirectory='{os.path.dirname(bat_path)}';$s.Save()"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=False)
        print(f"[OK] Acceso directo generado via PowerShell en: {shortcut_path}")

if __name__ == "__main__":
    create_desktop_shortcut()
