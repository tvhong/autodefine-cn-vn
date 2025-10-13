#!/usr/bin/env python3
"""Build script for autodefine-cn-vn Anki addon.

This script packages the addon with vendored dependencies (beautifulsoup4, soupsieve)
into an .ankiaddon file for distribution.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path


def get_version(pyproject_path: Path) -> str:
    """Get version from pyproject.toml."""
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def install_vendor_dependencies(vendor_dir: Path) -> None:
    """Install bs4 and dependencies into vendor directory.

    Args:
        vendor_dir: Path to vendor directory where packages will be installed
    """
    print(f"📦 Installing vendor dependencies to {vendor_dir}...")

    # Ensure vendor directory exists
    vendor_dir.mkdir(parents=True, exist_ok=True)

    # Install beautifulsoup4 and its dependencies
    # We use pip install with --target to install into the vendor directory
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(vendor_dir),
            "--no-deps",  # We'll install deps explicitly
            "beautifulsoup4>=4.12.0",
        ],
        check=True,
    )

    # Install bs4 dependencies
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(vendor_dir),
            "soupsieve",
            "typing-extensions",
        ],
        check=True,
    )

    # Clean up unnecessary files
    for pattern in ["*.dist-info", "*.egg-info", "__pycache__"]:
        for path in vendor_dir.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    print("✓ Vendor dependencies installed")


def copy_addon_files(src_dir: Path, dest_dir: Path) -> None:
    """Copy addon source files to destination.

    Args:
        src_dir: Source directory (src/autodefine_cn_vn)
        dest_dir: Destination directory for build
    """
    print(f"📋 Copying addon files from {src_dir} to {dest_dir}...")

    # Copy all Python files and JSON configs
    for pattern in ["*.py", "*.json"]:
        for file in src_dir.glob(pattern):
            shutil.copy2(file, dest_dir / file.name)

    print("✓ Addon files copied")


def create_ankiaddon_package(build_dir: Path, output_file: Path) -> None:
    """Create .ankiaddon package (zip file) from build directory.

    Args:
        build_dir: Directory containing addon files to package
        output_file: Output .ankiaddon file path
    """
    print(f"📦 Creating .ankiaddon package: {output_file}...")

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in build_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(build_dir.parent)
                zipf.write(file, arcname)

    print(f"✓ Package created: {output_file}")


def build(clean: bool = False, output_dir: Path | None = None) -> Path:
    """Build the Anki addon package.

    Args:
        clean: Whether to clean existing build artifacts first
        output_dir: Directory for output .ankiaddon file (default: dist/)

    Returns:
        Path to the created .ankiaddon file
    """
    # Setup paths
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "autodefine_cn_vn"
    pyproject_path = project_root / "pyproject.toml"

    if output_dir is None:
        output_dir = project_root / "dist"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get version for output filename
    version = get_version(pyproject_path)
    output_file = output_dir / f"autodefine_cn_vn-{version}.ankiaddon"

    # Clean if requested
    if clean and output_file.exists():
        print(f"🧹 Cleaning existing package: {output_file}")
        output_file.unlink()

    print("🚀 Building Anki addon package")
    print("=" * 50)
    print(f"Version: {version}")
    print(f"Source:  {src_dir}")
    print(f"Output:  {output_file}")
    print("=" * 50)
    print()

    # Create temporary build directory
    with tempfile.TemporaryDirectory() as temp_dir:
        build_dir = Path(temp_dir) / "autodefine_cn_vn"
        build_dir.mkdir()

        # Step 1: Copy addon files
        copy_addon_files(src_dir, build_dir)

        # Step 2: Install vendor dependencies
        vendor_dir = build_dir / "vendor"
        install_vendor_dependencies(vendor_dir)

        # Step 3: Create .ankiaddon package
        create_ankiaddon_package(build_dir, output_file)

    print()
    print("✅ Build complete! 🎉")
    print(f"Package: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")

    return output_file


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build autodefine-cn-vn Anki addon")
    parser.add_argument("--clean", action="store_true", help="Clean existing build artifacts")
    parser.add_argument("--output-dir", type=Path, help="Output directory (default: dist/)")

    args = parser.parse_args()

    try:
        build(clean=args.clean, output_dir=args.output_dir)
        return 0
    except Exception as e:
        print(f"❌ Build failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
