#!/usr/bin/env python3
"""Test script to verify MCP server can handle YAML prompts."""

import sys
from pathlib import Path

# Add the mcp directory to the path
sys.path.insert(0, str(Path(__file__).parent / "mcp"))

# Import the MCP server functions
from fastmcp_production_server import list_prompts, get_prompt, execute_prompt
import json


def test_mcp_yaml_integration():
    """Test MCP server integration with YAML prompts."""
    print("Testing MCP server with YAML prompts...")

    # Test 1: List prompts
    print("\n1. Testing list_prompts()...")
    try:
        result = list_prompts()
        data = json.loads(result)
        if data.get("success"):
            prompts = data.get("prompts", [])
            print(f"✅ Found {len(prompts)} prompts:")
            for prompt in prompts:
                print(f"  - {prompt['prompt_id']} - {prompt['name']}")
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error listing prompts: {e}")
        return False

    # Test 2: Get specific prompt
    print("\n2. Testing get_prompt()...")
    try:
        result = get_prompt("prompt-wizard")
        data = json.loads(result)
        if data.get("success"):
            prompt = data.get("prompt", {})
            print(f"✅ Loaded prompt: {prompt.get('name')}")
            print(f"  - Description: {prompt.get('description', '')[:100]}...")
            print(f"  - Template length: {len(prompt.get('template', ''))}")
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error getting prompt: {e}")
        return False

    # Test 3: Execute prompt
    print("\n3. Testing execute_prompt()...")
    try:
        input_data = {
            "user_goal": "I want to create a new prompt",
            "current_context": "I'm new to prompt management",
            "preferred_approach": "step-by-step guidance",
        }
        result = execute_prompt("prompt-wizard", input_data)
        data = json.loads(result)
        if data.get("success"):
            print("✅ Executed prompt successfully")
            print(f"  - Template length: {len(data.get('executed_template', ''))}")
            print(f"  - Metadata: {data.get('prompt_metadata', {})}")
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error executing prompt: {e}")
        return False

    print("\n✅ All MCP server tests passed! YAML integration is working correctly.")
    return True


if __name__ == "__main__":
    success = test_mcp_yaml_integration()
    sys.exit(0 if success else 1)
