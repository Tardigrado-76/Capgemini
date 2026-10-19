import sys
import types
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

# Map virtual package name 'qgrade_core' to this directory
if "qgrade_core" not in sys.modules:
    _mod = types.ModuleType("qgrade_core")
    _mod.__path__ = [str(_pkg_root)]
    _mod.__file__ = str(_pkg_root / "__init__.py")
    _mod.__version__ = "2.0.0"
    _mod.__suite__ = "Quantigrade - Detalle Iwan"
    sys.modules["qgrade_core"] = _mod
