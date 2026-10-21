#!/usr/bin/env python3
"""Validate hooks.json files in plugin directories."""

import json
import sys
from pathlib import Path
from typing import List, Tuple


def validate_hooks_json(filepath: Path) -> Tuple[bool, str]:
    """Validate hooks.json has correct schema: {'hooks': {}}."""
    try:
        content = filepath.read_text()
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Read error: {e}"

    # Check root is object
    if not isinstance(data, dict):
        return False, f"Root must be object, got {type(data).__name__}"

    # Check 'hooks' key exists and is object
    if "hooks" not in data:
        return False, "Missing required 'hooks' key"

    if not isinstance(data["hooks"], dict):
        return False, f"'hooks' must be object, got {type(data['hooks']).__name__}"

    return True, "OK"


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-hooks.py <path> [path...]")
        sys.exit(1)

    paths = [Path(p) for p in sys.argv[1:]]
    hooks_files: List[Path] = []

    for path in paths:
        if path.is_dir():
            hooks_files.extend(path.rglob("hooks.json"))
        elif path.name == "hooks.json":
            hooks_files.append(path)

    if not hooks_files:
        print("No hooks.json files found")
        sys.exit(0)

    all_ok = True
    for filepath in hooks_files:
        ok, msg = validate_hooks_json(filepath)
        status = "✓" if ok else "✗"
        print(f"{status} {filepath}: {msg}")
        if not ok:
            all_ok = False

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()