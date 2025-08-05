#!/usr/bin/env python3
"""Validate Cursor rules structure and compliance."""

import re
import yaml
import sys
from pathlib import Path
from typing import Dict, Any


def validate_rule_file(file_path: Path) -> Dict[str, Any]:
    """Validate a single rule file."""
    errors = []
    warnings = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        return {"errors": errors, "warnings": warnings}

    # Check frontmatter
    if not content.startswith("---"):
        errors.append("Missing frontmatter")
        return {"errors": errors, "warnings": warnings}

    # Extract frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return {"errors": errors, "warnings": warnings}

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return {"errors": errors, "warnings": warnings}

    # Validate required fields
    required_fields = ["globs", "description", "alwaysApply"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Validate globs
    if "globs" in frontmatter:
        globs = frontmatter["globs"]
        if isinstance(globs, str):
            globs = [globs]
        for glob in globs:
            if not glob or not isinstance(glob, str):
                errors.append("Invalid glob pattern")

    # Validate alwaysApply
    if "alwaysApply" in frontmatter:
        if not isinstance(frontmatter["alwaysApply"], bool):
            errors.append("alwaysApply must be boolean")

    # Check for global rules limit
    if frontmatter.get("alwaysApply", False):
        if "globs" in frontmatter:
            globs = frontmatter["globs"]
            if isinstance(globs, str):
                globs = [globs]
            if any(glob == "**" for glob in globs):
                warnings.append("Global rule detected - limit to 5 total")

    # Check token count (rough estimate)
    content_length = len(content)
    if content_length > 2000:  # Rough token estimate
        warnings.append(f"Rule content may exceed token limit (~{content_length} chars)")

    return {"errors": errors, "warnings": warnings}


def validate_all_rules() -> Dict[str, Any]:
    """Validate all rule files."""
    rules_dir = Path(".cursor/rules")
    if not rules_dir.exists():
        return {"errors": ["Rules directory not found"], "warnings": []}

    all_errors = []
    all_warnings = []
    global_rules_count = 0

    for rule_file in rules_dir.glob("*.mdc"):
        result = validate_rule_file(rule_file)
        all_errors.extend(result["errors"])
        all_warnings.extend(result["warnings"])

        # Count global rules
        try:
            with open(rule_file, "r", encoding="utf-8") as f:
                content = f.read()
            frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if frontmatter_match:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if frontmatter.get("alwaysApply", False):
                    globs = frontmatter.get("globs", [])
                    if isinstance(globs, str):
                        globs = [globs]
                    if any(glob == "**" for glob in globs):
                        global_rules_count += 1
        except Exception:
            pass

    # Check global rules limit
    if global_rules_count > 5:
        all_errors.append(f"Too many global rules: {global_rules_count} (max 5)")

    return {"errors": all_errors, "warnings": all_warnings}


def main():
    """Main entry point for rules validation."""
    result = validate_all_rules()

    if result["errors"]:
        print("❌ Rules validation failed:")
        for error in result["errors"]:
            print(f"  - {error}")
        sys.exit(1)
    elif result["warnings"]:
        print("⚠️  Rules validation warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
        print("✅ Rules validation passed with warnings")
    else:
        print("✅ All rules validation passed")


if __name__ == "__main__":
    main()
