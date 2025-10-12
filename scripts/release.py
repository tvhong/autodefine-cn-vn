#!/usr/bin/env python3
"""Release script for autodefine-cn-vn."""

import argparse
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Version:
    """Semantic version."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "Version") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: "Version") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __gt__(self, other: "Version") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, other: "Version") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        """Compare versions."""
        if not isinstance(other, Version):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """Parse a semantic version string."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
        )

    def bump_major(self) -> "Version":
        """Bump major version."""
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        """Bump minor version."""
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        """Bump patch version."""
        return Version(self.major, self.minor, self.patch + 1)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Release a new version of autodefine-cn-vn")
    parser.add_argument("version", nargs="?", help="Version to release (e.g., 0.1.2)")
    parser.add_argument("--patch", action="store_true", help="Bump patch version")
    parser.add_argument("--minor", action="store_true", help="Bump minor version")
    parser.add_argument("--major", action="store_true", help="Bump major version")
    parser.add_argument("--skip-ci", action="store_true", help="Skip CI checks")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without doing it"
    )

    args = parser.parse_args()

    # Find pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        print(f"❌ Error: {pyproject_path} not found", file=sys.stderr)
        return 1

    # Determine new version
    current_version = get_current_version(pyproject_path)

    bump_flags = sum([args.patch, args.minor, args.major])
    if args.version and bump_flags > 0:
        print(
            "❌ Error: Cannot specify both explicit version and bump flag",
            file=sys.stderr,
        )
        return 1

    if bump_flags > 1:
        print(
            "❌ Error: Can only specify one of --patch, --minor, or --major",
            file=sys.stderr,
        )
        return 1

    if args.patch:
        new_version = current_version.bump_patch()
    elif args.minor:
        new_version = current_version.bump_minor()
    elif args.major:
        new_version = current_version.bump_major()
    elif args.version:
        try:
            new_version = Version.parse(args.version)
        except ValueError as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    # Execute release
    success = release(new_version, pyproject_path, args.skip_ci, args.dry_run)
    return 0 if success else 1


def release(
    new_version: Version,
    pyproject_path: Path,
    skip_ci: bool = False,
    dry_run: bool = False,
) -> bool:
    """Execute the release process."""
    current_version = get_current_version(pyproject_path)

    print("🚀 Release Script")
    print("=" * 50)
    print(f"Current version: {current_version}")
    print(f"New version:     {new_version}")
    print(f"Skip CI:         {skip_ci}")
    print(f"Dry run:         {dry_run}")
    print("=" * 50)
    print()

    if new_version <= current_version:
        print(
            f"❌ Error: New version {new_version} must be greater than "
            f"current version {current_version}",
            file=sys.stderr,
        )
        return False

    if not check_working_directory_clean():
        if not dry_run:
            print(
                "❌ Error: Working directory is not clean. "
                "Please commit or stash your changes first.",
                file=sys.stderr,
            )
            result = run_command(["git", "status", "--short"], check=False)
            print(result.stdout)
            return False
        else:
            print("⚠️  Warning: Working directory is not clean (ignored in dry-run mode)")
            print()

    if dry_run:
        print("🔍 Dry run mode - no changes will be made")
        print()
        print(f"Would update version in {pyproject_path}")
        if not skip_ci:
            print("Would run CI checks")
        print(f"Would create commit: 'Bump version to {new_version}'")
        print(f"Would create tag: 'v{new_version}'")
        print()
        print("To push the release, you would run:")
        print("  git push origin main")
        print(f"  git push origin v{new_version}")
        return True

    try:
        # Step 1: Update version
        print("📝 Step 1/4: Updating version in pyproject.toml...")
        update_version_in_file(pyproject_path, new_version)
        print(f"✓ Version updated to {new_version}")
        print()

        # Step 2: Run CI checks
        if not skip_ci:
            print("🔍 Step 2/4: Running CI checks...")
            if not run_ci_checks():
                rollback_changes(pyproject_path)
                return False
            print("✓ All checks passed")
            print()
        else:
            print("⏭️  Step 2/4: Skipping CI checks")
            print()

        # Step 3: Create commit
        print("💾 Step 3/4: Creating git commit...")
        create_commit(new_version)
        print("✓ Version bump committed")
        print()

        # Step 4: Create tag
        print("🏷️  Step 4/4: Creating git tag...")
        create_tag(new_version)
        print(f"✓ Tag v{new_version} created")
        print()

        # Success
        print("✅ Release complete! 🎉")
        print()
        print("To push the release to remote, run:")
        print("  git push origin main")
        print(f"  git push origin v{new_version}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during release: {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        rollback_changes(pyproject_path)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        rollback_changes(pyproject_path)
        return False


def run_ci_checks() -> bool:
    """Run CI checks (format, lint, test)."""
    try:
        run_command(["just", "ci"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CI checks failed: {e}", file=sys.stderr)
        return False


def create_commit(version: Version) -> None:
    """Create a git commit for the version bump."""
    run_command(["git", "add", "pyproject.toml"])
    commit_message = f"Bump version to {version}\n\n"
    run_command(["git", "commit", "-m", commit_message])


def create_tag(version: Version) -> None:
    """Create a git tag for the release."""
    tag_name = f"v{version}"
    tag_message = f"Release version {version}"
    run_command(["git", "tag", "-a", tag_name, "-m", tag_message])


def rollback_changes(pyproject_path: Path) -> None:
    """Rollback changes if something goes wrong."""
    print("⚠️  Rolling back changes...")
    run_command(["git", "restore", str(pyproject_path)], check=False)


def update_version_in_file(pyproject_path: Path, new_version: Version) -> None:
    """Update version in pyproject.toml."""
    content = pyproject_path.read_text()
    updated_content = re.sub(
        r'^version = ".*"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    pyproject_path.write_text(updated_content)


def check_working_directory_clean() -> bool:
    """Check if git working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    # Filter out vhong_todo.md since it's tracked separately
    output_lines = [line for line in result.stdout.strip().split("\n") if line]
    filtered_lines = [line for line in output_lines if "vhong_todo.md" not in line]
    return len(filtered_lines) == 0


def get_current_version(pyproject_path: Path) -> Version:
    """Get the current version from pyproject.toml."""
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    version_str = data["project"]["version"]
    return Version.parse(version_str)


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


if __name__ == "__main__":
    sys.exit(main())
