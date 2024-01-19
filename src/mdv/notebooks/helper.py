from pathlib import Path
import sys

def fix_path():
    """Adds module to path so we can import from mdv."""
    module_path = (Path(__file__).parent / '..' / '..').resolve()
    module_path_str = str(module_path)
    if module_path_str not in sys.path:
        sys.path.insert(1, module_path_str)
