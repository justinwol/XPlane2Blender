# Migration Guide: Upgrading to XPlane2Blender with X-Plane 12+ Support

## Overview

This guide helps users migrate from older versions of XPlane2Blender to the latest version with X-Plane 12+ and Blender 4+ support. It covers breaking changes, new features, and step-by-step migration procedures.

## Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Version Compatibility](#version-compatibility)
3. [Breaking Changes](#breaking-changes)
4. [New Features Overview](#new-features-overview)
5. [Migration Steps](#migration-steps)
6. [Legacy Project Conversion](#legacy-project-conversion)
7. [Common Migration Issues](#common-migration-issues)
8. [Testing Your Migration](#testing-your-migration)

## Before You Begin

### Backup Your Projects

**⚠️ IMPORTANT**: Always backup your projects before migrating.

```bash
# Recommended backup structure
project_backup/
├── original_blend_files/
├── exported_obj_files/
├── textures/
└── migration_notes.txt
```

### System Requirements Check

**Minimum Requirements**:
- **Blender**: 4.0+ (recommended: 4.4.3+)
- **X-Plane**: 11.0+ (12.0+ for new features)
- **Operating System**: Windows 10+, macOS 10.15+, Linux (recent distributions)

**Recommended Setup**:
- **Blender**: 4.4.3 or later
- **X-Plane**: 12.0+ for full feature support
- **Python**: 3.10+ (included with Blender)

## Version Compatibility

### XPlane2Blender Version Matrix

| XPlane2Blender Version | Blender Support | X-Plane Support | Key Features |
|------------------------|-----------------|-----------------|--------------|
| 3.x (Legacy) | 2.80-3.6 | 10.x-11.x | Basic export, materials |
| 4.x (Current) | 4.0+ | 11.x-12.x+ | X-Plane 12 features, Blender 4+ integration |

### Feature Compatibility

| Feature | Legacy (3.x) | Current (4.x) | Migration Required |
|---------|--------------|---------------|-------------------|
| Basic Export | ✓ | ✓ | No |
| Materials | ✓ | ✓ Enhanced | Recommended |
| Animations | ✓ | ✓ | No |
| Rain System | ✗ | ✓ | New Feature |
| Thermal System | ✗ | ✓ | New Feature |
| Wiper System | ✗ | ✓ | New Feature |
| Blender 4+ Nodes | ✗ | ✓ | New Feature |
| Landing Gear | ✓ Basic | ✓ Enhanced | Recommended |

## Breaking Changes

### 1. Blender Version Requirements

**Change**: Minimum Blender version increased from 2.80 to 4.0

**Impact**: 
- Older Blender versions no longer supported
- UI panels may look different
- Some property locations changed

**Migration**: Upgrade to Blender 4.0+

### 2. Landing Gear Enum Values

**Change**: Landing gear enum values simplified

**Before (Legacy)**:
```python
gear_type = "GEAR_TYPE_NOSE"
gear_index = "GEAR_INDEX_NOSE"
```

**After (Current)**:
```python
gear_type = "NOSE"
gear_index = "GEAR_INDEX_NOSE"  # Unchanged
```

**Migration**: Update custom scripts and saved configurations

### 3. Material Node Integration

**Change**: New Blender 4+ material integration system

**Impact**:
- Legacy material setups still work
- New auto-detection features available
- Enhanced node support

**Migration**: Optional - enable new features for better workflow

### 4. Export Header Changes

**Change**: Export header constructor updated

**Before**:
```python
header = XPlaneHeader(file)
```

**After**:
```python
header = XPlaneHeader(file, obj_version=1200)
```

**Migration**: Update custom export scripts

## New Features Overview

### X-Plane 12 Features

**Rain System**:
- Rain scale effects
- Surface friction simulation
- Weather integration

**Thermal System**:
- Window defogging simulation
- Multiple thermal sources
- Custom dataref support

**Wiper System**:
- Realistic wiper effects
- Gradient texture generation
- Multi-wiper support

### Blender 4+ Integration

**Material Nodes**:
- Automatic Principled BSDF detection
- Normal map auto-connection
- Image texture node integration

**UI Improvements**:
- Updated panel layouts
- Better property organization
- Enhanced validation feedback

## Migration Steps

### Step 1: Environment Preparation

1. **Install Blender 4.4.3+**
   ```bash
   # Download from blender.org
   # Verify version: Help → About Blender
   ```

2. **Backup Current Projects**
   ```bash
   # Copy entire project folder
   cp -r my_aircraft_project my_aircraft_project_backup
   ```

3. **Download Latest XPlane2Blender**
   ```bash
   # Get latest release from GitHub
   # Or update through Blender Add-ons preferences
   ```

### Step 2: Addon Installation

1. **Remove Old Version**:
   - Blender → Edit → Preferences → Add-ons
   - Find "Import-Export: XPlane2Blender"
   - Disable and Remove

2. **Install New Version**:
   - Add-ons → Install...
   - Select downloaded .zip file
   - Enable "Import-Export: XPlane2Blender"

3. **Verify Installation**:
   - Check version in Add-ons list
   - Confirm X-Plane panels appear in Properties

### Step 3: Project Migration

1. **Open Legacy Project**:
   ```bash
   # Open .blend file in Blender 4.4.3+
   # Blender will automatically upgrade file format
   ```

2. **Check for Warnings**:
   - Review Blender console for migration warnings
   - Note any deprecated features

3. **Update Object Properties**:
   - Review X-Plane object settings
   - Check for any missing properties
   - Update landing gear enum values if needed

### Step 4: Material System Update

1. **Review Existing Materials**:
   ```python
   # Check material node trees
   for material in bpy.data.materials:
       if material.use_nodes:
           print(f"Material: {material.name}")
           for node in material.node_tree.nodes:
               print(f"  Node: {node.type}")
   ```

2. **Enable New Integration** (Optional):
   - Object Properties → X-Plane → Layer → Texture Maps
   - Enable "Blender Material Integration"
   - Enable auto-detection options

3. **Test Material Conversion**:
   - Export a test object
   - Verify materials export correctly
   - Check for any validation warnings

### Step 5: Add X-Plane 12 Features (Optional)

1. **Rain System Setup**:
   ```
   Object Properties → X-Plane → Layer → Rain
   - Set Rain Scale (e.g., 0.7)
   - Configure Rain Friction if needed
   ```

2. **Thermal System** (if applicable):
   ```
   - Set Thermal Texture path
   - Enable thermal sources as needed
   - Configure datarefs
   ```

3. **Wiper System** (if applicable):
   ```
   - Set Wiper Texture path
   - Enable wipers
   - Configure wiper objects and datarefs
   ```

## Legacy Project Conversion

### Automated Conversion Script

Create a Python script to help with bulk conversions:

```python
import bpy

def migrate_landing_gear_enums():
    """Update landing gear enum values"""
    for obj in bpy.data.objects:
        if hasattr(obj, 'xplane') and hasattr(obj.xplane, 'special_empty_props'):
            wheel_props = obj.xplane.special_empty_props.wheel_props
            if hasattr(wheel_props, 'gear_type'):
                # Update old enum values
                if wheel_props.gear_type == "GEAR_TYPE_NOSE":
                    wheel_props.gear_type = "NOSE"
                elif wheel_props.gear_type == "GEAR_TYPE_LEFT_MAIN":
                    wheel_props.gear_type = "LEFT_MAIN"
                elif wheel_props.gear_type == "GEAR_TYPE_RIGHT_MAIN":
                    wheel_props.gear_type = "RIGHT_MAIN"
                print(f"Updated gear type for {obj.name}")

def enable_blender4_integration():
    """Enable Blender 4+ material integration for all objects"""
    for obj in bpy.data.objects:
        if hasattr(obj, 'xplane') and hasattr(obj.xplane, 'layer'):
            texture_maps = obj.xplane.layer.texture_maps
            texture_maps.blender_material_integration = True
            texture_maps.auto_detect_principled_bsdf = True
            texture_maps.auto_detect_normal_map_nodes = True
            texture_maps.auto_detect_image_texture_nodes = True
            print(f"Enabled Blender 4+ integration for {obj.name}")

# Run migration
migrate_landing_gear_enums()
enable_blender4_integration()
print("Migration completed!")
```

### Manual Conversion Checklist

**For Each Aircraft Project**:

- [ ] Open in Blender 4.4.3+
- [ ] Save as new version (.blend1 backup created automatically)
- [ ] Check all X-Plane object settings
- [ ] Update landing gear enum values
- [ ] Review material setups
- [ ] Enable Blender 4+ integration (optional)
- [ ] Add X-Plane 12 features (optional)
- [ ] Test export functionality
- [ ] Verify in X-Plane

## Common Migration Issues

### Issue 1: Missing UI Panels

**Symptoms**: X-Plane panels not visible in Properties

**Causes**:
- Addon not properly installed
- Blender version incompatibility
- Addon not enabled

**Solutions**:
1. Verify addon installation and enablement
2. Check Blender version (must be 4.0+)
3. Restart Blender
4. Check console for error messages

### Issue 2: Material Export Problems

**Symptoms**: Materials not exporting correctly

**Causes**:
- Node tree incompatibilities
- Missing texture files
- Path issues

**Solutions**:
1. Check material node trees for deprecated nodes
2. Verify texture file paths
3. Enable Blender 4+ integration
4. Review export validation messages

### Issue 3: Landing Gear Configuration Errors

**Symptoms**: Landing gear validation errors

**Causes**:
- Old enum values
- Missing properties
- Configuration conflicts

**Solutions**:
1. Update enum values (GEAR_TYPE_NOSE → NOSE)
2. Check all gear properties
3. Verify object hierarchy
4. Review validation messages

### Issue 4: Performance Issues

**Symptoms**: Slow export or Blender performance

**Causes**:
- Complex material node trees
- Large texture files
- Inefficient scene setup

**Solutions**:
1. Optimize material node trees
2. Reduce texture sizes where appropriate
3. Disable unnecessary auto-detection features
4. Profile export performance

### Issue 5: X-Plane 12 Features Not Working

**Symptoms**: New features not visible in X-Plane

**Causes**:
- X-Plane version too old
- Export type not set to Aircraft
- Feature not properly configured

**Solutions**:
1. Verify X-Plane 12.0+ installation
2. Set export type to "Aircraft"
3. Check feature configuration
4. Review X-Plane developer console

## Testing Your Migration

### Validation Checklist

**Basic Functionality**:
- [ ] Project opens without errors
- [ ] All objects visible and properly configured
- [ ] Materials export correctly
- [ ] Animations work as expected
- [ ] Export completes without critical errors

**X-Plane 12 Features** (if enabled):
- [ ] Rain effects visible in X-Plane 12
- [ ] Thermal system responds to datarefs
- [ ] Wiper animations work correctly
- [ ] Landing gear functions properly

**Blender 4+ Integration** (if enabled):
- [ ] Material auto-detection works
- [ ] Node trees convert properly
- [ ] Texture mapping correct
- [ ] Performance acceptable

### Test Export Process

1. **Create Test Export**:
   ```
   File → Export → X-Plane Object (.obj)
   ```

2. **Review Export Log**:
   - Check for errors and warnings
   - Note any validation messages
   - Verify file generation

3. **Test in X-Plane**:
   - Load exported object
   - Test all features
   - Check performance
   - Verify visual quality

### Automated Testing

Use the integrated test suite to verify migration:

```bash
# Run validation tests
blender --python tests/test_blender4_xplane12_integration.py

# Check specific features
blender --python test_complete_validation.py
```

## Migration Support

### Getting Help

**Documentation**:
- [X-Plane 12+ User Guide](xplane12_user_guide.md)
- [Developer Documentation](developer_guide.md)
- [Troubleshooting Guide](troubleshooting.md)

**Community Resources**:
- GitHub Issues: Report migration problems
- Forums: Community support and tips
- Discord: Real-time help and discussion

**Professional Support**:
- Consulting services available for complex migrations
- Custom script development for large projects
- Training sessions for teams

### Migration Timeline

**Recommended Schedule**:

**Week 1**: Environment setup and testing
- Install Blender 4.4.3+
- Install latest XPlane2Blender
- Test with simple projects

**Week 2**: Pilot migration
- Migrate 1-2 small projects
- Document issues and solutions
- Refine migration process

**Week 3-4**: Full migration
- Migrate remaining projects
- Add new features as desired
- Comprehensive testing

**Ongoing**: Optimization and enhancement
- Leverage new features
- Optimize workflows
- Share learnings with community

---

*This migration guide ensures a smooth transition to the latest XPlane2Blender with X-Plane 12+ and Blender 4+ support. For additional help, consult the community resources or file an issue on GitHub.*