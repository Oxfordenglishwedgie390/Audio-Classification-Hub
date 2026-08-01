"""
pipeline/injector.py — Step 4: Bake the user's embedding into the package code
Takes the master (192,) numpy array and replaces {{EMBEDDING}} in core_template.py
Writes the final core.py into the workspace build folder.
"""

import shutil
import numpy as np
from pathlib import Path


TEMPLATE_DIR = Path(__file__).parent.parent / "template"


def inject_embedding(master: np.ndarray, workspace: Path):
    """
    1. Copy the entire template/ folder into workspace/build/
    2. Read core_template.py
    3. Replace {{EMBEDDING}} with the actual 192 numbers as a Python list
    4. Write result as core.py
    5. Delete core_template.py (not needed in final package)

    Input : master numpy array (192,), workspace Path
    Output: workspace/build/  folder is now ready to build into .whl
    """
    build_dir = workspace / "build"

    # Fresh copy of template into workspace/build/
    if build_dir.exists():
        shutil.rmtree(build_dir)
    shutil.copytree(TEMPLATE_DIR, build_dir)

    # Read the template
    template_file = build_dir / "src" / "audioauth" / "core_template.py"
    if not template_file.exists():
        raise FileNotFoundError(f"core_template.py not found at {template_file}")

    template_code = template_file.read_text(encoding="utf-8")

    # Convert numpy array → Python list literal string
    embedding_list = master.tolist()          # list of 192 Python floats
    embedding_str  = repr(embedding_list)     # e.g. [0.023, -0.114, ...]

    # Inject
    if "{{EMBEDDING}}" not in template_code:
        raise ValueError("core_template.py is missing the {{EMBEDDING}} placeholder")

    final_code = template_code.replace("{{EMBEDDING}}", embedding_str)

    # Write as core.py
    core_file = build_dir / "src" / "audioauth" / "core.py"
    core_file.write_text(final_code, encoding="utf-8")

    # Remove the template file from the package
    template_file.unlink()
    # also remove company template if it exists
    comp_template_file = build_dir / "src" / "audioauth" / "core_company_template.py"
    if comp_template_file.exists():
        comp_template_file.unlink()

    print(f"[INJECTOR] Embedding injected → {core_file}")


def inject_company_embeddings(company_master: dict, workspace: Path):
    """
    Input: dict of { "PersonName": (192,) }, workspace Path
    """
    build_dir = workspace / "build"

    # Fresh copy of template into workspace/build/
    if build_dir.exists():
        shutil.rmtree(build_dir)
    shutil.copytree(TEMPLATE_DIR, build_dir)

    # Read the company template
    template_file = build_dir / "src" / "audioauth" / "core_company_template.py"
    if not template_file.exists():
        raise FileNotFoundError(f"core_company_template.py not found at {template_file}")

    template_code = template_file.read_text(encoding="utf-8")

    # Convert dict of numpy arrays → Python dict literal string
    embedding_dict = {name: emb.tolist() for name, emb in company_master.items()}
    embedding_str  = repr(embedding_dict)

    if "{{COMPANY_EMBEDDINGS}}" not in template_code:
        raise ValueError("core_company_template.py is missing the {{COMPANY_EMBEDDINGS}} placeholder")

    final_code = template_code.replace("{{COMPANY_EMBEDDINGS}}", embedding_str)

    # Write as core.py
    core_file = build_dir / "src" / "audioauth" / "core.py"
    core_file.write_text(final_code, encoding="utf-8")

    # Remove the template files from the package
    template_file.unlink()
    single_template = build_dir / "src" / "audioauth" / "core_template.py"
    if single_template.exists():
        single_template.unlink()

    print(f"[INJECTOR] Company embeddings injected → {core_file}")
