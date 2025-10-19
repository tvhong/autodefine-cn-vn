#!/usr/bin/env python3
"""Link addon to Anki's addon folder for development on macOS.

This script creates a symlink from the build directory to Anki's addons folder,
allowing for easier testing during development.
"""

import argparse
import sys
from pathlib import Path


def find_anki_addon_folders() -> list[Path]:
    """Find potential Anki addon folders on macOS.

    Returns:
        List of paths to Anki2/addons21 directories that exist
    """
    home = Path.home()
    potential_locations = [
        home / "Library/Application Support/Anki2/addons21",
    ]

    # Also check for different user profiles
    anki2_base = home / "Library/Application Support/Anki2"
    if anki2_base.exists():
        # Look for User 1, User 2, etc.
        for user_dir in anki2_base.iterdir():
            if user_dir.is_dir() and user_dir.name.startswith("User"):
                addons_dir = user_dir / "addons21"
                if addons_dir.exists() and addons_dir not in potential_locations:
                    potential_locations.append(addons_dir)

    return [path for path in potential_locations if path.exists()]


def select_anki_folder(folders: list[Path], auto_confirm: bool = False) -> Path | None:
    """Let user select which Anki folder to use.

    Args:
        folders: List of available Anki addon folders
        auto_confirm: If True, automatically select first folder without prompting

    Returns:
        Selected folder path, or None if user cancels
    """
    if not folders:
        print("❌ No Anki addon folders found!")
        print()
        print("Expected location: ~/Library/Application Support/Anki2/addons21")
        print("Please make sure Anki is installed and you've run it at least once.")
        return None

    if len(folders) == 1:
        print(f"Found Anki addon folder: {folders[0]}")
        if auto_confirm:
            print("✓ Auto-confirmed (--yes flag)")
            return folders[0]
        response = input("Use this folder? [Y/n]: ").strip().lower()
        if response in ("", "y", "yes"):
            return folders[0]
        return None

    print("Multiple Anki addon folders found:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")

    if auto_confirm:
        print("✓ Auto-selecting first folder (--yes flag)")
        return folders[0]

    while True:
        choice = input(f"Select folder [1-{len(folders)}] or 'q' to quit: ").strip()
        if choice.lower() == "q":
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(folders):
                return folders[index]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")


def create_symlink(source: Path, target: Path, auto_confirm: bool = False) -> bool:
    """Create a symlink from source to target.

    Args:
        source: Source directory (build/autodefine_cn_vn)
        target: Target symlink path (in Anki addons folder)
        auto_confirm: If True, automatically overwrite existing files without prompting

    Returns:
        True if successful, False otherwise
    """
    if target.exists() or target.is_symlink():
        print(f"⚠️  Target already exists: {target}")

        # Check if it's already a symlink pointing to our source
        if target.is_symlink() and target.resolve() == source:
            print("✓ Symlink already points to the correct location")
            return True

        if auto_confirm:
            print("✓ Auto-removing and recreating (--yes flag)")
        else:
            response = input("Remove and recreate? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("Cancelled.")
                return False

        # Remove existing file/link
        if target.is_symlink():
            target.unlink()
        elif target.is_dir():
            import shutil

            shutil.rmtree(target)
        else:
            target.unlink()

    # Create symlink
    try:
        target.symlink_to(source)
        print(f"✅ Created symlink: {target} -> {source}")
        return True
    except Exception as e:
        print(f"❌ Failed to create symlink: {e}")
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Link AutoDefine CN-VN addon to Anki's addon folder"
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically confirm all prompts (useful for automation)",
    )

    args = parser.parse_args()

    print("🔗 Link AutoDefine CN-VN addon to Anki")
    print("=" * 50)

    # Get project root and build directory
    project_root = Path(__file__).parent.parent
    build_dir = project_root / "build" / "autodefine_cn_vn"

    # Check if build directory exists
    if not build_dir.exists():
        print(f"❌ Build directory not found: {build_dir}")
        print()
        print("Please run 'just build' first to create the build directory.")
        return 1

    print(f"Source: {build_dir}")
    print()

    # Find Anki addon folders
    anki_folders = find_anki_addon_folders()
    selected_folder = select_anki_folder(anki_folders, auto_confirm=args.yes)

    if not selected_folder:
        return 1

    # Create symlink
    target_link = selected_folder / "autodefine_cn_vn"
    success = create_symlink(build_dir, target_link, auto_confirm=args.yes)

    if success:
        print()
        print("✅ Setup complete! 🎉")
        print()
        print("Next steps:")
        print("1. Restart Anki")
        print("2. The addon should now appear in Tools > Add-ons")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
