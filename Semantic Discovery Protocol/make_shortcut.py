"""Generates a desktop shortcut to launch Semantic Discovery Protocol."""

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
    path = os.path.join(desktop, "IWAN - Semantic Discovery Protocol.lnk")
    target = os.path.abspath("INICIAR_SEMANTIC_DISCOVERY.bat")
    wDir = os.path.abspath(".")

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = target
    shortcut.save()
    print(f"[OK] Acceso directo creado exitosamente en: {path}")
except Exception as e:  # noqa: BLE001
    print(f"[WARN] No se pudo crear el acceso directo: {e}")
