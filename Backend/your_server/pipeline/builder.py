"""
pipeline/builder.py — Step 5: Build the .whl from the injected workspace
Runs `python -m build` inside workspace/build/ and returns the .whl path.
"""

import subprocess
import sys
from pathlib import Path


def build_whl(workspace: Path) -> str:
    """
    Run `python -m build` inside workspace/build/.
    Returns the absolute path to the generated .whl file.

    Raises RuntimeError if the build fails.
    """
    build_dir = workspace / "build"

    if not build_dir.exists():
        raise FileNotFoundError(f"Build directory not found: {build_dir}")

    # Run the build tool
    result = subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=str(build_dir),
        capture_output=True,
        text=True,
        timeout=120,   # 2 minute timeout
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Build failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    # Find the .whl in dist/
    dist_dir = build_dir / "dist"
    whl_files = list(dist_dir.glob("*.whl"))

    if not whl_files:
        raise FileNotFoundError(
            f"Build succeeded but no .whl found in {dist_dir}\n"
            f"stdout: {result.stdout}"
        )

    whl_path = str(whl_files[0].resolve())
    print(f"[BUILDER] .whl created → {whl_path}")
    return whl_path
