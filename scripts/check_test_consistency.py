"""
Pre-commit hook to check test file consistency.

This script ensures all test files follow consistent patterns for direct execution.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def check_test_file_consistency(file_path: Path) -> list[str]:
    """
    Check if a test file follows consistency standards.

    Returns a list of issues found, empty list if all checks pass.
    """
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Could not read file: {e}"]

    # Parse the AST
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        return [f"Syntax error: {e}"]

    # Check 1: Must have from __future__ import annotations
    has_future_annotations = False
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    has_future_annotations = True
                    break

    if not has_future_annotations:
        issues.append("Missing 'from __future__ import annotations' at top of file")

    # Check 2: Must have if __name__ == "__main__" block with pytest.main
    has_main_block = False
    has_pytest_main = False

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

                # Check if it contains pytest.main call
                for stmt in node.body:
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        if (
                            isinstance(stmt.value.func, ast.Attribute)
                            and isinstance(stmt.value.func.value, ast.Name)
                            and stmt.value.func.value.id == "pytest"
                            and stmt.value.func.attr == "main"
                        ):
                            has_pytest_main = True

                            # Check arguments - should be [__file__] only
                            if (
                                len(stmt.value.args) == 1
                                and isinstance(stmt.value.args[0], ast.List)
                                and len(stmt.value.args[0].elts) == 1
                                and isinstance(stmt.value.args[0].elts[0], ast.Name)
                                and stmt.value.args[0].elts[0].id == "__file__"
                            ):
                                pass  # Correct format
                            else:
                                issues.append("pytest.main() should be called with [__file__] only")

    if not has_main_block:
        issues.append("Missing 'if __name__ == \"__main__\":' block")
    elif not has_pytest_main:
        issues.append("Missing 'pytest.main([__file__])' in main block")

    # Check 3: Should not have shebang line
    if content.startswith("#!/"):
        issues.append("Test files should not have shebang lines")

    # Check 4: Should have proper docstring
    if not (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        issues.append("File should start with a docstring")

    return issues


def main() -> int:
    """Main function to check test file consistency."""
    if len(sys.argv) < 2:
        print("Usage: python check_test_consistency.py <test_file_path> [test_file_path ...]")
        return 1

    all_issues = []

    for file_path_str in sys.argv[1:]:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            return 1

        # Check if it's a test file (in tests directory and ends with .py)
        if not (file_path.parent.name == "tests" and file_path.name.endswith(".py")):
            print(f"Skipping {file_path} (not a test file)")
            continue

        issues = check_test_file_consistency(file_path)

        if issues:
            print(f"Issues in {file_path}:")
            for issue in issues:
                print(f"  - {issue}")
            all_issues.extend(issues)
        else:
            print(f"✓ {file_path} passes consistency checks")

    if all_issues:
        print(f"\nFound {len(all_issues)} total issues across test files")
        return 1

    print("\nAll test files pass consistency checks!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
