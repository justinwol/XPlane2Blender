# Modern Texture System (TEXTURE_MAP) for X-Plane 12+

## Overview

The Modern Texture System provides comprehensive support for X-Plane 12+ TEXTURE_MAP directives, enabling advanced material workflows with proper channel mapping, validation, and Blender 4+ material node integration.

## Features

### ✅ Complete TEXTURE_MAP Support
- **Normal Maps**: RG channel normal mapping with automatic Z reconstruction
- **Material/Gloss**: Combined metallic and roughness textures
- **Gloss Only**: Dedicated gloss/roughness textures
- **Metallic**: PBR metallic workflow support
- **Roughness**: PBR roughness workflow support

### ✅ Channel Mapping
- Flexible channel specification (R, G, B, A, RG, RGB, RGBA)
- Automatic channel validation and recommendations
- Support for packed texture workflows

### ✅ Texture Validation
- File existence checking
- Format validation (PNG, DDS, JPG support)
- Resolution validation with power-of-two recommendations
- Conflict detection (e.g., material_gloss vs gloss)

### ✅ Blender 4+ Integration
- Automatic Principled BSDF node detection
- Normal Map node integration
- Image Texture node path extraction
- Material compatibility analysis

## Usage

### Basic Setup

1. **Enable Modern Texture System**:
   - In the X-Plane layer properties, find "Modern Texture System (X-Plane 12+)"
   - Enable "Enable Validation" for comprehensive checking
   - Enable "Blender 4+ Integration" for automatic material detection

2. **Configure Texture Maps**:
   ```
   Normal Texture: textures/my_normal.png (Channels: RG)
   Material/Gloss: textures/my_material_gloss.dds (Channels: RGBA)
   ```

3. **Export**: The system automatically generates TEXTURE_MAP directives:
   ```
   TEXTURE_MAP normal RG textures/my_normal.png
   TEXTURE_MAP material_gloss RGBA textures/my_material_gloss.dds
   ```

### Blender Material Integration

The system can automatically detect textures from Blender 4+ material nodes:

1. **Setup Principled BSDF**: Use the standard Principled BSDF node
2. **Connect Image Textures**: Connect Image Texture nodes to appropriate inputs:
   - Base Color → Diffuse texture detection
   - Normal → Normal map detection (through Normal Map node)
   - Metallic → Metallic texture detection
   - Roughness → Roughness texture detection

3. **Auto-Detection**: Enable "Blender 4+ Integration" and the system will:
   - Scan material nodes in your objects
   - Extract texture paths from Image Texture nodes
   - Map them to appropriate X-Plane texture types
   - Apply proper channel configurations

## TEXTURE_MAP Format

The X-Plane 12+ TEXTURE_MAP directive format is:
```
TEXTURE_MAP <usage> <channels> <texture_path>
```

### Usage Types
- `normal`: Normal maps (typically RG channels)
- `material_gloss`: Combined material and gloss (typically RGBA)
- `gloss`: Gloss/roughness only (typically single channel)
- `metallic`: Metallic maps (typically single channel)
- `roughness`: Roughness maps (typically single channel)

### Channel Specifications
- `R`, `G`, `B`, `A`: Single channels
- `RG`, `RGB`, `RGBA`: Multi-channel combinations

## Validation System

### Error Types

**Errors** (prevent export):
- Missing texture files
- Unsupported texture formats
- Conflicting texture configurations

**Warnings** (allow export with notifications):
- Non-power-of-two texture resolutions
- Non-standard channel mappings
- Large texture files

**Info** (informational):
- Auto-detection results
- Optimization suggestions

### Validation Settings

- **Check File Existence**: Verify texture files exist on disk
- **Check File Formats**: Validate supported formats (PNG, DDS, JPG)
- **Check Resolution**: Warn about non-power-of-two textures

## Best Practices

### Texture Organization
```
textures/
├── diffuse/
│   ├── aircraft_body.png
│   └── aircraft_wings.png
├── normal/
│   ├── aircraft_body_normal.png    (RG channels)
│   └── aircraft_wings_normal.png   (RG channels)
└── material/
    ├── aircraft_body_material.dds  (R=metallic, G=roughness)
    └── aircraft_wings_material.dds (R=metallic, G=roughness)
```

### Channel Packing Recommendations

**Normal Maps**:
- Use RG channels (X-Plane reconstructs Z)
- Store in PNG or DDS format

**Material/Gloss Combined**:
- R channel: Metallic (0=dielectric, 1=metallic)
- G channel: Roughness (0=mirror, 1=rough)
- B channel: Available for future use
- A channel: Available for future use

**Single Channel Maps**:
- Use R channel for consistency
- Consider DDS for better compression

### Performance Optimization

1. **Texture Resolution**: Use power-of-two resolutions (512, 1024, 2048)
2. **Format Selection**: 
   - PNG for textures with transparency
   - DDS for better compression and performance
3. **Channel Packing**: Combine related maps (metallic + roughness)

## Blender 4+ Material Setup

### Recommended Node Setup

```
[Image Texture: diffuse.png] → [Principled BSDF: Base Color]
[Image Texture: normal.png] → [Normal Map] → [Principled BSDF: Normal]
[Image Texture: material.dds] → [Separate RGB] → R → [Principled BSDF: Metallic]
                                              → G → [Principled BSDF: Roughness]
```

### Auto-Detection Features

- **Principled BSDF Detection**: Automatically finds and analyzes Principled BSDF nodes
- **Normal Map Integration**: Traces through Normal Map nodes to find source textures
- **Path Resolution**: Handles Blender's relative path notation (`//`)
- **Multi-Material Support**: Processes all materials in the export

## API Reference

### Validation Functions

```python
from io_xplane2blender.xplane_utils.xplane_texture_validation import validate_texture_system

# Validate texture system
results = validate_texture_system(texture_maps, filename, xplane_version)
errors = results['errors']
warnings = results['warnings']
info = results['info']
```

### Material Conversion

```python
from io_xplane2blender.xplane_utils.xplane_material_converter import convert_blender_material_to_xplane

# Convert Blender material to X-Plane texture maps
result = convert_blender_material_to_xplane(material, texture_maps)
if result['success']:
    detected_textures = result['textures']
```

### Export String Generation

```python
from io_xplane2blender.xplane_utils.xplane_texture_validation import get_texture_map_export_string

# Generate TEXTURE_MAP export string
export_string = get_texture_map_export_string("normal", "RG", "textures/normal.png")
# Result: "TEXTURE_MAP normal RG textures/normal.png"
```

## Migration from Legacy System

### Legacy Properties (Still Supported)
- `texture_map_normal`
- `texture_map_material_gloss`
- `texture_map_gloss`

### Modern System Advantages
- Channel specification support
- Comprehensive validation
- Blender material integration
- Extended texture type support
- Better error reporting

### Migration Steps

1. **Enable Modern System**: Turn on validation and integration
2. **Review Existing Textures**: Check current texture map assignments
3. **Configure Channels**: Specify appropriate channel mappings
4. **Test Export**: Verify TEXTURE_MAP directives are correct
5. **Optimize**: Use validation feedback to improve texture setup

## Troubleshooting

### Common Issues

**"Texture file not found"**:
- Check file paths are correct
- Ensure textures exist relative to blend file
- Verify file permissions

**"Non-power-of-two texture resolution"**:
- Resize textures to 512, 1024, 2048, etc.
- Consider performance impact of large textures

**"Conflicting texture configurations"**:
- Don't use both material_gloss and gloss textures
- Choose one approach for consistency

**"No Principled BSDF node found"**:
- Add Principled BSDF node to material
- Enable "Use Nodes" for the material
- Connect nodes properly

### Debug Information

Enable debug mode in X-Plane scene settings to see:
- Texture detection results
- Material analysis details
- Validation step-by-step process
- Export generation details

## Version Compatibility

- **X-Plane 12.00+**: Full TEXTURE_MAP support
- **X-Plane 12.10+**: Enhanced texture features
- **Blender 4.0+**: Full material integration support
- **Blender 3.x**: Basic functionality (limited material integration)

## Future Enhancements

Planned features for future versions:
- Additional texture usage types
- Advanced channel packing options
- Texture optimization tools
- Batch material conversion
- Custom shader support

---

For technical support and feature requests, please refer to the XPlane2Blender documentation and community forums.