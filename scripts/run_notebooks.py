"""Execute only the three public synthetic notebooks; optionally publish scrubbed outputs."""
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/executed_notebooks"))
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--publish", action="store_true", help="Refresh public synthetic notebook outputs")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    paths = sorted((root / "notebooks").glob("*.ipynb"))
    if len(paths) != 3:
        raise RuntimeError("Expected exactly three public notebooks")
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        NotebookClient(notebook, timeout=120, kernel_name=args.kernel, record_timing=False,
                       resources={"metadata": {"path": str(root)}}).execute()
        notebook.metadata = {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}
        }
        for cell in notebook.cells:
            cell.metadata = {}
        nbformat.write(notebook, args.output / path.name)
        if args.publish:
            nbformat.write(notebook, path)
        print("Executed", path.name)


if __name__ == "__main__":
    main()
