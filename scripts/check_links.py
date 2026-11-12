"""Check relative documentation links, notebook links, and Markdown images without network access."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    missing = []
    sources = [ROOT / "README.md", ROOT / "README.es.md", *sorted((ROOT / "docs").rglob("*.md"))]
    texts = [(p, p.read_text(encoding="utf-8")) for p in sources]
    for p in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = json.loads(p.read_text(encoding="utf-8"))
        texts.append((p, "\n".join(
            "".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "markdown"
        )))
    for path, text in texts:
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            count += 1
            if not (path.parent / target).exists():
                missing.append((str(path.relative_to(ROOT)), target))
    if missing:
        for path, target in missing:
            print("Broken link:", path, target)
        raise SystemExit(1)
    print(f"PASS: {count} local links and image references")


if __name__ == "__main__":
    main()
