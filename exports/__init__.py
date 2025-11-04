from pathlib import Path

EXPORT_DIR = Path("exports/out")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

__all__ = ["EXPORT_DIR"]
