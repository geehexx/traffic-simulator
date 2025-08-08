"""Dulwich-based Git adapter for MCP server."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

from dulwich import porcelain
from dulwich.repo import Repo

from .schemas import GitCommit, GitCommitWorkflow, GitDiff, GitStatus, GitSync


class GitAdapter:
    """Git operations using Dulwich library."""

    def __init__(self, repo_path: Path):
        """Initialize Git adapter with repository path."""
        self.repo_path = repo_path
        self.repo = Repo(str(repo_path))

    def get_status(self) -> GitStatus:
        """Get current repository status."""
        try:
            # Get current branch
            head_ref = self.repo.refs.read_ref(b"HEAD")
            if head_ref:
                branch = head_ref.decode()
                if branch.startswith("refs/heads/"):
                    branch = branch[11:]  # Remove "refs/heads/" prefix
                else:
                    branch = "main"  # Default branch
            else:
                branch = "main"

            # Get working tree status
            status = porcelain.status(self.repo)

            # Handle the status object properly
            staged_files = []
            unstaged_files = []
            untracked_files = []

            # Extract staged files from the dict structure
            if hasattr(status, "staged") and status.staged:
                for category, files in status.staged.items():
                    if files:  # Only add non-empty categories
                        staged_files.extend(
                            [f.decode() if isinstance(f, bytes) else f for f in files]
                        )

            # Extract unstaged files
            if hasattr(status, "unstaged") and status.unstaged:
                unstaged_files = [
                    f.decode() if isinstance(f, bytes) else f for f in status.unstaged
                ]

            # Extract untracked files
            if hasattr(status, "untracked") and status.untracked:
                untracked_files = [
                    f.decode() if isinstance(f, bytes) else f for f in status.untracked
                ]

            # Check if working tree is clean
            clean = not staged_files and not unstaged_files and not untracked_files

            # Get ahead/behind info (simplified - would need remote tracking)
            ahead = 0
            behind = 0

            return GitStatus(
                branch=branch,
                ahead=ahead,
                behind=behind,
                staged_files=staged_files,
                unstaged_files=unstaged_files,
                untracked_files=untracked_files,
                clean=clean,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get git status: {e}")

    def get_diff(self, paths: Optional[List[str]] = None, staged: bool = False) -> GitDiff:
        """Get diff for specified paths or all changes."""
        try:
            # Get current commit
            try:
                current_commit = self.repo.head()
            except Exception:
                current_commit = None

            if staged and current_commit:
                # Get staged changes (compare with parent)
                if current_commit.parents:
                    parent_commit = self.repo[current_commit.parents[0]]
                    diff_text = porcelain.diff_tree(
                        self.repo, parent_commit.tree, current_commit.tree
                    )
                else:
                    # First commit, compare with empty tree
                    diff_text = porcelain.diff_tree(self.repo, None, current_commit.tree)
            else:
                # Get working tree changes
                if current_commit:
                    diff_text = porcelain.diff_tree(self.repo, current_commit.tree, None)
                else:
                    # No commits yet, show all files
                    diff_text = porcelain.diff_tree(self.repo, None, None)

            # Handle case where diff_text is None
            if diff_text is None:
                diff_text = ""

            # Parse diff for file changes
            file_changes = {}
            lines = diff_text.split("\n")
            for line in lines:
                if line.startswith("diff --git"):
                    # Extract filename from diff header
                    parts = line.split()
                    if len(parts) >= 4:
                        filename = parts[2][2:]  # Remove 'a/' prefix
                        file_changes[filename] = (
                            0  # Simplified - would need to count actual changes
                        )

            return GitDiff(
                diff_text=diff_text,
                file_changes=file_changes,
                stats={"files_changed": len(file_changes)},
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get git diff: {e}")

    def stage_files(self, paths: List[str]) -> List[str]:
        """Stage files for commit."""
        try:
            staged_files = []
            for path in paths:
                porcelain.add(self.repo, [path])
                staged_files.append(path)
            return staged_files
        except Exception as e:
            raise RuntimeError(f"Failed to stage files: {e}")

    def unstage_files(self, paths: List[str]) -> List[str]:
        """Unstage files."""
        try:
            unstaged_files = []
            for path in paths:
                # Reset specific files from index
                subprocess.run(
                    ["git", "reset", "HEAD", "--", path],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True,
                )
                unstaged_files.append(path)
            return unstaged_files
        except Exception as e:
            raise RuntimeError(f"Failed to unstage files: {e}")

    def commit_changes(self, message: str, signoff: bool = False) -> GitCommit:
        """Commit staged changes."""
        try:
            # Create commit
            commit_id = porcelain.commit(self.repo, message.encode())

            # Get commit info
            commit_obj = self.repo[commit_id]
            author = commit_obj.author.decode()
            timestamp = commit_obj.commit_time

            # Get files changed in this commit
            files_changed = []
            if commit_obj.parents:
                # Compare with parent commit
                parent_commit = self.repo[commit_obj.parents[0]]
                try:
                    for change in self.repo.object_store.tree_changes(
                        parent_commit.tree, commit_obj.tree
                    ):
                        files_changed.append(
                            change.path.decode() if isinstance(change.path, bytes) else change.path
                        )
                except Exception:
                    # Fallback: try to get files from the commit message or status
                    pass

            return GitCommit(
                commit_hash=commit_id.decode(),
                message=message,
                author=author,
                timestamp=str(timestamp),
                files_changed=files_changed,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to commit changes: {e}")

    def sync_repository(
        self, pull_first: bool = True, push_after: bool = True, rebase: bool = False
    ) -> GitSync:
        """Sync repository with remote (simplified implementation)."""
        try:
            conflicts = []
            changes_pulled = 0
            changes_pushed = 0

            if pull_first:
                try:
                    # Pull changes
                    if rebase:
                        subprocess.run(
                            ["git", "pull", "--rebase"],
                            cwd=self.repo_path,
                            check=True,
                            capture_output=True,
                        )
                    else:
                        subprocess.run(
                            ["git", "pull"], cwd=self.repo_path, check=True, capture_output=True
                        )
                    changes_pulled = 1  # Simplified - would need to count actual changes
                except subprocess.CalledProcessError as e:
                    if "conflict" in e.stderr.decode().lower():
                        conflicts.append("Merge conflicts detected")
                    return GitSync(
                        pull_success=False,
                        push_success=False,
                        conflicts=conflicts,
                        error=f"Pull failed: {e.stderr.decode()}",
                    )

            if push_after:
                try:
                    # Push changes
                    subprocess.run(
                        ["git", "push"], cwd=self.repo_path, check=True, capture_output=True
                    )
                    changes_pushed = 1  # Simplified - would need to count actual changes
                except subprocess.CalledProcessError as e:
                    return GitSync(
                        pull_success=pull_first,
                        push_success=False,
                        conflicts=conflicts,
                        error=f"Push failed: {e.stderr.decode()}",
                    )

            return GitSync(
                pull_success=pull_first,
                push_success=push_after,
                conflicts=conflicts,
                changes_pulled=changes_pulled,
                changes_pushed=changes_pushed,
            )

        except Exception as e:
            return GitSync(pull_success=False, push_success=False, error=f"Sync failed: {e}")

    def commit_workflow(
        self,
        message: str,
        paths: Optional[List[str]] = None,
        signoff: bool = False,
        preview: bool = True,
    ) -> GitCommitWorkflow:
        """Complete commit workflow with staging and validation."""
        try:
            validation_errors = []
            files_staged = []
            diff_preview = None

            # Stage files if specified
            if paths:
                files_staged = self.stage_files(paths)
            else:
                # Stage all changes
                status = self.get_status()
                all_files = status.staged_files + status.unstaged_files
                if all_files:
                    files_staged = self.stage_files(all_files)

            # Show diff preview if requested
            if preview and files_staged:
                diff_result = self.get_diff(staged=True)
                diff_preview = diff_result.diff_text

            # Validate commit message (basic validation)
            if not message.strip():
                validation_errors.append("Commit message cannot be empty")

            if validation_errors:
                return GitCommitWorkflow(
                    success=False,
                    files_staged=files_staged,
                    diff_preview=diff_preview,
                    validation_errors=validation_errors,
                )

            # Create commit
            commit_result = self.commit_changes(message, signoff)

            return GitCommitWorkflow(
                success=True,
                commit_hash=commit_result.commit_hash,
                files_staged=files_staged,
                diff_preview=diff_preview,
            )

        except Exception as e:
            return GitCommitWorkflow(
                success=False,
                files_staged=files_staged if "files_staged" in locals() else [],
                error=f"Commit workflow failed: {e}",
            )
