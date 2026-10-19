"""Generates a desktop shortcut to launch White Coding Harness."""

import os
import sys

try:
    import winshell
    from win32com.client import Dispatch
except ImportError:
    print("[INFO] winshell or pywin32 not installed, skipping desktop shortcut creation.")
    sys.exit(0)

try:
    desktop = winshell.desktop()
    path = os.path.join(desktop, "WHITE CODING HARNESS.lnk")
    target = os.path.abspath("INICIAR_WHITE_CODING_HARNESS.bat")
    wDir = os.path.abspath(".")

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = target
    shortcut.save()
    print(f"[OK] Acceso directo creado exitosamente en: {path}")
except (OSError, RuntimeError, ImportError) as e:
    print(f"[WARN] No se pudo crear el acceso directo: {e}")
