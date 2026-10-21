import pytest
import json
import tempfile
import importlib.util
from pathlib import Path

scripts_dir = Path(__file__).parent.parent.parent / "scripts"

spec_hooks = importlib.util.spec_from_file_location("validate_hooks", scripts_dir / "validate-hooks.py")
hooks_module = importlib.util.module_from_spec(spec_hooks)
spec_hooks.loader.exec_module(hooks_module)
validate_hooks_json = hooks_module.validate_hooks_json

spec_mcp = importlib.util.spec_from_file_location("validate_mcp", scripts_dir / "validate-mcp.py")
mcp_module = importlib.util.module_from_spec(spec_mcp)
spec_mcp.loader.exec_module(mcp_module)
validate_mcp_json = mcp_module.validate_mcp_json


class TestHooksJsonValidator:
    """Test hooks.json schema validation."""

    def test_valid_hooks_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"hooks": {}}, f)
            f.flush()
            ok, msg = validate_hooks_json(Path(f.name))
            assert ok is True
            assert msg == "OK"

    def test_bare_array_rejected(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            f.flush()
            ok, msg = validate_hooks_json(Path(f.name))
            assert ok is False
            assert "Root must be object" in msg

    def test_missing_hooks_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            f.flush()
            ok, msg = validate_hooks_json(Path(f.name))
            assert ok is False
            assert "Missing required 'hooks' key" in msg

    def test_hooks_not_object(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"hooks": []}, f)
            f.flush()
            ok, msg = validate_hooks_json(Path(f.name))
            assert ok is False
            assert "'hooks' must be object" in msg

    def test_hooks_with_content(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"hooks": {"pre_tool_use": []}}, f)
            f.flush()
            ok, msg = validate_hooks_json(Path(f.name))
            assert ok is True
            assert msg == "OK"

    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            f.flush()
            ok, msg = validate_hooks_json(Path(f.name))
            assert ok is False
            assert "Invalid JSON" in msg


class TestMcpJsonValidator:
    """Test .mcp.json schema validation."""

    def test_valid_connectors(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"connectors": {"example": {"url": "http://example.com"}}}, f)
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is True
            assert msg == "OK"

    def test_valid_servers(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"servers": {"example": {"command": "npx", "args": ["server"]}}}, f)
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is True
            assert msg == "OK"

    def test_missing_both_keys(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"other": "value"}, f)
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is False
            assert "Must have 'connectors' or 'servers' key" in msg

    def test_connectors_not_object(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"connectors": []}, f)
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is False
            assert "'connectors' must be object" in msg

    def test_servers_not_object(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"servers": "not-an-object"}, f)
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is False
            assert "'servers' must be object" in msg

    def test_invalid_json_missing_comma(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"connectors": {"egnyte": {"url": "..."} "box": {"url": "..."}}}')
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is False
            assert "Invalid JSON" in msg

    def test_invalid_json_unclosed_brace(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"connectors": {"egnyte": {"url": "..."}}}')
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is True

    def test_unclosed_object_brace(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"connectors": {"egnyte": {"url": "..."}}')
            f.flush()
            ok, msg = validate_mcp_json(Path(f.name))
            assert ok is False
            assert "Invalid JSON" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])