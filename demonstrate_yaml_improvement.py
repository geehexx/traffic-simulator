#!/usr/bin/env python3
"""Demonstrate the improvement in readability from JSON to YAML format."""

from pathlib import Path


def demonstrate_improvement():
    """Show the difference between JSON and YAML formats."""
    print("🎯 YAML vs JSON Prompt Format Comparison")
    print("=" * 60)

    # Read both formats
    json_file = Path("prompts/prompt-wizard.json")
    yaml_file = Path("prompts/prompt-wizard.yaml")

    if json_file.exists() and yaml_file.exists():
        print("\n📄 JSON Format (Original):")
        print("-" * 40)
        with open(json_file, "r") as f:
            json_content = f.read()
        print(json_content[:500] + "..." if len(json_content) > 500 else json_content)

        print("\n📄 YAML Format (Improved):")
        print("-" * 40)
        with open(yaml_file, "r") as f:
            yaml_content = f.read()
        print(yaml_content[:500] + "..." if len(yaml_content) > 500 else yaml_content)

        print("\n✨ Key Improvements:")
        print("1. 🎨 Front matter separates metadata from content")
        print("2. 📖 Template content is much more readable")
        print("3. 🔧 YAML syntax is more human-friendly")
        print("4. 📝 Better structure for editing and maintenance")
        print("5. 🚀 Easier to version control and diff")

        # Show size comparison
        json_size = len(json_content)
        yaml_size = len(yaml_content)
        print("\n📊 File Size Comparison:")
        print(f"   JSON: {json_size:,} characters")
        print(f"   YAML: {yaml_size:,} characters")
        print(f"   Difference: {yaml_size - json_size:+,} characters")

    else:
        print("❌ Could not find both JSON and YAML files for comparison")


if __name__ == "__main__":
    demonstrate_improvement()
