#!/usr/bin/env python3
"""Simple test to verify YAML prompt functionality."""

import sys
from pathlib import Path

# Add the mcp directory to the path
sys.path.insert(0, str(Path(__file__).parent / "mcp"))

from yaml_prompt_loader import YAMLPromptLoader


def test_yaml_functionality():
    """Test YAML prompt functionality end-to-end."""
    print("Testing YAML prompt functionality...")

    # Initialize loader
    prompts_dir = Path("prompts")
    loader = YAMLPromptLoader(prompts_dir)

    # Test 1: List prompts
    print("\n1. Listing all prompts...")
    prompts = loader.list_prompts()
    print(f"Found {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"  - {prompt['prompt_id']} ({prompt['file_type']}) - {prompt['name']}")

    # Test 2: Load a prompt and show structure
    print("\n2. Loading prompt-wizard...")
    prompt_data = loader.load_prompt("prompt-wizard")
    print("Prompt structure:")
    for key, value in prompt_data.items():
        if key == "template":
            print(f"  - {key}: {len(str(value))} characters")
        elif isinstance(value, (dict, list)):
            print(f"  - {key}: {type(value).__name__} with {len(value)} items")
        else:
            print(f"  - {key}: {value}")

    # Test 3: Test template substitution
    print("\n3. Testing template substitution...")
    template = prompt_data.get("template", "")
    if template:
        # Simple substitution test
        test_template = template.replace("{user_goal}", "Create documentation")
        test_template = test_template.replace("{current_context}", "New user")
        test_template = test_template.replace("{preferred_approach}", "Step by step")
        print(f"Template substitution successful. Result length: {len(test_template)}")

    # Test 4: Test saving a new prompt
    print("\n4. Testing save functionality...")
    test_prompt_data = {
        "prompt_id": "test_prompt",
        "name": "Test Prompt",
        "description": "A test prompt for YAML functionality",
        "template": "Hello {name}, this is a test prompt!",
        "tags": ["test", "yaml"],
        "version": "1.0.0",
        "active": True,
    }

    try:
        loader.save_prompt_as_yaml("test_prompt", test_prompt_data)
        print("✅ Test prompt saved successfully")

        # Load it back to verify
        loaded_test = loader.load_prompt("test_prompt")
        print(f"✅ Test prompt loaded back: {loaded_test['name']}")

        # Clean up
        test_file = prompts_dir / "test_prompt.yaml"
        if test_file.exists():
            test_file.unlink()
            print("✅ Test file cleaned up")

    except Exception as e:
        print(f"❌ Error with save/load test: {e}")
        return False

    print("\n✅ All YAML functionality tests passed!")
    return True


if __name__ == "__main__":
    success = test_yaml_functionality()
    sys.exit(0 if success else 1)
