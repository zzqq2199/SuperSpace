import sys
from pathlib import Path


def get_app_location(
    executable: str | None = None,
    script_file: str | None = None,
    frozen: bool | None = None,
) -> str:
    executable_path = Path(executable or sys.executable).resolve()
    script_path = Path(script_file or __file__).resolve()
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen

    for path in (executable_path, *executable_path.parents):
        if path.suffix == ".app":
            return str(path)

    if is_frozen:
        return str(executable_path.parent)

    return str(script_path.parent)
