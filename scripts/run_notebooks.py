"""Execute the three offline notebooks in fresh kernels; preserve source notebooks."""
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/executed_notebooks"))
    parser.add_argument("--kernel", default="python3")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    for path in sorted((root / "notebooks").glob("*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(notebook, timeout=120, kernel_name=args.kernel,
                       resources={"metadata": {"path": str(root)}}).execute()
        nbformat.write(notebook, args.output / path.name)
        print("Executed", path.name)


if __name__ == "__main__":
    main()
