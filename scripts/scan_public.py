"""Pre-publication checks. Reports locations/categories only; never prints matched values."""
import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "provider token": r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{24,})",
    "embedded URL credentials": r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/'\"]+:[^\s/'\"]+@",
    "literal credential": r"(?i)(?:password|passwd|token|secret)\s*=\s*['\"][^'\"]{4,}['\"]",
    "local user path": r"(?i)[a-z]:[\\/]+users[\\/]+(?!public\b)",
}


def main():
    paths = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT
    ).decode().split("\0")
    issues = []
    checked = 0
    for name in filter(None, paths):
        path = ROOT / name
        if not path.is_file() or name == "scripts/scan_public.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".sql", ".csv", ".json", ".ipynb",
                                       ".yml", ".yaml", ".toml", ".txt", ".example", ".acl"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        checked += 1
        for category, pattern in PATTERNS.items():
            if re.search(pattern, text):
                issues.append((name, category))
        if name.startswith("data/synthetic/") and path.suffix == ".csv":
            for row in csv.DictReader(text.splitlines()):
                for key in ("row_id", "student_ref", "program_ref"):
                    if row.get(key) and not row[key].startswith("SYN-"):
                        issues.append((name, "non-synthetic identifier"))
    if issues:
        for name, category in issues:
            print(f"FAIL {name}: {category}")
        raise SystemExit(1)
    print(f"PASS: {checked} public text files; credential patterns and synthetic identifiers checked.")
    print("Scope: working-tree text only; not an image, history, or secret-rotation audit.")


if __name__ == "__main__":
    main()
