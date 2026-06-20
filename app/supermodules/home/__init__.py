import runpy
from pathlib import Path

def run():
    """Run the home page script."""
    path = Path(__file__).resolve() / 'pages.py'
    return runpy.run_path(str(path), run_name='__main__')
