# Developer Guide: XPlane2Blender Validation Systems

## Overview

This guide provides comprehensive documentation for developers working with XPlane2Blender's validation systems, X-Plane 12+ feature implementations, and Blender 4+ integration components.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Validation Framework](#validation-framework)
3. [X-Plane 12 Feature Implementation](#x-plane-12-feature-implementation)
4. [Blender 4+ Integration](#blender-4-integration)
5. [Testing Framework](#testing-framework)
6. [API Reference](#api-reference)
7. [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### Core Components

```
XPlane2Blender/
├── io_xplane2blender/
│   ├── xplane_types/          # Core data structures
│   ├── xplane_utils/          # Validation and utilities
│   ├── xplane_props/          # Blender property definitions
│   ├── xplane_ui/             # User interface panels
│   └── tests/                 # Test framework
├── tests/                     # Integration tests
└── docs/                      # Documentation
```

### Validation System Architecture

```
Validation Framework
├── Core Validators
│   ├── Rain System Validator
│   ├── Thermal System Validator
│   ├── Wiper System Validator
│   ├── Landing Gear Validator
│   └── Material Validator
├── Integration Validators
│   ├── Multi-feature Validator
│   ├── Performance Validator
│   └── Compatibility Validator
└── Reporting System
    ├── Error Collection
    ├── Warning Generation
    └── Report Formatting
```

## Validation Framework

### Core Validation Interface

All validators implement the base validation interface:

```python
from typing import Dict, List, Any
from abc import ABC, abstractmethod

class BaseValidator(ABC):
    """Base class for all validation systems"""
    
    @abstractmethod
    def validate(self, target: Any, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate a target object with given context
        
        Args:
            target: Object to validate
            context: Validation context (filename, version, etc.)
            
        Returns:
            Dict with 'errors', 'warnings', 'info' lists
        """
        pass
    
    def _create_result(self, errors: List[str] = None, 
                      warnings: List[str] = None, 
                      info: List[str] = None) -> Dict[str, List[str]]:
        """Create standardized validation result"""
        return {
            'errors': errors or [],
            'warnings': warnings or [],
            'info': info or []
        }
```

### Rain System Validator

**Location**: `io_xplane2blender/xplane_utils/xplane_rain_validation.py`

```python
def validate_rain_system(rain_props, filename: str, xplane_version: int) -> Dict[str, List[str]]:
    """
    Validate X-Plane 12 rain system configuration
    
    Args:
        rain_props: Rain property group from Blender object
        filename: Target export filename
        xplane_version: Target X-Plane version (e.g., 1200)
        
    Returns:
        Validation results with errors, warnings, and info
        
    Example:
        >>> results = validate_rain_system(obj.xplane.layer.rain, "aircraft.obj", 1200)
        >>> if results['errors']:
        ...     print(f"Validation failed: {results['errors']}")
    """
    errors = []
    warnings = []
    info = []
    
    # Version compatibility check
    if xplane_version < 1200:
        warnings.append("Rain system requires X-Plane 12.0+")
        return {'errors': errors, 'warnings': warnings, 'info': info}
    
    # Rain scale validation
    if hasattr(rain_props, 'rain_scale'):
        if rain_props.rain_scale < 0.0 or rain_props.rain_scale > 1.0:
            errors.append(f"Rain scale must be between 0.0 and 1.0, got {rain_props.rain_scale}")
        elif rain_props.rain_scale == 0.0:
            info.append("Rain scale is 0.0 - no rain effects will be visible")
    
    # Rain friction validation
    if hasattr(rain_props, 'rain_friction_enabled') and rain_props.rain_friction_enabled:
        if not hasattr(rain_props, 'rain_friction_dataref') or not rain_props.rain_friction_dataref:
            errors.append("Rain friction enabled but no dataref specified")
        
        if hasattr(rain_props, 'rain_friction_dry_coefficient'):
            if rain_props.rain_friction_dry_coefficient <= 0.0:
                errors.append("Rain friction dry coefficient must be positive")
        
        if hasattr(rain_props, 'rain_friction_wet_coefficient'):
            if rain_props.rain_friction_wet_coefficient <= 0.0:
                errors.append("Rain friction wet coefficient must be positive")
            elif rain_props.rain_friction_wet_coefficient >= rain_props.rain_friction_dry_coefficient:
                warnings.append("Wet coefficient should typically be less than dry coefficient")
    
    return {'errors': errors, 'warnings': warnings, 'info': info}
```

### Thermal System Validator

```python
def validate_thermal_system(rain_props, filename: str, xplane_version: int) -> Dict[str, List[str]]:
    """Validate thermal system configuration"""
    errors = []
    warnings = []
    info = []
    
    if xplane_version < 1200:
        return {'errors': errors, 'warnings': warnings, 'info': info}
    
    # Thermal texture validation
    if hasattr(rain_props, 'thermal_texture') and rain_props.thermal_texture:
        if not rain_props.thermal_texture.endswith(('.png', '.dds')):
            warnings.append("Thermal texture should be PNG or DDS format")
    
    # Thermal sources validation
    active_sources = 0
    for i in range(1, 5):
        enabled_prop = f'thermal_source_{i}_enabled'
        if hasattr(rain_props, enabled_prop) and getattr(rain_props, enabled_prop):
            active_sources += 1
            
            # Validate source settings
            source_prop = f'thermal_source_{i}'
            if hasattr(rain_props, source_prop):
                source = getattr(rain_props, source_prop)
                
                if hasattr(source, 'defrost_time'):
                    try:
                        defrost_time = float(source.defrost_time)
                        if defrost_time <= 0:
                            errors.append(f"Thermal source {i} defrost time must be positive")
                    except ValueError:
                        errors.append(f"Thermal source {i} defrost time must be a number")
                
                if hasattr(source, 'dataref_on_off') and not source.dataref_on_off:
                    warnings.append(f"Thermal source {i} enabled but no dataref specified")
    
    if active_sources == 0:
        info.append("No thermal sources enabled")
    else:
        info.append(f"{active_sources} thermal source(s) configured")
    
    return {'errors': errors, 'warnings': warnings, 'info': info}
```

### Landing Gear Validator

```python
def validate_gear_object(gear_obj) -> 'GearValidationResult':
    """
    Validate landing gear configuration
    
    Returns:
        GearValidationResult object with validation status
    """
    class GearValidationResult:
        def __init__(self):
            self.is_valid = True
            self.errors = []
            self.warnings = []
    
    result = GearValidationResult()
    
    if not hasattr(gear_obj.xplane, 'special_empty_props'):
        result.is_valid = False
        result.errors.append("Object missing special empty properties")
        return result
    
    wheel_props = gear_obj.xplane.special_empty_props.wheel_props
    
    # Validate gear type
    if hasattr(wheel_props, 'gear_type'):
        valid_types = ['NOSE', 'LEFT_MAIN', 'RIGHT_MAIN']
        if wheel_props.gear_type not in valid_types:
            result.is_valid = False
            result.errors.append(f"Invalid gear type: {wheel_props.gear_type}")
    
    # Validate gear index
    if hasattr(wheel_props, 'gear_index'):
        if not wheel_props.gear_index:
            result.warnings.append("Gear index not specified")
    
    # Validate wheel index
    if hasattr(wheel_props, 'wheel_index'):
        if wheel_props.wheel_index < 0:
            result.is_valid = False
            result.errors.append("Wheel index must be non-negative")
    
    return result
```

## X-Plane 12 Feature Implementation

### Property Group Structure

X-Plane 12 features are implemented through Blender property groups:

```python
import bpy
from bpy.props import *

class XPlaneRainSettings(bpy.types.PropertyGroup):
    """X-Plane 12 Rain System Properties"""
    
    # Rain scale (RAIN_scale)
    rain_scale: FloatProperty(
        name="Rain Scale",
        description="Overall rain effect intensity (0.0-1.0)",
        min=0.0,
        max=1.0,
        default=0.0,
        precision=2
    )
    
    # Rain friction system
    rain_friction_enabled: BoolProperty(
        name="Enable Rain Friction",
        description="Enable rain friction simulation",
        default=False
    )
    
    rain_friction_dataref: StringProperty(
        name="Rain Friction Dataref",
        description="Dataref controlling rain intensity",
        default="sim/weather/rain_percent"
    )
    
    rain_friction_dry_coefficient: FloatProperty(
        name="Dry Friction Coefficient",
        description="Friction coefficient when dry",
        min=0.0,
        default=1.0,
        precision=3
    )
    
    rain_friction_wet_coefficient: FloatProperty(
        name="Wet Friction Coefficient", 
        description="Friction coefficient when wet",
        min=0.0,
        default=0.3,
        precision=3
    )
    
    # Thermal system
    thermal_texture: StringProperty(
        name="Thermal Texture",
        description="Texture file for thermal effects",
        subtype='FILE_PATH'
    )
    
    # Thermal sources (4 sources)
    thermal_source_1_enabled: BoolProperty(
        name="Pilot Side Window",
        description="Enable pilot side window thermal source",
        default=False
    )
    
    # ... additional thermal sources
    
    # Wiper system
    wiper_texture: StringProperty(
        name="Wiper Texture",
        description="Gradient texture for wiper effects",
        subtype='FILE_PATH'
    )
    
    # Wiper settings (4 wipers)
    wiper_1_enabled: BoolProperty(
        name="Wiper 1",
        description="Enable wiper 1",
        default=False
    )
    
    # ... additional wiper settings
```

### Export Integration

X-Plane 12 features are integrated into the export process:

```python
class XPlaneHeader:
    """Export header with X-Plane 12 support"""
    
    def __init__(self, xplane_file, obj_version=1200):
        self.xplane_file = xplane_file
        self.obj_version = obj_version
        self.attributes = {}
        
        # Initialize X-Plane 12 attributes
        if obj_version >= 1200:
            self._init_xplane12_attributes()
    
    def _init_xplane12_attributes(self):
        """Initialize X-Plane 12 specific attributes"""
        self.attributes.update({
            'RAIN_scale': None,
            'RAIN_friction': None,
            'THERMAL_texture': None,
            'WIPER_texture': None,
            # ... additional attributes
        })
    
    def write_rain_attributes(self, rain_props):
        """Write rain system attributes to export"""
        if hasattr(rain_props, 'rain_scale') and rain_props.rain_scale > 0:
            self.attributes['RAIN_scale'] = rain_props.rain_scale
        
        if hasattr(rain_props, 'rain_friction_enabled') and rain_props.rain_friction_enabled:
            friction_data = {
                'dataref': rain_props.rain_friction_dataref,
                'dry_coeff': rain_props.rain_friction_dry_coefficient,
                'wet_coeff': rain_props.rain_friction_wet_coefficient
            }
            self.attributes['RAIN_friction'] = friction_data
```

## Blender 4+ Integration

### Material Node Detection

```python
def detect_principled_bsdf(material) -> List[bpy.types.Node]:
    """Detect Principled BSDF nodes in material"""
    if not material.use_nodes or not material.node_tree:
        return []
    
    principled_nodes = []
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled_nodes.append(node)
    
    return principled_nodes

def auto_detect_texture_nodes(material) -> Dict[str, bpy.types.Node]:
    """Auto-detect texture nodes and their purposes"""
    texture_nodes = {}
    
    if not material.use_nodes:
        return texture_nodes
    
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            # Analyze connections to determine purpose
            for output in node.outputs:
                for link in output.links:
                    input_node = link.to_node
                    input_socket = link.to_socket
                    
                    if input_node.type == 'BSDF_PRINCIPLED':
                        if input_socket.name == 'Base Color':
                            texture_nodes['diffuse'] = node
                        elif input_socket.name == 'Roughness':
                            texture_nodes['roughness'] = node
                        elif input_socket.name == 'Metallic':
                            texture_nodes['metallic'] = node
                    elif input_node.type == 'NORMAL_MAP':
                        texture_nodes['normal'] = node
    
    return texture_nodes

def convert_blender_material_to_xplane(material, texture_maps) -> Dict[str, Any]:
    """Convert Blender 4+ material to X-Plane format"""
    result = {
        'success': False,
        'message': '',
        'mappings': []
    }
    
    if not material.use_nodes:
        result['message'] = "Material does not use nodes"
        return result
    
    # Detect Principled BSDF
    principled_nodes = detect_principled_bsdf(material)
    if not principled_nodes:
        result['message'] = "No Principled BSDF found"
        return result
    
    # Auto-detect textures
    texture_nodes = auto_detect_texture_nodes(material)
    
    # Convert to X-Plane texture mappings
    mappings = []
    if 'diffuse' in texture_nodes:
        mappings.append({
            'type': 'diffuse',
            'texture': texture_nodes['diffuse'].image.filepath if texture_nodes['diffuse'].image else '',
            'node': texture_nodes['diffuse']
        })
    
    if 'normal' in texture_nodes:
        mappings.append({
            'type': 'normal',
            'texture': texture_nodes['normal'].image.filepath if texture_nodes['normal'].image else '',
            'node': texture_nodes['normal']
        })
    
    result.update({
        'success': True,
        'message': f"Converted {len(mappings)} texture mappings",
        'mappings': mappings
    })
    
    return result
```

### UI Panel Integration

```python
class MATERIAL_PT_xplane(bpy.types.Panel):
    """X-Plane material properties panel for Blender 4+"""
    
    bl_label = "X-Plane"
    bl_idname = "MATERIAL_PT_xplane"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    @classmethod
    def poll(cls, context):
        """Panel visibility condition"""
        return context.material is not None
    
    def draw(self, context):
        """Draw panel UI"""
        layout = self.layout
        material = context.material
        
        if not hasattr(material, 'xplane'):
            layout.label(text="X-Plane properties not available")
            return
        
        # Blender 4+ integration section
        if bpy.app.version >= (4, 0, 0):
            box = layout.box()
            box.label(text="Blender 4+ Integration", icon='NODETREE')
            
            texture_maps = material.xplane.texture_maps
            box.prop(texture_maps, 'blender_material_integration')
            
            if texture_maps.blender_material_integration:
                col = box.column()
                col.prop(texture_maps, 'auto_detect_principled_bsdf')
                col.prop(texture_maps, 'auto_detect_normal_map_nodes')
                col.prop(texture_maps, 'auto_detect_image_texture_nodes')
                
                # Material conversion button
                op = box.operator('xplane.convert_material', text="Convert Material")
                op.material_name = material.name
```

## Testing Framework

### Test Structure

```python
class TestBlender4XPlane12Integration(XPlaneTestCase):
    """Integration test class following XPlane2Blender test framework"""
    
    def setUp(self):
        """Test setup - called before each test method"""
        super().setUp()
        self.test_results = {
            'ui_compatibility': [],
            'xplane12_features': [],
            'material_integration': [],
            'errors': []
        }
    
    def _log_test_result(self, category: str, test_name: str, success: bool, message: str):
        """Log test result for reporting"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'blender_version': bpy.app.version
        }
        self.test_results[category].append(result)
    
    def test_rain_system_validation(self):
        """Test rain system validation"""
        # Create test object
        bpy.ops.mesh.primitive_cube_add()
        test_obj = bpy.context.active_object
        test_obj.xplane.isExportableRoot = True
        
        # Configure rain properties
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_scale = 0.7
        rain_props.rain_friction_enabled = True
        
        # Test validation
        from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
        results = validate_rain_system(rain_props, "test.obj", 1200)
        
        # Assert results
        self.assertIsInstance(results, dict)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
        self.assertIn('info', results)
        
        # Clean up
        bpy.data.objects.remove(test_obj, do_unlink=True)
```

### Performance Testing

```python
def test_export_performance(self):
    """Test export performance with complex scenarios"""
    import time
    
    start_time = time.time()
    
    # Create complex scene
    objects = []
    for i in range(10):
        bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
        obj = bpy.context.active_object
        obj.xplane.isExportableRoot = True
        
        # Add material with nodes
        mat = bpy.data.materials.new(f"test_mat_{i}")
        mat.use_nodes = True
        obj.data.materials.append(mat)
        
        # Configure X-Plane 12 features
        rain_props = obj.xplane.layer.rain
        rain_props.rain_scale = 0.5
        rain_props.rain_friction_enabled = True
        
        objects.append(obj)
    
    setup_time = time.time() - start_time
    
    # Test validation performance
    validation_start = time.time()
    for obj in objects:
        validate_rain_system(obj.xplane.layer.rain, f"test_{obj.name}.obj", 1200)
    
    validation_time = time.time() - validation_start
    total_time = time.time() - start_time
    
    # Performance assertions
    self.assertLess(total_time, 5.0, "Performance test should complete within 5 seconds")
    self.assertLess(validation_time / len(objects), 0.1, "Validation should be under 0.1s per object")
    
    # Clean up
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)
```

## API Reference

### Core Validation Functions

```python
# Rain system validation
validate_rain_system(rain_props, filename: str, xplane_version: int) -> Dict[str, List[str]]

# Thermal system validation  
validate_thermal_system(rain_props, filename: str, xplane_version: int) -> Dict[str, List[str]]

# Wiper system validation
validate_wiper_system(rain_props, filename: str, xplane_version: int) -> Dict[str, List[str]]

# Landing gear validation
validate_gear_object(gear_obj) -> GearValidationResult

# Material conversion
convert_blender_material_to_xplane(material, texture_maps) -> Dict[str, Any]

# Texture validation
validate_texture_system(texture_maps, filename: str, xplane_version: int) -> Dict[str, List[str]]
```

### Property Group Classes

```python
# Main property groups
XPlaneObjectSettings      # Object-level properties
XPlaneLayer              # Layer properties
XPlaneRainSettings       # Rain system properties
XPlaneThermalSourceSettings  # Thermal source properties
XPlaneWiperSettings      # Wiper properties
XPlaneTextureMap         # Texture mapping properties

# Material properties
XPlaneMaterialSettings   # Material-level properties

# Scene properties
XPlaneSceneSettings      # Scene-level properties
```

### UI Panel Classes

```python
# Property panels
MATERIAL_PT_xplane       # Material properties panel
OBJECT_PT_xplane         # Object properties panel
SCENE_PT_xplane          # Scene properties panel

# Operators
XPLANE_OT_convert_material           # Material conversion operator
XPLANE_OT_bake_wiper_gradient_texture # Wiper texture generation
XPLANE_OT_validate_xplane12_features  # Feature validation operator
```

## Contributing Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Document all public functions and classes
- Include docstring examples for complex functions

### Testing Requirements

- All new features must include unit tests
- Integration tests required for UI components
- Performance tests for validation systems
- Validation tests for X-Plane 12 features

### Documentation Standards

- Update user guide for new features
- Include migration notes for breaking changes
- Document API changes in developer guide
- Provide examples for complex workflows

### Pull Request Process

1. Create feature branch from main
2. Implement feature with tests
3. Update documentation
4. Run full test suite
5. Submit pull request with description
6. Address review feedback
7. Merge after approval

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/der-On/XPlane2Blender.git
cd XPlane2Blender

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python tests.py

# Run specific test
blender --python tests/test_blender4_xplane12_integration.py
```

---

*This developer guide provides comprehensive documentation for working with XPlane2Blender's validation systems and X-Plane 12+ features. For user-facing documentation, see the [User Guide](xplane12_user_guide.md).*