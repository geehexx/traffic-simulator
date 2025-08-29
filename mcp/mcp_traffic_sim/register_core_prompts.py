"""Register core prompts for the traffic simulator project."""

from pathlib import Path
from prompt_registry import PromptConfig, PromptRegistry


def register_core_prompts():
    """Register the core prompts for documentation and rules maintenance."""

    # Initialize registry
    registry_path = Path("mcp_registry")
    registry = PromptRegistry(registry_path)

    # Register Documentation Generation Prompt
    docs_prompt = PromptConfig(
        prompt_id="generate_docs",
        name="Generate Documentation",
        description="Generate comprehensive documentation for code changes",
        template="""Generate documentation for the following code changes:

Code Changes:
{code_changes}

Context:
{context}

Requirements:
- Follow the project's documentation standards
- Include clear explanations and examples
- Maintain consistency with existing documentation
- Use proper markdown formatting
- Include relevant code snippets and diagrams where appropriate

Output should be well-structured documentation that enhances understanding and maintainability.""",
        input_schema={
            "type": "object",
            "properties": {
                "code_changes": {
                    "type": "string",
                    "description": "Description of the code changes made",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the changes",
                },
            },
            "required": ["code_changes"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "documentation": {
                    "type": "string",
                    "description": "Generated documentation content",
                },
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of documentation sections created",
                },
            },
            "required": ["documentation"],
        },
        tags=["docs", "documentation", "maintenance"],
        metadata={"category": "documentation", "priority": "high", "version_history": ["1.0.0"]},
    )

    # Register Rules Generation Prompt
    rules_prompt = PromptConfig(
        prompt_id="generate_rules",
        name="Generate Rules",
        description="Generate Cursor rules for code patterns and guidelines",
        template="""Generate Cursor rules for the following patterns:

Patterns:
{patterns}

Context:
{context}

Requirements:
- Follow the project's rule generation standards
- Include clear, actionable guidelines
- Maintain consistency with existing rules
- Use proper rule formatting
- Include examples and counter-examples where appropriate

Output should be well-structured rules that guide development practices.""",
        input_schema={
            "type": "object",
            "properties": {
                "patterns": {
                    "type": "string",
                    "description": "Description of the patterns to create rules for",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the patterns",
                },
            },
            "required": ["patterns"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "rules": {"type": "string", "description": "Generated rules content"},
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of rule categories created",
                },
            },
            "required": ["rules"],
        },
        tags=["rules", "guidelines", "maintenance"],
        metadata={"category": "rules", "priority": "high", "version_history": ["1.0.0"]},
    )

    # Register Hybrid Maintenance Prompt
    hybrid_prompt = PromptConfig(
        prompt_id="hybrid_maintenance",
        name="Hybrid Maintenance",
        description="Combined documentation and rules maintenance with mode selection",
        template="""Perform maintenance task in {mode} mode:

Task: {task}
Context: {context}

Mode Options:
- docs: Focus on documentation generation
- rules: Focus on rules generation
- hybrid: Balance both documentation and rules

Requirements:
- Follow the project's standards for the selected mode
- Maintain consistency with existing content
- Use proper formatting and structure
- Include relevant examples and explanations

Output should be well-structured content that enhances the project's maintainability.""",
        input_schema={
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["docs", "rules", "hybrid"],
                    "description": "Maintenance mode to use",
                },
                "task": {"type": "string", "description": "Description of the maintenance task"},
                "context": {"type": "string", "description": "Additional context for the task"},
            },
            "required": ["mode", "task"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Generated content"},
                "mode_used": {
                    "type": "string",
                    "description": "The mode that was used for generation",
                },
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of content sections created",
                },
            },
            "required": ["content", "mode_used"],
        },
        tags=["hybrid", "maintenance", "docs", "rules"],
        metadata={"category": "hybrid", "priority": "high", "version_history": ["1.0.0"]},
    )

    # Register all prompts
    registry.register_prompt(docs_prompt)
    registry.register_prompt(rules_prompt)
    registry.register_prompt(hybrid_prompt)

    print("✅ Core prompts registered successfully!")
    print("📋 Registered prompts:")
    for prompt in registry.list_prompts():
        print(f"  - {prompt.prompt_id}: {prompt.name}")

    return registry


if __name__ == "__main__":
    register_core_prompts()
