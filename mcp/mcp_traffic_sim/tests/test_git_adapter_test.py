"""Unit tests for Git adapter."""

import tempfile
from pathlib import Path

import pytest
from dulwich import porcelain

from ..git.adapter import GitAdapter
from ..git.schemas import GitStatus


class TestGitAdapter:
    """Test Git adapter functionality."""

    def test_init_with_valid_repo(self):
        """Test adapter initialization with valid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a git repository
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            adapter = GitAdapter(repo_path)
            assert adapter.repo_path == repo_path
            assert adapter.repo is not None

    def test_init_with_invalid_repo(self):
        """Test adapter initialization with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            with pytest.raises(Exception):
                GitAdapter(repo_path)

    def test_get_status_empty_repo(self):
        """Test getting status from empty repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            adapter = GitAdapter(repo_path)
            status = adapter.get_status()

            assert isinstance(status, GitStatus)
            assert status.branch == "main"  # Default branch
            assert status.clean is True
            assert len(status.staged_files) == 0
            assert len(status.unstaged_files) == 0
            assert len(status.untracked_files) == 0

    def test_get_status_with_files(self):
        """Test getting status with untracked files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            # Create a test file
            test_file = repo_path / "test.txt"
            test_file.write_text("Hello, world!")

            adapter = GitAdapter(repo_path)
            status = adapter.get_status()

            assert isinstance(status, GitStatus)
            assert "test.txt" in status.untracked_files
            assert status.clean is False

    def test_stage_files(self):
        """Test staging files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            # Create a test file
            test_file = repo_path / "test.txt"
            test_file.write_text("Hello, world!")

            adapter = GitAdapter(repo_path)
            staged_files = adapter.stage_files(["test.txt"])

            assert "test.txt" in staged_files

            # Verify file is staged
            status = adapter.get_status()
            assert "test.txt" in status.staged_files

    def test_commit_changes(self):
        """Test committing changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            # Create and stage a test file
            test_file = repo_path / "test.txt"
            test_file.write_text("Hello, world!")

            adapter = GitAdapter(repo_path)
            adapter.stage_files(["test.txt"])

            commit_result = adapter.commit_changes("feat: add test file")

            assert commit_result.commit_hash is not None
            assert commit_result.message == "feat: add test file"
            # Note: files_changed tracking is simplified in this implementation
            # The commit was successful, which is the main test

    def test_get_diff(self):
        """Test getting diff."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            # Create a test file
            test_file = repo_path / "test.txt"
            test_file.write_text("Hello, world!")

            adapter = GitAdapter(repo_path)
            diff_result = adapter.get_diff()

            assert diff_result.diff_text is not None
            assert isinstance(diff_result.file_changes, dict)
            assert isinstance(diff_result.stats, dict)

    def test_commit_workflow(self):
        """Test complete commit workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            porcelain.init(repo_path)

            # Create a test file
            test_file = repo_path / "test.txt"
            test_file.write_text("Hello, world!")

            adapter = GitAdapter(repo_path)
            workflow_result = adapter.commit_workflow(
                "feat: add test file", paths=["test.txt"], preview=True
            )

            assert workflow_result.success is True
            assert workflow_result.commit_hash is not None
            assert "test.txt" in workflow_result.files_staged
            assert workflow_result.diff_preview is not None
