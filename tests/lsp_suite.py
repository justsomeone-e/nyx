import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(BASE_DIR, "src", "cli.py")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from src.toolchain.lsp_server import NyxuageServer
from src.core.language_surface import (
    EXPERIMENTAL_KEYWORDS,
    RESERVED_KEYWORDS,
    STABLE_KEYWORDS,
)

def run_lsp_suite():
    print("=" * 70)
    print("⚡ NYX LSP v2 IDE SERVICE HARNESS")
    print("=" * 70)

    server = NyxuageServer()
    test_uri = "file:///C:/test_project/main.nyx"
    test_code = """import "std/math"

struct Point { x: int, y: int }

fn calculate_distance(p1: Point, p2: Point) -> float {
    var dx = abs(p1.x - p2.x)
    var dy = abs(p1.y - p2.y)
    return dx + dy
}

var pt = Point(10, 20)
print(calculate_distance(pt, pt))
"""
    server.documents[test_uri] = test_code
    server.validate_document(test_uri, test_code)

    # 1. Test Autocompletion
    print("[*] Testing LSP Autocompletion (Local & stdlib imported symbols)...")
    comp_items = server.handle_completion(test_uri, {"line": 10, "character": 5})
    labels = [item["label"] for item in comp_items]
    assert "abs" in labels, "Imported stdlib function 'abs' must appear in completions"
    assert "pow" in labels, "Imported stdlib function 'pow' must appear in completions"
    assert "Point" in labels, "Local struct 'Point' must appear in completions"
    assert "calculate_distance" in labels, "Local function 'calculate_distance' must appear in completions"
    assert "print" in labels and "match" in labels
    for canonical_label in (
        "append_string",
        "fnv1a_64_hex",
        "nucleo-f401re",
        "cpp",
        "Buffer",
        "args",
    ):
        assert canonical_label in labels, f"Missing canonical completion: {canonical_label}"
    assert len(comp_items) >= 200, "Canonical completion catalog unexpectedly shrank"
    assert set(STABLE_KEYWORDS).issubset(labels)
    assert set(EXPERIMENTAL_KEYWORDS).issubset(labels)
    assert set(RESERVED_KEYWORDS).isdisjoint(labels)
    assert "val" not in labels

    with open(os.path.join(BASE_DIR, "vscode-extension", "language-surface.json"), "r", encoding="utf-8") as handle:
        editor_surface = json.load(handle)
    assert tuple(editor_surface["stableKeywords"]) == STABLE_KEYWORDS
    assert tuple(editor_surface["experimentalKeywords"]) == EXPERIMENTAL_KEYWORDS
    assert tuple(editor_surface["reservedKeywords"]) == RESERVED_KEYWORDS
    print(f"  [PASS] Autocompletion returned {len(comp_items)} verified symbols")

    incomplete_uri = "file:///C:/test_project/incomplete.nyx"
    incomplete_source = "fn local_helper(value: int) -> int {\n    let local_value = value +\n"
    server.documents[incomplete_uri] = incomplete_source
    server.validate_document(incomplete_uri, incomplete_source)
    incomplete_labels = {
        item["label"]
        for item in server.handle_completion(incomplete_uri, {"line": 1, "character": 28})
    }
    assert "local_helper" in incomplete_labels
    assert "local_value" in incomplete_labels
    print("  [PASS] Half-written source keeps local declarations available")

    # 2. Test Hover Information
    print("[*] Testing LSP Hover Tooltips...")
    hover_fn = server.handle_hover(test_uri, {"line": 4, "character": 5}) # 'calculate_distance'
    assert hover_fn is not None and "calculate_distance" in hover_fn["contents"]["value"]
    hover_struct = server.handle_hover(test_uri, {"line": 2, "character": 8}) # 'Point'
    assert hover_struct is not None and "struct Point" in hover_struct["contents"]["value"]
    hover_builtin = server.handle_hover(test_uri, {"line": 11, "character": 2}) # 'print'
    assert hover_builtin is not None and "Writes values" in hover_builtin["contents"]["value"]
    print("  [PASS] Hover cards correctly formatted Markdown signatures")

    # 3. Test Go To Definition
    print("[*] Testing LSP Go-To-Definition...")
    def_res = server.handle_definition(test_uri, {"line": 11, "character": 8}) # 'calculate_distance'
    assert def_res is not None
    assert def_res["range"]["start"]["line"] == 4, "Should point to line 5 (0-indexed 4)"
    print("  [PASS] Go-To-Definition resolved exact AST source location")

    # 4. Verify the real CLI process speaks framed JSON-RPC without import errors.
    print("[*] Testing CLI LSP JSON-RPC process contract...")
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "shutdown", "params": {}},
        {"jsonrpc": "2.0", "method": "exit", "params": {}},
    ]
    wire_input = b""
    for message in messages:
        body = json.dumps(message).encode("utf-8")
        wire_input += f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body
    process = subprocess.run(
        [sys.executable, CLI_PATH, "lsp"],
        cwd=BASE_DIR,
        input=wire_input,
        capture_output=True,
    )
    assert process.returncode == 0, process.stderr.decode("utf-8", errors="replace")
    output = process.stdout
    assert b'"id": 1' in output and b'"hoverProvider": true' in output
    assert b'"id": 2' in output and b'"result": null' in output
    print("  [PASS] nyx lsp initialize/shutdown framing verified")

    print("=" * 70)
    print("[OK] LSP v2 Conformance: 4/4 Passed")
    print("=" * 70)
    return True

if __name__ == "__main__":
    ok = run_lsp_suite()
    sys.exit(0 if ok else 1)
