"""Apply the African staff/portrait update after Render extracts its bundled source."""
from pathlib import Path
import base64
import lzma
import subprocess

_APP_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _APP_ROOT.parent
_MARKER = _APP_ROOT / ".african_team_update_applied"
_PARTS = [
    _REPO_ROOT / "workforce-ai-patch.part1.b64",
    _REPO_ROOT / "workforce-ai-patch.part2.b64",
    _REPO_ROOT / "workforce-ai-patch.part3.b64",
]

if not _MARKER.exists() and all(part.is_file() for part in _PARTS):
    try:
        encoded = "".join(part.read_text(encoding="ascii").strip() for part in _PARTS)
        patch_data = lzma.decompress(base64.b64decode(encoded, validate=True))
        result = subprocess.run(
            ["patch", "--batch", "--forward", "-p1", "-d", str(_APP_ROOT)],
            input=patch_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode == 0:
            _MARKER.write_text("Applied African team update.\n", encoding="utf-8")
            print("Workforce AI African team update applied.")
        else:
            print("Workforce AI update patch did not apply cleanly; leaving source unchanged.")
            print(result.stdout.decode("utf-8", errors="replace")[-2000:])
    except Exception as exc:
        print(f"Workforce AI update patch could not be applied: {type(exc).__name__}: {exc}")
