#!/usr/bin/env python3
"""Test script to verify YAML prompt loading works correctly."""

import sys
from pathlib import Path

# Add the mcp directory to the path
sys.path.insert(0, str(Path(__file__).parent / "mcp"))

from yaml_prompt_loader import YAMLPromptLoader


def test_yaml_loading():
    """Test YAML prompt loading functionality."""
    print("Testing YAML prompt loading...")

    # Initialize loader
    prompts_dir = Path("prompts")
    loader = YAMLPromptLoader(prompts_dir)

    # Test listing prompts
    print("\n1. Testing list_prompts()...")
    try:
        prompts = loader.list_prompts()
        print(f"Found {len(prompts)} prompts:")
        for prompt in prompts:
            print(f"  - {prompt['prompt_id']} ({prompt['file_type']}) - {prompt['name']}")
    except Exception as e:
        print(f"Error listing prompts: {e}")
        return False

    # Test loading a specific prompt
    print("\n2. Testing load_prompt()...")
    try:
        prompt_data = loader.load_prompt("prompt-wizard")
        print("Loaded prompt-wizard:")
        print(f"  - Name: {prompt_data.get('name')}")
        print(f"  - Description: {prompt_data.get('description', '')[:100]}...")
        print(f"  - Template length: {len(prompt_data.get('template', ''))}")
        print(f"  - Tags: {prompt_data.get('tags', [])}")
    except Exception as e:
        print(f"Error loading prompt: {e}")
        return False

    # Test loading a different prompt
    print("\n3. Testing load_prompt() with generate_docs_v2_2_0...")
    try:
        prompt_data = loader.load_prompt("generate_docs_v2_2_0")
        print("Loaded generate_docs_v2_2_0:")
        print(f"  - Name: {prompt_data.get('name')}")
        print(f"  - Description: {prompt_data.get('description', '')[:100]}...")
        print(f"  - Template length: {len(prompt_data.get('template', ''))}")
        print(f"  - Tags: {prompt_data.get('tags', [])}")
    except Exception as e:
        print(f"Error loading prompt: {e}")
        return False

    print("\n✅ All tests passed! YAML loading is working correctly.")
    return True


if __name__ == "__main__":
    success = test_yaml_loading()
    sys.exit(0 if success else 1)
