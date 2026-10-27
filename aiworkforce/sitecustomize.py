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

def _update_already_present():
    migration = _APP_ROOT / "workforce/migrations/0002_agent_person_name.py"
    model = _APP_ROOT / "workforce/models.py"
    catalog = _APP_ROOT / "workforce/agent_catalog.py"
    portraits = [
        _APP_ROOT / f"workforce/static/workforce/agents/{slug}-portrait.svg"
        for slug in ("aura", "nova", "sage", "pixel", "atlas")
    ]
    if not (migration.is_file() and model.is_file() and catalog.is_file() and all(p.is_file() for p in portraits)):
        return False
    model_text = model.read_text(encoding="utf-8")
    catalog_text = catalog.read_text(encoding="utf-8")
    return "person_name" in model_text and all(
        name in catalog_text for name in ("Amaka Okoye", "Tunde Adebayo", "Chidi Okafor", "Zainab Bello", "Kofi Mensah")
    )

if not _MARKER.exists():
    try:
        if _update_already_present():
            _MARKER.write_text("African team update already present in source bundle.\n", encoding="utf-8")
            print("Workforce AI African staff names and portraits are already present.")
        elif all(part.is_file() for part in _PARTS):
            encoded = "".join(part.read_text(encoding="ascii").strip() for part in _PARTS)
            patch_data = lzma.decompress(base64.b64decode(encoded, validate=True))
            result = subprocess.run(
                ["patch", "--batch", "--forward", "-p1", "-d", str(_APP_ROOT)],
                input=patch_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode == 0 or _update_already_present():
                _MARKER.write_text("African team update is present.\n", encoding="utf-8")
                print("Workforce AI African team update is ready.")
            else:
                print("Workforce AI update patch did not apply cleanly; source was not verified as updated.")
                print(result.stdout.decode("utf-8", errors="replace")[-2000:])
    except Exception as exc:
        print(f"Workforce AI update patch could not be applied: {type(exc).__name__}: {exc}")
