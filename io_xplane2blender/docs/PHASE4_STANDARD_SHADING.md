# Phase 4: Standard Shading Completion

This document describes the implementation of Phase 4 Standard Shading features for XPlane2Blender, providing comprehensive support for X-Plane's standard shading commands and PBR workflow integration.

## Overview

Phase 4 completes the standard shading implementation by adding support for:

- **Complete PBR Workflow** - Full Physically Based Rendering material pipeline
- **Decal Support** - Advanced decal rendering with DECAL, DECAL_RGBA, DECAL_KEYED commands
- **Texture Tiling** - TEXTURE_TILE command for breaking up texture repetition
- **Normal Map Decals** - NORMAL_DECAL commands for enhanced surface detail
- **Advanced Material Controls** - SPECULAR, BUMP_LEVEL, DITHER_ALPHA commands

## Standard Shading Commands

### Decal Commands

#### DECAL
Basic decal command for blending higher resolution repeating textures into base textures.

**Format:** `DECAL [scale] [texture_file]`

**Parameters:**
- `scale`: Scale factor for the decal texture (0.1 - 10.0)
- `texture_file`: Path to the decal texture file

**Usage:**
```
DECAL 2.0 textures/detail_decal.png
```

#### DECAL_RGBA
RGBA decal command with full alpha channel support.

**Format:** `DECAL_RGBA [scale] [texture_file]`

**Parameters:**
- `scale`: Scale factor for the decal texture (0.1 - 10.0)
- `texture_file`: Path to the RGBA decal texture file

**Usage:**
```
DECAL_RGBA 1.5 textures/detail_rgba.png
```

#### DECAL_KEYED
Keyed decal command with color key transparency.

**Format:** `DECAL_KEYED [scale] [r] [g] [b] [a] [alpha] [texture_file]`

**Parameters:**
- `scale`: Scale factor for the decal texture (0.1 - 10.0)
- `r`, `g`, `b`, `a`: Key color components (0.0 - 1.0)
- `alpha`: Alpha value for the decal (0.0 - 1.0)
- `texture_file`: Path to the keyed decal texture file

**Usage:**
```
DECAL_KEYED 1.0 1.0 0.0 1.0 1.0 0.8 textures/keyed_decal.png
```

### Texture Tiling

#### TEXTURE_TILE
Breaks up texture repetition by dividing textures into grids and randomly permuting tiles.

**Format:** `TEXTURE_TILE [x_tiles] [y_tiles] [x_pages] [y_pages] [texture]`

**Parameters:**
- `x_tiles`: Number of tiles in X direction (1 - 16)
- `y_tiles`: Number of tiles in Y direction (1 - 16)
- `x_pages`: Number of pages in X direction (1 - 16)
- `y_pages`: Number of pages in Y direction (1 - 16)
- `texture`: Path to the tile texture file

**Usage:**
```
TEXTURE_TILE 4 4 2 2 textures/tiled_surface.png
```

### Normal Map Decals

#### NORMAL_DECAL
Provides additional surface detail with gloss control.

**Format:** `NORMAL_DECAL [scale] [texture_file] [gloss]`

**Parameters:**
- `scale`: Scale factor for the normal decal (0.1 - 10.0)
- `texture_file`: Path to the normal map texture file
- `gloss`: Gloss value for the normal decal (0.0 - 2.0)

**Usage:**
```
NORMAL_DECAL 1.0 textures/surface_normal.png 1.5
```

### Material Controls

#### SPECULAR
Fine-tuning of specular effects.

**Format:** `SPECULAR [ratio]`

**Parameters:**
- `ratio`: Specular ratio (0.0 - 2.0)

**Usage:**
```
SPECULAR 1.2
```

#### BUMP_LEVEL
Fine-tuning of bump mapping effects.

**Format:** `BUMP_LEVEL [ratio]`

**Parameters:**
- `ratio`: Bump level ratio (0.0 - 2.0)

**Usage:**
```
BUMP_LEVEL 0.8
```

### Alpha Controls

#### DITHER_ALPHA
Controls alpha dithering for transparency effects.

**Format:** `DITHER_ALPHA [softness] [bleed]`

**Parameters:**
- `softness`: Dithering softness (0.0 - 1.0)
- `bleed`: Dithering bleed (0.0 - 1.0)

**Usage:**
```
DITHER_ALPHA 0.7 0.3
```

#### NO_ALPHA
Disables alpha channel processing.

**Format:** `NO_ALPHA`

**Usage:**
```
NO_ALPHA
```

#### NO_BLEND (Enhanced)
Enhanced NO_BLEND command with alpha cutoff control.

**Format:** `NO_BLEND [alpha_cutoff_level]`

**Parameters:**
- `alpha_cutoff_level`: Alpha cutoff threshold (0.0 - 1.0)

**Usage:**
```
NO_BLEND 0.6
```

## PBR Workflow Integration

### Automatic PBR Detection

The system automatically detects PBR (Physically Based Rendering) workflows in Blender materials by analyzing:

- **Principled BSDF Node**: Presence and usage of Principled BSDF shader
- **Connected Inputs**: Metallic, Roughness, Normal, and Base Color connections
- **Texture Usage**: Number and type of connected texture nodes
- **Material Complexity**: Overall node setup complexity

### PBR Confidence Scoring

The PBR detection system provides confidence scoring based on:

- **Base Color Input**: 20% weight
- **Metallic Input**: 30% weight  
- **Roughness Input**: 30% weight
- **Normal Input**: 20% weight

Materials with confidence scores ≥ 50% are considered PBR workflows.

### Auto-Configuration

When PBR workflows are detected, the system can automatically:

- Enable standard shading features
- Set appropriate material control defaults
- Configure texture tiling for complex materials
- Apply recommended settings for X-Plane compatibility

## Blender Integration

### Material Properties

Standard shading properties are accessible through the material properties panel:

**Location:** Material Properties → X-Plane → Standard Shading (Phase 4)

### Property Groups

#### Enable/Disable Controls
- **Enable Standard Shading**: Master toggle for all standard shading features

#### Decal Commands
- **DECAL**: Basic decal settings with scale and texture path
- **DECAL_RGBA**: RGBA decal settings with texture path
- **DECAL_KEYED**: Keyed decal with color key and alpha settings

#### Texture Tiling
- **TEXTURE_TILE**: Grid configuration and texture path settings

#### Normal Decals
- **NORMAL_DECAL**: Scale, texture path, and gloss settings

#### Material Controls
- **Specular Ratio**: Fine-tune specular effects
- **Bump Level Ratio**: Fine-tune bump mapping

#### Alpha Controls
- **Dither Alpha**: Softness and bleed settings
- **NO_ALPHA**: Simple toggle
- **NO_BLEND**: Alpha cutoff level

### Auto-Configuration Operator

**Operator:** `material.xplane_auto_configure_standard_shading`

**Function:** Automatically analyzes the current material and applies appropriate standard shading settings based on:

- PBR workflow detection
- Texture complexity analysis
- Material node setup evaluation
- X-Plane compatibility requirements

### PBR Analysis Panel

**Location:** Material Properties → X-Plane → Standard Shading → PBR Analysis

**Features:**
- Real-time PBR workflow detection
- Confidence scoring display
- Feature compatibility analysis
- Recommendations for optimization

## Implementation Details

### File Structure

```
io_xplane2blender/
├── xplane_constants.py          # Standard shading constants
├── xplane_props.py              # XPlaneStandardShading PropertyGroup
├── xplane_ui.py                 # UI panels and operators
├── xplane_types/
│   ├── xplane_header.py         # Export command generation
│   └── xplane_material.py       # Material integration
├── xplane_utils/
│   └── xplane_material_converter.py  # PBR detection and analysis
└── tests/materials/standard_shading/  # Test suite
```

### Constants

All standard shading constants are defined in `xplane_constants.py`:

```python
# Standard Shading Commands
SHADER_DECAL = "DECAL"
SHADER_DECAL_RGBA = "DECAL_RGBA"
SHADER_DECAL_KEYED = "DECAL_KEYED"
SHADER_TEXTURE_TILE = "TEXTURE_TILE"
SHADER_NORMAL_DECAL = "NORMAL_DECAL"
SHADER_DITHER_ALPHA = "DITHER_ALPHA"
SHADER_NO_ALPHA = "NO_ALPHA"

# Default Values
DEFAULT_DECAL_SCALE = 1.0
DEFAULT_TEXTURE_TILE_X = 1
DEFAULT_TEXTURE_TILE_Y = 1
DEFAULT_NORMAL_DECAL_GLOSS = 1.0
DEFAULT_SPECULAR_RATIO = 1.0
DEFAULT_BUMP_LEVEL_RATIO = 1.0
DEFAULT_DITHER_ALPHA_SOFTNESS = 0.5
DEFAULT_NO_BLEND_ALPHA_CUTOFF = 0.5
```

### Export Pipeline Integration

Standard shading commands are exported through the `_export_standard_shading_commands()` method in `XPlaneHeader`, which:

1. Checks X-Plane version compatibility (requires 12+)
2. Validates material settings and standard shading enablement
3. Processes each command type with appropriate parameters
4. Generates properly formatted OBJ commands
5. Handles texture path resolution and error reporting

### Material Converter Integration

The material converter system provides:

- **PBR Workflow Detection**: Automatic analysis of Blender material nodes
- **Standard Shading Feature Detection**: Identification of potential decals and tiling
- **Compatibility Analysis**: Assessment of material suitability for standard shading
- **Auto-Configuration**: Intelligent application of appropriate settings

## Version Compatibility

### X-Plane Version Requirements

- **Minimum Version**: X-Plane 12.0 (version 1200)
- **Recommended Version**: X-Plane 12.1+ for full feature support

### Blender Version Requirements

- **Minimum Version**: Blender 3.0+
- **Recommended Version**: Blender 4.0+ for full PBR integration
- **Node System**: Requires materials with enabled node systems

## Usage Examples

### Basic Decal Setup

1. Create a material with standard shading enabled
2. Configure DECAL command with appropriate scale
3. Specify decal texture path
4. Export to X-Plane 12+ format

### PBR Material Workflow

1. Set up Principled BSDF with connected textures
2. Use Auto-Configure operator for automatic setup
3. Fine-tune material controls as needed
4. Verify compatibility in PBR Analysis panel

### Texture Tiling Configuration

1. Enable TEXTURE_TILE for materials with repetitive textures
2. Configure grid dimensions based on texture complexity
3. Specify tile texture with appropriate resolution
4. Test in X-Plane for optimal visual results

## Testing

### Test Suite

Comprehensive test coverage is provided in `tests/materials/standard_shading/`:

- **Property Validation**: Ensures all properties are accessible
- **Command Export**: Validates proper OBJ command generation
- **Version Compatibility**: Tests X-Plane version requirements
- **PBR Integration**: Validates workflow detection and analysis
- **Multi-Feature Testing**: Ensures features work together correctly

### Running Tests

```bash
# Run all standard shading tests
python -m pytest tests/materials/standard_shading/

# Run specific test class
python -m pytest tests/materials/standard_shading/standard_shading_phase4.test.py::TestStandardShadingPhase4

# Run with verbose output
python -m pytest tests/materials/standard_shading/ -v
```

## Best Practices

### Material Setup

1. **Use PBR Workflows**: Leverage Principled BSDF for best results
2. **Optimize Texture Usage**: Use appropriate resolutions and formats
3. **Test Compatibility**: Use PBR Analysis panel for validation
4. **Version Targeting**: Ensure X-Plane 12+ compatibility

### Performance Considerations

1. **Texture Resolution**: Use power-of-two resolutions when possible
2. **Decal Complexity**: Limit number of active decals per material
3. **Tiling Configuration**: Balance visual quality with performance
4. **Material Controls**: Use conservative values for ratios

### Workflow Recommendations

1. **Start with Auto-Configure**: Use automatic setup as baseline
2. **Iterative Refinement**: Adjust settings based on X-Plane testing
3. **Documentation**: Document custom configurations for team use
4. **Version Control**: Track material settings in project files

## Troubleshooting

### Common Issues

#### Standard Shading Not Available
- **Cause**: Material lacks XPlane properties
- **Solution**: Ensure material has XPlane settings configured

#### Commands Not Exported
- **Cause**: Standard shading disabled or X-Plane version < 12
- **Solution**: Enable standard shading and set X-Plane version to 1200+

#### PBR Detection Failed
- **Cause**: Material lacks Principled BSDF or connected inputs
- **Solution**: Set up proper PBR node structure with connected textures

#### Texture Paths Invalid
- **Cause**: Relative paths not resolved correctly
- **Solution**: Use absolute paths or ensure proper project structure

### Debug Information

Enable debug logging to troubleshoot issues:

1. Set debug mode in XPlane2Blender preferences
2. Check console output during export
3. Review generated OBJ files for command presence
4. Validate texture path resolution

## Future Enhancements

### Planned Features

1. **Advanced Decal Types**: Additional decal command variants
2. **Procedural Tiling**: Automatic tile generation from base textures
3. **Material Libraries**: Preset configurations for common use cases
4. **Real-time Preview**: X-Plane-style material preview in Blender

### Integration Opportunities

1. **Texture Baking**: Automatic texture optimization for X-Plane
2. **LOD Integration**: Material complexity scaling with LOD levels
3. **Animation Support**: Animated material properties
4. **Validation Tools**: Enhanced compatibility checking

## Conclusion

Phase 4 Standard Shading Completion provides comprehensive support for X-Plane's advanced shading features, enabling artists to create high-quality materials with modern PBR workflows while maintaining optimal performance in X-Plane 12+.

The implementation follows established XPlane2Blender patterns, provides extensive testing coverage, and includes comprehensive documentation to ensure reliable operation and ease of use.