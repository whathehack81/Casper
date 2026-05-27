from pathlib import Path

from casper.runtime.manifest import build_manifest, write_manifest


def test_manifest_creation(tmp_path: Path):
    manifest = build_manifest(["casper", "tool", "httpx"])

    assert manifest.run_id
    assert manifest.argv == ["casper", "tool", "httpx"]

    out = tmp_path / "manifest.json"
    write_manifest(out, manifest)

    assert out.exists()
    assert '"run_id"' in out.read_text()
