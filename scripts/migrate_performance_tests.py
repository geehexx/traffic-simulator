#!/usr/bin/env python3
"""
Performance Test Migration Script

This script helps migrate from the old individual performance test files
to the new unified benchmarking framework.

Replaces:
- tests/performance_test.py
- tests/performance_smoke_test.py
- tests/performance_highperf_test.py

With:
- tests/benchmark_tests.py (unified framework)
- scripts/benchmarking_framework.py (main framework)
- scripts/external_tools.py (external tool integration)
- scripts/advanced_profiling.py (advanced analysis)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, Any


class PerformanceTestMigrator:
    """Migrate performance tests to unified framework."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.backup_dir = Path("backup_performance_tests")
        self.old_test_files = [
            "tests/performance_test.py",
            "tests/performance_smoke_test.py",
            "tests/performance_highperf_test.py",
        ]
        self.new_test_file = "tests/benchmark_tests.py"
        self.new_scripts = [
            "scripts/benchmarking_framework.py",
            "scripts/external_tools.py",
            "scripts/advanced_profiling.py",
        ]

    def check_migration_readiness(self) -> Dict[str, Any]:
        """Check if migration can proceed safely."""
        status = {
            "can_migrate": True,
            "issues": [],
            "warnings": [],
            "old_files_exist": [],
            "new_files_exist": [],
        }

        # Check old files
        for file_path in self.old_test_files:
            if Path(file_path).exists():
                status["old_files_exist"].append(file_path)
            else:
                status["warnings"].append(f"Old test file not found: {file_path}")

        # Check new files
        for file_path in self.new_scripts:
            if Path(file_path).exists():
                status["new_files_exist"].append(file_path)
            else:
                status["issues"].append(f"New script not found: {file_path}")
                status["can_migrate"] = False

        if not Path(self.new_test_file).exists():
            status["issues"].append(f"New test file not found: {self.new_test_file}")
            status["can_migrate"] = False

        return status

    def create_backup(self) -> bool:
        """Create backup of old test files."""
        if self.dry_run:
            print("DRY RUN: Would create backup directory")
            return True

        try:
            self.backup_dir.mkdir(exist_ok=True)

            for file_path in self.old_test_files:
                if Path(file_path).exists():
                    backup_path = self.backup_dir / Path(file_path).name
                    shutil.copy2(file_path, backup_path)
                    print(f"Backed up {file_path} to {backup_path}")

            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def migrate_test_files(self) -> bool:
        """Migrate old test files to new framework."""
        if self.dry_run:
            print("DRY RUN: Would migrate test files")
            return True

        try:
            # Remove old test files
            for file_path in self.old_test_files:
                if Path(file_path).exists():
                    Path(file_path).unlink()
                    print(f"Removed old test file: {file_path}")

            # Verify new test file exists
            if not Path(self.new_test_file).exists():
                print(f"Error: New test file not found: {self.new_test_file}")
                return False

            print(f"Migration completed. New test file: {self.new_test_file}")
            return True

        except Exception as e:
            print(f"Error during migration: {e}")
            return False

    def update_ci_configuration(self) -> bool:
        """Update CI configuration to use new framework."""
        if self.dry_run:
            print("DRY RUN: Would update CI configuration")
            return True

        # Check for GitHub Actions workflow
        workflow_file = Path(".github/workflows/ci.yml")
        if workflow_file.exists():
            print("Found GitHub Actions workflow. Manual update may be required.")
            print("Consider updating test commands to use the new benchmarking framework.")

        # Check for other CI files
        ci_files = [
            ".github/workflows/benchmark.yml",
            ".github/workflows/performance.yml",
            "azure-pipelines.yml",
            ".travis.yml",
            "Jenkinsfile",
        ]

        for ci_file in ci_files:
            if Path(ci_file).exists():
                print(f"Found CI file: {ci_file}. Manual update may be required.")

        return True

    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate migration report."""
        status = self.check_migration_readiness()

        report = {
            "migration_status": "ready" if status["can_migrate"] else "not_ready",
            "old_files": status["old_files_exist"],
            "new_files": status["new_files_exist"],
            "issues": status["issues"],
            "warnings": status["warnings"],
            "recommendations": [],
        }

        if status["can_migrate"]:
            report["recommendations"].extend(
                [
                    "Migration can proceed safely",
                    "Old test files will be backed up",
                    "New unified framework provides enhanced capabilities",
                    "Consider running tests after migration to verify functionality",
                ]
            )
        else:
            report["recommendations"].extend(
                [
                    "Resolve issues before migration",
                    "Ensure all new framework files are present",
                    "Verify new test file is properly configured",
                ]
            )

        return report

    def run_migration(self) -> bool:
        """Run the complete migration process."""
        print("=== Performance Test Migration ===")

        # Check readiness
        status = self.check_migration_readiness()
        if not status["can_migrate"]:
            print("❌ Migration cannot proceed due to issues:")
            for issue in status["issues"]:
                print(f"  - {issue}")
            return False

        print("✅ Migration readiness check passed")

        # Create backup
        if not self.create_backup():
            print("❌ Failed to create backup")
            return False

        print("✅ Backup created successfully")

        # Migrate files
        if not self.migrate_test_files():
            print("❌ Failed to migrate test files")
            return False

        print("✅ Test files migrated successfully")

        # Update CI configuration
        if not self.update_ci_configuration():
            print("⚠️  CI configuration update may be required")

        print("✅ Migration completed successfully")
        return True


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(description="Migrate performance tests to unified framework")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )
    parser.add_argument("--check-only", action="store_true", help="Only check migration readiness")
    parser.add_argument(
        "--force", action="store_true", help="Force migration even if issues are detected"
    )

    args = parser.parse_args()

    migrator = PerformanceTestMigrator(dry_run=args.dry_run)

    if args.check_only:
        # Only check readiness
        report = migrator.generate_migration_report()

        print("\n=== Migration Readiness Report ===")
        print(f"Status: {report['migration_status']}")

        if report["old_files"]:
            print(f"\nOld test files found: {len(report['old_files'])}")
            for file in report["old_files"]:
                print(f"  - {file}")

        if report["new_files"]:
            print(f"\nNew framework files found: {len(report['new_files'])}")
            for file in report["new_files"]:
                print(f"  - {file}")

        if report["issues"]:
            print(f"\nIssues ({len(report['issues'])}):")
            for issue in report["issues"]:
                print(f"  ❌ {issue}")

        if report["warnings"]:
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warning in report["warnings"]:
                print(f"  ⚠️  {warning}")

        if report["recommendations"]:
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  💡 {rec}")

        return 0 if report["migration_status"] == "ready" else 1

    else:
        # Run migration
        success = migrator.run_migration()

        if success:
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print(
                "1. Run the new benchmark tests: uv run python -m pytest tests/benchmark_tests.py -v"
            )
            print(
                "2. Test the benchmarking framework: uv run python scripts/benchmarking_framework.py --mode=benchmark"
            )
            print("3. Update any CI/CD configurations if needed")
            print("4. Remove backup files when confident in the migration")
            return 0
        else:
            print("\n❌ Migration failed. Check the issues above.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
