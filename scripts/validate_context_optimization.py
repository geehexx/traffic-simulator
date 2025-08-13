#!/usr/bin/env python3
"""
Context Optimization Validation Script

Validates Cursor rules and documentation for context optimization compliance.
Implements quality gates for context management and AI-friendly structure.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of context optimization validation."""

    rule_name: str
    token_count: int
    reference_count: int
    has_semantic_anchors: bool
    has_ai_friendly_structure: bool
    broken_links: List[str]
    duplicate_content: List[str]
    efficiency_score: float
    violations: List[str]


class ContextOptimizationValidator:
    """Validates context optimization compliance for Cursor rules."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.rules_dir = project_root / ".cursor" / "rules"
        self.docs_dir = project_root / "docs"
        self.config_dir = project_root / "config"
        self.quality_gates = self._load_quality_gates()

    def _load_quality_gates(self) -> Dict[str, Any]:
        """Load quality gates configuration."""
        gates_file = self.config_dir / "quality_gates.yaml"
        if gates_file.exists():
            with open(gates_file, "r") as f:
                return yaml.safe_load(f)
        return {}

    def _count_tokens(self, content: str) -> int:
        """Estimate token count for content."""
        # Simple token estimation: words + punctuation
        words = len(content.split())
        punctuation = len(re.findall(r"[^\w\s]", content))
        return words + punctuation

    def _extract_references(self, content: str) -> List[str]:
        """Extract all mdc: references from content."""
        pattern = r"mdc:([^\s\)]+)"
        return re.findall(pattern, content)

    def _check_semantic_anchors(self, content: str) -> bool:
        """Check if content has semantic anchors."""
        return bool(re.search(r"\{#id:[^}]+\}", content))

    def _check_ai_friendly_structure(self, content: str) -> bool:
        """Check if content has AI-friendly structure."""
        has_qa_format = bool(re.search(r"Q:|A:|Question|Answer", content, re.IGNORECASE))
        has_decision_tree = bool(re.search(r"if|then|when|if.*then", content, re.IGNORECASE))
        has_structured_sections = bool(re.search(r"## .*\{#id:", content))
        return has_qa_format or has_decision_tree or has_structured_sections

    def _validate_links(self, content: str) -> List[str]:
        """Validate mdc: links and return broken ones."""
        broken_links = []
        references = self._extract_references(content)

        for ref in references:
            if ref.startswith("docs/"):
                doc_path = self.docs_dir / ref[5:]  # Remove 'docs/' prefix
                if not doc_path.exists():
                    broken_links.append(ref)
            elif ref.startswith("src/"):
                src_path = self.project_root / ref
                if not src_path.exists():
                    broken_links.append(ref)
            elif ref.startswith("config/"):
                config_path = self.project_root / ref
                if not config_path.exists():
                    broken_links.append(ref)

        return broken_links

    def _detect_duplicate_content(self, content: str, other_contents: List[str]) -> List[str]:
        """Detect duplicate content patterns."""
        duplicates = []
        content_lines = content.split("\n")

        for other_content in other_contents:
            other_lines = other_content.split("\n")
            common_lines = set(content_lines) & set(other_lines)
            if len(common_lines) > 5:  # Threshold for duplicate detection
                duplicates.extend(common_lines)

        return duplicates

    def _calculate_efficiency_score(self, content: str, token_count: int) -> float:
        """Calculate token efficiency score."""
        if token_count == 0:
            return 0.0

        # Count meaningful content (non-whitespace, non-markdown)
        meaningful_content = re.sub(r"[#\*\-\s]+", "", content)
        meaningful_tokens = len(meaningful_content.split())

        return meaningful_tokens / token_count if token_count > 0 else 0.0

    def validate_rule(self, rule_file: Path) -> ValidationResult:
        """Validate a single rule file."""
        with open(rule_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract rule content (skip frontmatter)
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        token_count = self._count_tokens(content)
        reference_count = len(self._extract_references(content))
        has_semantic_anchors = self._check_semantic_anchors(content)
        has_ai_friendly_structure = self._check_ai_friendly_structure(content)
        broken_links = self._validate_links(content)

        # Load other rule contents for duplicate detection
        other_contents = []
        for other_rule in self.rules_dir.glob("*.mdc"):
            if other_rule != rule_file:
                with open(other_rule, "r", encoding="utf-8") as f:
                    other_content = f.read()
                    if other_content.startswith("---"):
                        parts = other_content.split("---", 2)
                        if len(parts) >= 3:
                            other_content = parts[2].strip()
                    other_contents.append(other_content)

        duplicate_content = self._detect_duplicate_content(content, other_contents)
        efficiency_score = self._calculate_efficiency_score(content, token_count)

        # Check violations
        violations = []
        context_config = self.quality_gates.get("context_optimization", {})

        max_tokens = context_config.get("max_tokens_per_rule", 500)
        max_references = context_config.get("max_references_per_rule", 5)
        efficiency_threshold = context_config.get("token_efficiency_threshold", 0.8)

        if token_count > max_tokens:
            violations.append(f"Token count {token_count} exceeds limit {max_tokens}")

        if reference_count > max_references:
            violations.append(f"Reference count {reference_count} exceeds limit {max_references}")

        if not has_semantic_anchors and context_config.get("require_semantic_anchors", True):
            violations.append("Missing semantic anchors")

        if not has_ai_friendly_structure and context_config.get(
            "require_ai_friendly_structure", True
        ):
            violations.append("Missing AI-friendly structure")

        if efficiency_score < efficiency_threshold:
            violations.append(
                f"Efficiency score {efficiency_score:.2f} below threshold {efficiency_threshold}"
            )

        return ValidationResult(
            rule_name=rule_file.stem,
            token_count=token_count,
            reference_count=reference_count,
            has_semantic_anchors=has_semantic_anchors,
            has_ai_friendly_structure=has_ai_friendly_structure,
            broken_links=broken_links,
            duplicate_content=duplicate_content,
            efficiency_score=efficiency_score,
            violations=violations,
        )

    def validate_all_rules(self) -> List[ValidationResult]:
        """Validate all rule files."""
        results = []
        for rule_file in self.rules_dir.glob("*.mdc"):
            result = self.validate_rule(rule_file)
            results.append(result)
        return results

    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate validation report."""
        report = ["# Context Optimization Validation Report\n"]

        total_rules = len(results)
        compliant_rules = sum(1 for r in results if not r.violations)
        total_tokens = sum(r.token_count for r in results)
        total_references = sum(r.reference_count for r in results)

        report.append("## Summary")
        report.append(f"- Total Rules: {total_rules}")
        report.append(f"- Compliant Rules: {compliant_rules}")
        report.append(f"- Compliance Rate: {compliant_rules/total_rules*100:.1f}%")
        report.append(f"- Total Tokens: {total_tokens}")
        report.append(f"- Total References: {total_references}")
        report.append("")

        # Violations summary
        all_violations = []
        for result in results:
            all_violations.extend(result.violations)

        if all_violations:
            report.append("## Violations Summary")
            violation_counts = {}
            for violation in all_violations:
                violation_counts[violation] = violation_counts.get(violation, 0) + 1

            for violation, count in sorted(violation_counts.items()):
                report.append(f"- {violation}: {count} rules")
            report.append("")

        # Detailed results
        report.append("## Detailed Results")
        for result in results:
            report.append(f"### {result.rule_name}")
            report.append(f"- Tokens: {result.token_count}")
            report.append(f"- References: {result.reference_count}")
            report.append(f"- Semantic Anchors: {'✓' if result.has_semantic_anchors else '✗'}")
            report.append(
                f"- AI-Friendly Structure: {'✓' if result.has_ai_friendly_structure else '✗'}"
            )
            report.append(f"- Efficiency Score: {result.efficiency_score:.2f}")

            if result.broken_links:
                report.append(f"- Broken Links: {', '.join(result.broken_links)}")

            if result.violations:
                report.append(f"- Violations: {', '.join(result.violations)}")

            report.append("")

        return "\n".join(report)


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    validator = ContextOptimizationValidator(project_root)

    print("Validating context optimization...")
    results = validator.validate_all_rules()

    report = validator.generate_report(results)
    print(report)

    # Save report
    report_file = project_root / "runs" / "quality" / "context_optimization_report.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {report_file}")

    # Exit with error code if violations found
    total_violations = sum(len(r.violations) for r in results)
    if total_violations > 0:
        print(f"\nFound {total_violations} violations. Please fix before committing.")
        exit(1)
    else:
        print("\nAll rules pass context optimization validation!")


if __name__ == "__main__":
    main()
