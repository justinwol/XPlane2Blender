# Changelog

All notable changes to XPlane2Blender will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.0] - 2025-06-24

### Major Modernization Release

This is a comprehensive modernization of XPlane2Blender for X-Plane 12+ and Blender 4+ compatibility.

### Added
- **X-Plane 12+ Features Support**
  - Enhanced rain system with thermal options, wiper controls, and friction settings
  - Advanced landing gear animations and detection systems
  - Improved texture validation for X-Plane 12 requirements
  - Material converter for modern X-Plane 12 material workflows

- **Blender 4+ Compatibility**
  - Full compatibility with Blender 4.0+ API changes
  - Updated UI components for modern Blender interface
  - Enhanced collection-based workflow support
  - Improved material node handling

- **New Documentation**
  - Comprehensive X-Plane 12 User Guide (`io_xplane2blender/docs/xplane12_user_guide.md`)
  - Migration Guide for upgrading from older versions (`io_xplane2blender/docs/migration_guide.md`)
  - Developer Guide for contributors (`io_xplane2blender/docs/developer_guide.md`)

- **Enhanced Testing Framework**
  - New integration test suite for Blender 4+ and X-Plane 12+ (`tests/test_blender4_xplane12_integration.py`)
  - Comprehensive test suite runner (`tests/test_suite_runner.py`)
  - Fixed and modernized export tests (`tests/xplane_export_legacy.test.py`)
  - Rain system validation tests
  - Landing gear feature tests
  - Texture mapping validation tests

- **New Utility Modules**
  - `xplane_gear_animation.py` - Landing gear animation utilities
  - `xplane_gear_detection.py` - Automatic gear detection
  - `xplane_gear_validation.py` - Gear configuration validation
  - `xplane_material_converter.py` - Material conversion utilities
  - `xplane_rain_validation.py` - Rain system validation
  - `xplane_texture_validation.py` - Texture validation for X-Plane 12

### Changed
- **Minimum Requirements Updated**
  - Now requires Blender 4.0+ (was 2.80+)
  - Optimized for X-Plane 12+ (maintains backward compatibility)
  - Updated addon metadata and descriptions

- **Core System Improvements**
  - Modernized material handling for X-Plane 12 workflows
  - Enhanced manipulator system with improved validation
  - Updated export pipeline for better X-Plane 12 compatibility
  - Improved error handling and user feedback

- **UI/UX Enhancements**
  - Updated interface for Blender 4+ design language
  - Improved property panels and controls
  - Better integration with Blender's modern workflow

### Removed
- **Legacy Update System**
  - Removed outdated updater functionality (`xplane_updater.py`)
  - Cleaned up legacy update helper utilities
  - Removed obsolete update tests and fixtures

- **Deprecated Features**
  - Removed support for very old Blender versions
  - Cleaned up legacy compatibility code
  - Removed outdated test cases and fixtures

### Fixed
- **Export System**
  - Fixed export test failures that were preventing proper validation
  - Resolved collection export issues in Blender 4+
  - Fixed material export compatibility problems

- **Compatibility Issues**
  - Resolved API deprecation warnings in Blender 4+
  - Fixed property registration issues
  - Corrected UI layout problems in modern Blender

- **Test Suite**
  - Fixed broken export tests
  - Resolved test runner compatibility issues
  - Updated test fixtures for current X-Plane standards

### Technical Details
- **Version**: 5.0.0
- **Blender Compatibility**: 4.0.0+
- **X-Plane Compatibility**: 12+ (with backward compatibility)
- **Python Version**: 3.10+ (Blender 4+ requirement)

### Migration Notes
- Users upgrading from older versions should review the Migration Guide
- Existing projects may need material updates for optimal X-Plane 12 compatibility
- Test your exports thoroughly after upgrading
- Backup your projects before upgrading

### Contributors
- Modernization and X-Plane 12+ compatibility updates
- Enhanced testing framework
- Comprehensive documentation overhaul
- Legacy code cleanup and optimization

---

## Previous Versions

For changelog information about versions prior to 5.0.0, please refer to the [GitHub releases page](https://github.com/X-Plane/XPlane2Blender/releases) and commit history.