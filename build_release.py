#!/usr/bin/env python3
"""
XPlane2Blender Release Builder
Creates a release package for Blender addon installation
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_release_package():
    """Create a release package for XPlane2Blender addon"""
    
    # Version info
    version = "5.1.0"
    release_name = f"XPlane2Blender-v{version}-Release"
    
    # Paths
    source_dir = Path("io_xplane2blender")
    temp_dir = Path("temp_release")
    release_dir = temp_dir / "io_xplane2blender"
    zip_path = Path(f"{release_name}.zip")
    
    print(f"Building XPlane2Blender v{version} release package...")
    
    # Clean up any existing temp directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Create temp directory structure
    temp_dir.mkdir(exist_ok=True)
    release_dir.mkdir(exist_ok=True)
    
    # Files and directories to include in the release
    include_patterns = [
        "*.py",           # All Python files
        "resources/",     # Resource files
        "docs/",          # Documentation
        "xplane_types/",  # Type definitions
        "xplane_utils/",  # Utility modules
    ]
    
    # Files to exclude
    exclude_patterns = [
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".pytest_cache/",
        "tests/",
        "*.test.py",
        ".git*",
        "*.tmp",
        "*.bak",
    ]
    
    def should_include(file_path):
        """Check if a file should be included in the release"""
        path_str = str(file_path)
        
        # Check exclude patterns first
        for pattern in exclude_patterns:
            if pattern in path_str or path_str.endswith(pattern.rstrip('/')):
                return False
        
        # Check include patterns
        for pattern in include_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if pattern.rstrip('/') in path_str:
                    return True
            else:
                # File pattern
                if path_str.endswith(pattern.lstrip('*')):
                    return True
        
        return False
    
    # Copy files to release directory
    copied_files = 0
    for root, dirs, files in os.walk(source_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(pattern.rstrip('/') in d for pattern in exclude_patterns)]
        
        for file in files:
            source_file = Path(root) / file
            relative_path = source_file.relative_to(source_dir)
            
            if should_include(relative_path):
                dest_file = release_dir / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                copied_files += 1
                print(f"  Copied: {relative_path}")
    
    # Copy essential root files
    essential_files = [
        "README.md",
        "RELEASE_NOTES_v5.1.0.md",
        "requirements.txt",
    ]
    
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, temp_dir / file)
            print(f"  Copied: {file}")
    
    # Create the zip file
    print(f"\nCreating zip file: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the addon directory
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
                
        # Add essential files to zip root
        for file in essential_files:
            file_path = temp_dir / file
            if file_path.exists():
                zipf.write(file_path, file)
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    # Get zip file size
    zip_size = zip_path.stat().st_size / 1024 / 1024  # MB
    
    print(f"\n✅ Release package created successfully!")
    print(f"📦 Package: {zip_path}")
    print(f"📊 Size: {zip_size:.2f} MB")
    print(f"📁 Files included: {copied_files}")
    print(f"\n📋 Installation Instructions:")
    print(f"1. Download {zip_path}")
    print(f"2. Open Blender 4.0+")
    print(f"3. Go to Edit → Preferences → Add-ons")
    print(f"4. Click 'Install...' and select the zip file")
    print(f"5. Enable 'Import-Export: XPlane2Blender Export for X-Plane 12+ OBJs'")

if __name__ == "__main__":
    create_release_package()