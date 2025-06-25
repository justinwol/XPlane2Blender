#!/usr/bin/env python3
"""
Validation script for XPlane2Blender bl_info modernization.
Tests that the addon metadata meets Blender 4+ standards.
"""

import sys
import os
import importlib.util
from typing import Dict, Any, List, Tuple

def load_bl_info(addon_path: str) -> Dict[str, Any]:
    """Load bl_info from the addon's __init__.py file."""
    init_path = os.path.join(addon_path, "__init__.py")
    
    if not os.path.exists(init_path):
        raise FileNotFoundError(f"Addon __init__.py not found at: {init_path}")
    
    # Read and parse the file to extract bl_info
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find bl_info dictionary in the file
    import ast
    import re
    
    # Extract bl_info using regex and ast
    bl_info_match = re.search(r'bl_info\s*=\s*({.*?})', content, re.DOTALL)
    if not bl_info_match:
        raise RuntimeError("bl_info dictionary not found in __init__.py")
    
    try:
        # Parse the dictionary literal
        bl_info_str = bl_info_match.group(1)
        bl_info = ast.literal_eval(bl_info_str)
        return bl_info
    except Exception as e:
        raise RuntimeError(f"Failed to parse bl_info: {e}")

def validate_bl_info(bl_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate bl_info against Blender 4+ standards.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Required fields for modern Blender addons
    required_fields = {
        "name": str,
        "description": str, 
        "author": str,
        "version": tuple,
        "blender": tuple,
        "category": str
    }
    
    # Check required fields
    for field, expected_type in required_fields.items():
        if field not in bl_info:
            issues.append(f"Missing required field: '{field}'")
        elif not isinstance(bl_info[field], expected_type):
            issues.append(f"Field '{field}' should be {expected_type.__name__}, got {type(bl_info[field]).__name__}")
    
    # Blender 4+ specific validations
    
    # 1. Check for modern doc_url instead of deprecated wiki_url
    if "wiki_url" in bl_info:
        issues.append("Deprecated field 'wiki_url' found - should use 'doc_url' for Blender 4+")
    
    if "doc_url" not in bl_info:
        issues.append("Missing 'doc_url' field - required for modern Blender addons")
    elif not isinstance(bl_info["doc_url"], str) or not bl_info["doc_url"].startswith(("http://", "https://")):
        issues.append("'doc_url' should be a valid HTTP/HTTPS URL")
    
    # 2. Check for support field
    if "support" not in bl_info:
        issues.append("Missing 'support' field - required for Blender 4+")
    else:
        valid_support_values = ["OFFICIAL", "COMMUNITY", "TESTING"]
        if bl_info["support"] not in valid_support_values:
            issues.append(f"'support' field should be one of {valid_support_values}, got '{bl_info['support']}'")
    
    # 3. Validate version format
    if "version" in bl_info:
        version = bl_info["version"]
        if not isinstance(version, tuple) or len(version) < 2:
            issues.append("'version' should be a tuple with at least 2 elements (major, minor)")
        elif not all(isinstance(v, int) for v in version):
            issues.append("'version' tuple should contain only integers")
    
    # 4. Validate Blender version compatibility
    if "blender" in bl_info:
        blender_version = bl_info["blender"]
        if not isinstance(blender_version, tuple) or len(blender_version) < 2:
            issues.append("'blender' should be a tuple with at least 2 elements (major, minor)")
        elif not all(isinstance(v, int) for v in blender_version):
            issues.append("'blender' tuple should contain only integers")
        elif blender_version < (4, 0):
            issues.append(f"Minimum Blender version {blender_version} is below 4.0 - not compatible with Blender 4+")
    
    # 5. Check for valid category
    if "category" in bl_info:
        # Common Blender addon categories
        valid_categories = [
            "3D View", "Add Mesh", "Animation", "Development", "Game Engine",
            "Import-Export", "Material", "Mesh", "Node", "Object", "Paint",
            "Physics", "Render", "Rigging", "Sculpting", "Sequencer", "System",
            "Text Editor", "UV", "User Interface"
        ]
        if bl_info["category"] not in valid_categories:
            issues.append(f"Category '{bl_info['category']}' may not be recognized by Blender")
    
    # 6. Optional but recommended fields
    recommended_fields = ["tracker_url", "location", "warning"]
    missing_recommended = [field for field in recommended_fields if field not in bl_info]
    if missing_recommended:
        issues.append(f"Missing recommended fields: {missing_recommended}")
    
    return len(issues) == 0, issues

def print_validation_report(bl_info: Dict[str, Any], is_valid: bool, issues: List[str]):
    """Print a detailed validation report."""
    print("=" * 70)
    print("XPlane2Blender bl_info Modernization Validation Report")
    print("=" * 70)
    
    print("\n📋 Current bl_info Structure:")
    print("-" * 40)
    for key, value in bl_info.items():
        print(f"  {key}: {repr(value)}")
    
    print(f"\n🔍 Validation Results:")
    print("-" * 40)
    
    if is_valid:
        print("✅ PASSED - bl_info meets Blender 4+ standards!")
    else:
        print("❌ FAILED - Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    print(f"\n📊 Modernization Checklist:")
    print("-" * 40)
    
    # Check specific modernization requirements
    checklist = [
        ("'wiki_url' removed", "wiki_url" not in bl_info),
        ("'doc_url' added", "doc_url" in bl_info),
        ("'support' field added", "support" in bl_info),
        ("Blender 4+ compatibility", bl_info.get("blender", (0, 0)) >= (4, 0)),
        ("Version 5.0.0", bl_info.get("version", (0, 0, 0)) >= (5, 0, 0)),
        ("Community support specified", bl_info.get("support") == "COMMUNITY"),
    ]
    
    for description, passed in checklist:
        status = "✅" if passed else "❌"
        print(f"  {status} {description}")
    
    print(f"\n🎯 Summary:")
    print("-" * 40)
    passed_checks = sum(1 for _, passed in checklist if passed)
    total_checks = len(checklist)
    print(f"Modernization Progress: {passed_checks}/{total_checks} checks passed")
    
    if is_valid and passed_checks == total_checks:
        print("🎉 XPlane2Blender bl_info is fully modernized for Blender 4+!")
    elif is_valid:
        print("✅ bl_info is valid but some modernization items could be improved")
    else:
        print("⚠️  bl_info needs fixes to meet Blender 4+ standards")

def main():
    """Main validation function."""
    addon_path = "io_xplane2blender"
    
    try:
        print("Loading bl_info from XPlane2Blender addon...")
        bl_info = load_bl_info(addon_path)
        
        print("Validating against Blender 4+ standards...")
        is_valid, issues = validate_bl_info(bl_info)
        
        print_validation_report(bl_info, is_valid, issues)
        
        # Return appropriate exit code
        return 0 if is_valid else 1
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())