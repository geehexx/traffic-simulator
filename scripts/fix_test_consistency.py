"""
Script to automatically fix test file consistency issues.

This script applies the consistency standards to all test files in the tests directory.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def fix_test_file(file_path: Path) -> bool:
    """
    Fix consistency issues in a test file.

    Returns True if changes were made, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    original_content = content
    lines = content.split("\n")

    # Check if file starts with shebang and remove it
    if lines and lines[0].startswith("#!/"):
        lines = lines[1:]
        content = "\n".join(lines)

    # Parse the AST
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False

    # Check if we need to add future annotations
    has_future_annotations = False
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    has_future_annotations = True
                    break

    # Check if we need to add pytest import
    has_pytest_import = False
    for node in tree.body:
        if isinstance(node, ast.Import) and any(alias.name == "pytest" for alias in node.names):
            has_pytest_import = True
            break
        elif isinstance(node, ast.ImportFrom) and node.module == "pytest":
            has_pytest_import = True
            break

    # Check if we have main block
    has_main_block = False
    for node in tree.body:
        if isinstance(node, ast.If):
            if (
                isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
                and len(node.test.comparators) == 1
                and isinstance(node.test.comparators[0], ast.Constant)
                and node.test.comparators[0].value == "__main__"
            ):
                has_main_block = True
                break

    # Check if we have a docstring
    has_docstring = (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    )

    # Apply fixes
    new_lines = lines.copy()
    insert_index = 0
    
    # Add docstring if missing or fix position
    if not has_docstring:
        docstring = f'"""Tests for {file_path.stem.replace("_", " ")}."""'
        new_lines.insert(insert_index, docstring)
        new_lines.insert(insert_index + 1, "")
        insert_index += 2
    else:
        # Check if docstring is at the beginning
        if not (new_lines[0].strip().startswith('"""') or new_lines[0].strip().startswith("'''")):
            # Find and move docstring to the beginning
            docstring_line_idx = None
            for i, line in enumerate(new_lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    docstring_line_idx = i
                    break
            
            if docstring_line_idx is not None:
                # Remove docstring from current position
                docstring_line = new_lines.pop(docstring_line_idx)
                # Insert at the beginning
                new_lines.insert(0, docstring_line)
                new_lines.insert(1, "")
                insert_index = 2
    
    # Add future annotations if missing - must be at the very beginning
    if not has_future_annotations:
        new_lines.insert(insert_index, "from __future__ import annotations")
        new_lines.insert(insert_index + 1, "")
        insert_index += 2
    
    # Add pytest import if missing
    if not has_pytest_import:
        new_lines.insert(insert_index, "import pytest")
        new_lines.insert(insert_index + 1, "")
        insert_index += 2
    
    # Fix import order if future annotations is not at the beginning
    if has_future_annotations:
        # Find where future annotations is and move it to the beginning
        future_line_idx = None
        for i, line in enumerate(new_lines):
            if line.strip() == "from __future__ import annotations":
                future_line_idx = i
                break
        
        if future_line_idx is not None and future_line_idx > 0:
            # Remove from current position
            future_line = new_lines.pop(future_line_idx)
            # Insert at the beginning after docstring
            new_lines.insert(insert_index, future_line)
            new_lines.insert(insert_index + 1, "")

    # Add main block if missing
    if not has_main_block:
        new_lines.append("")
        new_lines.append("")
        new_lines.append('if __name__ == "__main__":')
        new_lines.append("    pytest.main([__file__])")

    # Write the fixed content
    fixed_content = "\n".join(new_lines)

    if fixed_content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print(f"Fixed {file_path}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False

    return False


def main() -> int:
    """Main function to fix test file consistency."""
    tests_dir = Path("tests")

    if not tests_dir.exists():
        print("Error: tests directory not found")
        return 1

    test_files = [f for f in tests_dir.glob("*.py") if f.name != "__init__.py"]

    if not test_files:
        print("No test files found")
        return 0

    fixed_count = 0
    for test_file in test_files:
        if fix_test_file(test_file):
            fixed_count += 1

    print(f"\nFixed {fixed_count} out of {len(test_files)} test files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
