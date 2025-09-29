#!/usr/bin/env python3
"""
Convert JSON prompt files to YAML format with front matter for better readability.
The YAML format will use front matter for structured components and the main content
for the human-readable template.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any
import re


def clean_template_text(template: str) -> str:
    """Clean and format template text for better readability in YAML."""
    # Expand escaped characters
    template = template.replace("\\n", "\n")
    template = template.replace("\\t", "\t")
    template = template.replace('\\"', '"')
    template = template.replace("\\'", "'")

    # Clean up any remaining escape sequences
    template = re.sub(r"\\(.)", r"\1", template)

    return template


def extract_front_matter(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured data for YAML front matter."""
    front_matter = {}

    # Core metadata
    if "name" in data:
        front_matter["name"] = data["name"]
    if "description" in data:
        front_matter["description"] = data["description"]
    if "version" in data:
        front_matter["version"] = data["version"]
    if "active" in data:
        front_matter["active"] = data["active"]
    if "tags" in data:
        front_matter["tags"] = data["tags"]
    if "prompt_id" in data:
        front_matter["prompt_id"] = data["prompt_id"]

    # Schema information
    if "input_schema" in data:
        front_matter["input_schema"] = data["input_schema"]
    if "output_schema" in data:
        front_matter["output_schema"] = data["output_schema"]

    # Additional metadata
    if "metadata" in data:
        front_matter["metadata"] = data["metadata"]
    if "last_modified" in data:
        front_matter["last_modified"] = data["last_modified"]

    return front_matter


def convert_json_to_yaml(json_file_path: Path, output_dir: Path) -> None:
    """Convert a single JSON prompt file to YAML format."""
    print(f"Converting {json_file_path.name}...")

    # Read JSON file
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract front matter (structured data)
    front_matter = extract_front_matter(data)

    # Extract template (human-readable content)
    template = data.get("template", "")
    if template:
        template = clean_template_text(template)

    # Create YAML content
    yaml_content = []

    # Add front matter
    if front_matter:
        yaml_content.append("---")
        yaml_content.append(yaml.dump(front_matter, default_flow_style=False, sort_keys=False))
        yaml_content.append("---")
        yaml_content.append("")

    # Add template content
    if template:
        yaml_content.append(template)

    # Write YAML file
    output_file = output_dir / f"{json_file_path.stem}.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_content))

    print(f"  -> Created {output_file.name}")


def convert_manifest_to_yaml(json_file_path: Path, output_dir: Path) -> None:
    """Convert manifest.json to YAML format."""
    print(f"Converting {json_file_path.name}...")

    # Read JSON file
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create YAML content
    yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False, indent=2)

    # Write YAML file
    output_file = output_dir / f"{json_file_path.stem}.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"  -> Created {output_file.name}")


def main():
    """Convert all JSON prompt files to YAML format."""
    # Set up paths
    prompts_dir = Path("/home/gxx/projects/traffic-simulator/prompts")
    output_dir = Path("/home/gxx/projects/traffic-simulator/prompts_yaml")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("Converting JSON prompt files to YAML format...")
    print(f"Input directory: {prompts_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Convert each JSON file
    for json_file in prompts_dir.glob("*.json"):
        if json_file.name == "manifest.json":
            convert_manifest_to_yaml(json_file, output_dir)
        else:
            convert_json_to_yaml(json_file, output_dir)

    print()
    print("Conversion complete!")
    print(f"YAML files created in: {output_dir}")


if __name__ == "__main__":
    main()
