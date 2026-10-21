#!/usr/bin/env python3
"""Validate .mcp.json files in plugin directories."""

import json
import sys
from pathlib import Path
from typing import List, Tuple


def validate_mcp_json(filepath: Path) -> Tuple[bool, str]:
    """Validate .mcp.json is valid JSON with expected structure."""
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

    # Check for required structure: connectors or servers
    has_connectors = "connectors" in data
    has_servers = "servers" in data

    if not has_connectors and not has_servers:
        return False, "Must have 'connectors' or 'servers' key"

    if has_connectors and not isinstance(data["connectors"], dict):
        return False, "'connectors' must be object"

    if has_servers and not isinstance(data["servers"], dict):
        return False, "'servers' must be object"

    return True, "OK"


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-mcp.py <path> [path...]")
        sys.exit(1)

    paths = [Path(p) for p in sys.argv[1:]]
    mcp_files: List[Path] = []

    for path in paths:
        if path.is_dir():
            mcp_files.extend(path.rglob(".mcp.json"))
        elif path.name == ".mcp.json":
            mcp_files.append(path)

    if not mcp_files:
        print("No .mcp.json files found")
        sys.exit(0)

    all_ok = True
    for filepath in mcp_files:
        ok, msg = validate_mcp_json(filepath)
        status = "✓" if ok else "✗"
        print(f"{status} {filepath}: {msg}")
        if not ok:
            all_ok = False

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()