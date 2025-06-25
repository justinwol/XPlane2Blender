# XPlane2Blender Developer Architecture Guide

## Overview

This guide provides comprehensive documentation for developers working with the XPlane2Blender architecture, covering the new patterns, frameworks, and integration points introduced during the Feature Implementation Project. The architecture has been designed for extensibility, maintainability, and performance while supporting the complete OBJ8 specification.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Design Patterns](#core-design-patterns)
3. [Validation Framework](#validation-framework)
4. [Export Pipeline Architecture](#export-pipeline-architecture)
5. [Property System Design](#property-system-design)
6. [UI Integration Patterns](#ui-integration-patterns)
7. [Testing Architecture](#testing-architecture)
8. [Performance Optimization Patterns](#performance-optimization-patterns)
9. [Extension and Plugin Patterns](#extension-and-plugin-patterns)
10. [Best Practices and Guidelines](#best-practices-and-guidelines)

## Architecture Overview

### System Architecture Diagram

```
XPlane2Blender Architecture
├── Core Framework
│   ├── Property System (xplane_props.py)
│   ├── Type System (xplane_types/)
│   ├── Validation Framework (xplane_utils/)
│   └── Export Pipeline (xplane_types/xplane_header.py)
├── Feature Modules
│   ├── Geometry Commands
│   ├── Lighting System
│   ├── Action Commands
│   ├── Material System
│   ├── Weather System
│   └── State Management
├── Integration Layer
│   ├── Blender Integration (xplane_ui.py)
│   ├── X-Plane Compatibility
│   └── Version Management
└── Testing Framework
    ├── Unit Tests
    ├── Integration Tests
    └── Performance Tests
```

### Key Architectural Principles

1. **Modularity**: Each feature is self-contained with clear interfaces
2. **Extensibility**: Easy addition of new OBJ8 commands and features
3. **Validation-First**: Comprehensive validation at all levels
4. **Performance-Oriented**: Optimized for large project handling
5. **Backward Compatibility**: Maintains compatibility with existing projects

## Core Design Patterns

### 1. Command Pattern for OBJ8 Export

The export system uses the Command pattern to encapsulate OBJ8 command generation:

```python
class XPlaneCommand:
    """Base class for all X-Plane OBJ8 commands"""
    
    def __init__(self, name: str, version_required: int = 1000):
        self.name = name
        self.version_required = version_required
        self.parameters = {}
    
    def validate(self, context: 'ExportContext') -> 'ValidationResult':
        """Validate command parameters and context"""
        raise NotImplementedError
    
    def generate(self, context: 'ExportContext') -> str:
        """Generate OBJ8 command string"""
        raise NotImplementedError
    
    def get_dependencies(self) -> List[str]:
        """Return list of dependent commands"""
        return []

# Example implementation
class LightConeCommand(XPlaneCommand):
    def __init__(self, position, direction, color, angle, intensity):
        super().__init__("LIGHT_CONE", 1200)
        self.position = position
        self.direction = direction
        self.color = color
        self.angle = angle
        self.intensity = intensity
    
    def validate(self, context):
        result = ValidationResult()
        if self.angle < 0 or self.angle > 180:
            result.add_error("Light cone angle must be between 0 and 180 degrees")
        return result
    
    def generate(self, context):
        return f"LIGHT_CONE {self.position.x} {self.position.y} {self.position.z} " \
               f"{self.direction.x} {self.direction.y} {self.direction.z} " \
               f"{self.color.r} {self.color.g} {self.color.b} {self.angle} {self.intensity}"
```

### 2. Factory Pattern for Feature Creation

Feature factories provide consistent creation and configuration:

```python
class FeatureFactory:
    """Factory for creating feature instances"""
    
    @staticmethod
    def create_geometry_feature(geometry_type: str, **kwargs) -> 'GeometryFeature':
        """Create geometry feature based on type"""
        factories = {
            'LINES': LinesFeatureFactory,
            'LINE_STRIP': LineStripFeatureFactory,
            'QUAD_STRIP': QuadStripFeatureFactory,
            'FAN': FanFeatureFactory
        }
        
        factory = factories.get(geometry_type)
        if not factory:
            raise ValueError(f"Unknown geometry type: {geometry_type}")
        
        return factory.create(**kwargs)
    
    @staticmethod
    def create_lighting_feature(light_type: str, **kwargs) -> 'LightingFeature':
        """Create lighting feature based on type"""
        factories = {
            'LIGHT_CONE': LightConeFeatureFactory,
            'LIGHT_BILLBOARD': LightBillboardFeatureFactory
        }
        
        factory = factories.get(light_type)
        if not factory:
            raise ValueError(f"Unknown light type: {light_type}")
        
        return factory.create(**kwargs)
```

### 3. Observer Pattern for Property Updates

Property changes trigger validation and UI updates:

```python
class PropertyObserver:
    """Observer for property changes"""
    
    def on_property_changed(self, property_name: str, old_value, new_value, context):
        """Called when a property changes"""
        pass

class ValidationObserver(PropertyObserver):
    """Observer that triggers validation on property changes"""
    
    def on_property_changed(self, property_name, old_value, new_value, context):
        if self.should_validate(property_name):
            validation_result = self.validate_property(property_name, new_value, context)
            self.update_validation_ui(validation_result)

class XPlanePropertyGroup(bpy.types.PropertyGroup):
    """Base property group with observer support"""
    
    def __init__(self):
        super().__init__()
        self.observers = []
    
    def add_observer(self, observer: PropertyObserver):
        self.observers.append(observer)
    
    def notify_observers(self, property_name, old_value, new_value):
        for observer in self.observers:
            observer.on_property_changed(property_name, old_value, new_value, self)
```

### 4. Strategy Pattern for Version Compatibility

Different strategies handle various X-Plane versions:

```python
class VersionStrategy:
    """Base strategy for version-specific behavior"""
    
    def __init__(self, version: int):
        self.version = version
    
    def supports_feature(self, feature_name: str) -> bool:
        """Check if version supports feature"""
        raise NotImplementedError
    
    def get_command_format(self, command_name: str) -> str:
        """Get command format for version"""
        raise NotImplementedError

class XPlane12Strategy(VersionStrategy):
    """Strategy for X-Plane 12+ features"""
    
    def __init__(self):
        super().__init__(1200)
    
    def supports_feature(self, feature_name):
        xp12_features = {
            'RAIN_scale', 'RAIN_friction', 'THERMAL_texture', 
            'WIPER_texture', 'BLEND_GLASS', 'ATTR_cockpit_device'
        }
        return feature_name in xp12_features
    
    def get_command_format(self, command_name):
        formats = {
            'RAIN_scale': 'RAIN_scale {scale}',
            'RAIN_friction': 'RAIN_friction {dataref} {dry_coeff} {wet_coeff}',
            'THERMAL_texture': 'THERMAL_texture {texture_path}'
        }
        return formats.get(command_name, '')

class VersionManager:
    """Manages version strategies"""
    
    def __init__(self):
        self.strategies = {
            1000: XPlane10Strategy(),
            1100: XPlane11Strategy(),
            1200: XPlane12Strategy(),
            1210: XPlane12_1Strategy()
        }
    
    def get_strategy(self, version: int) -> VersionStrategy:
        """Get appropriate strategy for version"""
        # Find the highest version <= requested version
        available_versions = [v for v in self.strategies.keys() if v <= version]
        if not available_versions:
            raise ValueError(f"No strategy available for version {version}")
        
        best_version = max(available_versions)
        return self.strategies[best_version]
```

## Validation Framework

### Validation Architecture

The validation framework provides comprehensive, configurable validation:

```python
class ValidationLevel(Enum):
    """Validation levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    VERBOSE = "verbose"
    DEBUG = "debug"

class ValidationResult:
    """Container for validation results"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.debug = []
    
    def add_error(self, message: str, context: str = None):
        self.errors.append(ValidationMessage(message, context, MessageType.ERROR))
    
    def add_warning(self, message: str, context: str = None):
        self.warnings.append(ValidationMessage(message, context, MessageType.WARNING))
    
    def add_info(self, message: str, context: str = None):
        self.info.append(ValidationMessage(message, context, MessageType.INFO))
    
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.debug.extend(other.debug)

class BaseValidator:
    """Base class for all validators"""
    
    def __init__(self, level: ValidationLevel = ValidationLevel.STANDARD):
        self.level = level
        self.cache = {}
    
    def validate(self, target, context: 'ValidationContext') -> ValidationResult:
        """Main validation method"""
        # Check cache first
        cache_key = self.get_cache_key(target, context)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Perform validation
        result = self.perform_validation(target, context)
        
        # Cache result
        self.cache[cache_key] = result
        return result
    
    def perform_validation(self, target, context) -> ValidationResult:
        """Override in subclasses"""
        raise NotImplementedError
    
    def get_cache_key(self, target, context) -> str:
        """Generate cache key for validation"""
        return f"{type(target).__name__}_{hash(str(target))}"

class CompositeValidator(BaseValidator):
    """Validator that combines multiple validators"""
    
    def __init__(self, validators: List[BaseValidator], level: ValidationLevel = ValidationLevel.STANDARD):
        super().__init__(level)
        self.validators = validators
    
    def perform_validation(self, target, context):
        result = ValidationResult()
        
        for validator in self.validators:
            validator_result = validator.validate(target, context)
            result.merge(validator_result)
            
            # Stop on first error if in minimal mode
            if self.level == ValidationLevel.MINIMAL and not validator_result.is_valid():
                break
        
        return result
```

### Feature-Specific Validators

Each feature implements its own validation logic:

```python
class RainSystemValidator(BaseValidator):
    """Validator for rain system features"""
    
    def perform_validation(self, rain_props, context):
        result = ValidationResult()
        
        # Version compatibility check
        if context.xplane_version < 1200:
            result.add_warning("Rain system requires X-Plane 12.0+")
            return result
        
        # Rain scale validation
        if hasattr(rain_props, 'rain_scale'):
            if rain_props.rain_scale < 0.0 or rain_props.rain_scale > 1.0:
                result.add_error(f"Rain scale must be between 0.0 and 1.0, got {rain_props.rain_scale}")
        
        # Rain friction validation
        if getattr(rain_props, 'rain_friction_enabled', False):
            if not getattr(rain_props, 'rain_friction_dataref', ''):
                result.add_error("Rain friction enabled but no dataref specified")
            
            dry_coeff = getattr(rain_props, 'rain_friction_dry_coefficient', 1.0)
            wet_coeff = getattr(rain_props, 'rain_friction_wet_coefficient', 0.3)
            
            if dry_coeff <= 0.0:
                result.add_error("Rain friction dry coefficient must be positive")
            if wet_coeff <= 0.0:
                result.add_error("Rain friction wet coefficient must be positive")
            if wet_coeff >= dry_coeff:
                result.add_warning("Wet coefficient should typically be less than dry coefficient")
        
        return result

class MaterialValidator(BaseValidator):
    """Validator for material system"""
    
    def perform_validation(self, material, context):
        result = ValidationResult()
        
        # PBR workflow validation
        if hasattr(material, 'use_nodes') and material.use_nodes:
            pbr_nodes = self.detect_principled_bsdf(material)
            if pbr_nodes:
                result.add_info(f"Detected {len(pbr_nodes)} Principled BSDF node(s)")
                
                # Validate node connections
                for node in pbr_nodes:
                    if not node.inputs['Base Color'].is_linked:
                        result.add_warning("Principled BSDF Base Color not connected")
        
        # Texture validation
        texture_paths = self.extract_texture_paths(material)
        for texture_path in texture_paths:
            if not os.path.exists(texture_path):
                result.add_error(f"Texture file not found: {texture_path}")
        
        return result
```

## Export Pipeline Architecture

### Pipeline Overview

The export pipeline processes objects through multiple stages:

```python
class ExportPipeline:
    """Main export pipeline coordinator"""
    
    def __init__(self, context: 'ExportContext'):
        self.context = context
        self.stages = [
            ValidationStage(),
            PreprocessingStage(),
            GeometryProcessingStage(),
            MaterialProcessingStage(),
            CommandGenerationStage(),
            OptimizationStage(),
            OutputStage()
        ]
    
    def execute(self, objects: List[bpy.types.Object]) -> 'ExportResult':
        """Execute the export pipeline"""
        pipeline_data = PipelineData(objects, self.context)
        
        for stage in self.stages:
            try:
                stage.execute(pipeline_data)
                if pipeline_data.should_abort():
                    break
            except Exception as e:
                pipeline_data.add_error(f"Stage {stage.name} failed: {str(e)}")
                break
        
        return pipeline_data.get_result()

class PipelineStage:
    """Base class for pipeline stages"""
    
    def __init__(self, name: str):
        self.name = name
    
    def execute(self, data: 'PipelineData'):
        """Execute this stage"""
        raise NotImplementedError

class ValidationStage(PipelineStage):
    """Validation stage of the pipeline"""
    
    def __init__(self):
        super().__init__("Validation")
        self.validator = CompositeValidator([
            GeometryValidator(),
            MaterialValidator(),
            LightingValidator(),
            WeatherValidator(),
            StateValidator()
        ])
    
    def execute(self, data):
        for obj in data.objects:
            validation_result = self.validator.validate(obj, data.context)
            data.add_validation_result(obj, validation_result)
            
            if not validation_result.is_valid() and data.context.strict_validation:
                data.abort(f"Validation failed for object {obj.name}")

class CommandGenerationStage(PipelineStage):
    """Command generation stage"""
    
    def __init__(self):
        super().__init__("Command Generation")
        self.generators = {
            'GEOMETRY': GeometryCommandGenerator(),
            'LIGHTING': LightingCommandGenerator(),
            'MATERIAL': MaterialCommandGenerator(),
            'WEATHER': WeatherCommandGenerator(),
            'STATE': StateCommandGenerator()
        }
    
    def execute(self, data):
        for obj in data.objects:
            for generator_type, generator in self.generators.items():
                if generator.can_process(obj):
                    commands = generator.generate_commands(obj, data.context)
                    data.add_commands(obj, commands)
```

### Command Generation Architecture

Commands are generated through specialized generators:

```python
class CommandGenerator:
    """Base class for command generators"""
    
    def can_process(self, obj: bpy.types.Object) -> bool:
        """Check if this generator can process the object"""
        raise NotImplementedError
    
    def generate_commands(self, obj: bpy.types.Object, context: 'ExportContext') -> List[XPlaneCommand]:
        """Generate commands for the object"""
        raise NotImplementedError

class GeometryCommandGenerator(CommandGenerator):
    """Generator for geometry commands"""
    
    def can_process(self, obj):
        return obj.type == 'MESH' and hasattr(obj.data, 'xplane_geometry_type')
    
    def generate_commands(self, obj, context):
        commands = []
        geometry_type = obj.data.xplane_geometry_type
        
        if geometry_type == 'LINES':
            commands.extend(self.generate_lines_commands(obj, context))
        elif geometry_type == 'LINE_STRIP':
            commands.extend(self.generate_line_strip_commands(obj, context))
        elif geometry_type == 'QUAD_STRIP':
            commands.extend(self.generate_quad_strip_commands(obj, context))
        elif geometry_type == 'FAN':
            commands.extend(self.generate_fan_commands(obj, context))
        
        return commands
    
    def generate_lines_commands(self, obj, context):
        """Generate LINES commands with VLINE vertex table"""
        commands = []
        
        # Generate VLINE commands for vertices
        for vertex in obj.data.vertices:
            world_pos = obj.matrix_world @ vertex.co
            xplane_pos = self.convert_to_xplane_coords(world_pos)
            commands.append(VLineCommand(xplane_pos))
        
        # Generate LINES command with indices
        edge_indices = [(edge.vertices[0], edge.vertices[1]) for edge in obj.data.edges]
        commands.append(LinesCommand(edge_indices))
        
        return commands

class LightingCommandGenerator(CommandGenerator):
    """Generator for lighting commands"""
    
    def can_process(self, obj):
        return (obj.type == 'EMPTY' and 
                hasattr(obj.xplane, 'special_empty_props') and
                obj.xplane.special_empty_props.special_type in ['LIGHT_CONE', 'LIGHT_BILLBOARD'])
    
    def generate_commands(self, obj, context):
        light_props = obj.xplane.special_empty_props.light_props
        light_type = obj.xplane.special_empty_props.special_type
        
        position = self.get_world_position(obj)
        direction = self.get_world_direction(obj)
        
        if light_type == 'LIGHT_CONE':
            return [LightConeCommand(
                position=position,
                direction=direction,
                color=light_props.color,
                angle=light_props.cone_angle,
                intensity=light_props.intensity
            )]
        elif light_type == 'LIGHT_BILLBOARD':
            return [LightBillboardCommand(
                position=position,
                direction=direction,
                color=light_props.color,
                size=light_props.billboard_size
            )]
        
        return []
```

## Property System Design

### Property Group Architecture

The property system uses hierarchical property groups:

```python
class XPlanePropertyGroup(bpy.types.PropertyGroup):
    """Base class for all X-Plane property groups"""
    
    def __init__(self):
        super().__init__()
        self.validation_cache = {}
        self.observers = []
    
    def validate(self, context: 'ValidationContext') -> ValidationResult:
        """Validate this property group"""
        validator = self.get_validator()
        return validator.validate(self, context)
    
    def get_validator(self) -> BaseValidator:
        """Get appropriate validator for this property group"""
        raise NotImplementedError
    
    def on_property_update(self, property_name: str, context):
        """Called when a property is updated"""
        # Clear validation cache
        self.validation_cache.clear()
        
        # Notify observers
        for observer in self.observers:
            observer.on_property_changed(property_name, self, context)

class XPlaneGeometrySettings(XPlanePropertyGroup):
    """Property group for geometry settings"""
    
    geometry_type: EnumProperty(
        name="Geometry Type",
        description="Type of geometry to export",
        items=[
            ('TRIS', 'Triangles', 'Standard triangle geometry'),
            ('LINES', 'Lines', 'Line geometry with VLINE support'),
            ('LINE_STRIP', 'Line Strip', 'Connected line sequences'),
            ('QUAD_STRIP', 'Quad Strip', 'Quad strip geometry'),
            ('FAN', 'Fan', 'Triangle fan geometry')
        ],
        default='TRIS',
        update=lambda self, context: self.on_property_update('geometry_type', context)
    )
    
    enable_vline: BoolProperty(
        name="Enable VLINE",
        description="Use VLINE vertex table for line geometry",
        default=True,
        update=lambda self, context: self.on_property_update('enable_vline', context)
    )
    
    def get_validator(self):
        return GeometryValidator()

class XPlaneLightingSettings(XPlanePropertyGroup):
    """Property group for lighting settings"""
    
    light_type: EnumProperty(
        name="Light Type",
        description="Type of light to create",
        items=[
            ('POINT', 'Point Light', 'Standard point light'),
            ('CONE', 'Cone Light', 'Directional cone light'),
            ('BILLBOARD', 'Billboard Light', 'Billboard-style light')
        ],
        default='POINT',
        update=lambda self, context: self.on_property_update('light_type', context)
    )
    
    color: FloatVectorProperty(
        name="Color",
        description="Light color (RGB)",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=lambda self, context: self.on_property_update('color', context)
    )
    
    intensity: FloatProperty(
        name="Intensity",
        description="Light intensity",
        min=0.0,
        max=10.0,
        default=1.0,
        update=lambda self, context: self.on_property_update('intensity', context)
    )
    
    cone_angle: FloatProperty(
        name="Cone Angle",
        description="Cone light angle in degrees",
        min=0.0,
        max=180.0,
        default=45.0,
        update=lambda self, context: self.on_property_update('cone_angle', context)
    )
    
    def get_validator(self):
        return LightingValidator()
```

### Dynamic Property Registration

Properties are registered dynamically based on available features:

```python
class PropertyRegistrar:
    """Manages dynamic property registration"""
    
    def __init__(self):
        self.registered_properties = {}
        self.feature_properties = {}
    
    def register_feature_properties(self, feature_name: str, property_class: type):
        """Register properties for a feature"""
        self.feature_properties[feature_name] = property_class
        
        # Register with Blender
        bpy.utils.register_class(property_class)
        self.registered_properties[feature_name] = property_class
    
    def unregister_feature_properties(self, feature_name: str):
        """Unregister properties for a feature"""
        if feature_name in self.registered_properties:
            property_class = self.registered_properties[feature_name]
            bpy.utils.unregister_class(property_class)
            del self.registered_properties[feature_name]
    
    def get_feature_properties(self, feature_name: str) -> type:
        """Get property class for a feature"""
        return self.feature_properties.get(feature_name)

# Global property registrar
property_registrar = PropertyRegistrar()

def register_properties():
    """Register all X-Plane properties"""
    # Core properties
    property_registrar.register_feature_properties('geometry', XPlaneGeometrySettings)
    property_registrar.register_feature_properties('lighting', XPlaneLightingSettings)
    property_registrar.register_feature_properties('materials', XPlaneMaterialSettings)
    
    # Feature-specific properties
    property_registrar.register_feature_properties('rain', XPlaneRainSettings)
    property_registrar.register_feature_properties('thermal', XPlaneThermalSettings)
    property_registrar.register_feature_properties('wiper', XPlaneWiperSettings)
```

## UI Integration Patterns

### Panel Architecture

UI panels follow a consistent pattern:

```python
class XPlanePanelBase(bpy.types.Panel):
    """Base class for X-Plane panels"""
    
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        """Panel visibility condition"""
        return (context.object is not None and 
                hasattr(context.object, 'xplane'))
    
    def draw_header(self, context):
        """Draw panel header"""
        layout = self.layout
        layout.label(text=self.bl_label, icon=self.get_icon())
    
    def draw(self, context):
        """Draw panel content"""
        layout = self.layout
        obj = context.object
        
        if not self.is_available(obj):
            layout.label(text="Not available for this object type")
            return
        
        self.draw_content(layout, obj, context)
    
    def get_icon(self) -> str:
        """Get panel icon"""
        return 'NONE'
    
    def is_available(self, obj: bpy.types.Object) -> bool:
        """Check if panel is available for object"""
        return True
    
    def draw_content(self, layout, obj, context):
        """Draw panel content - override in subclasses"""
        pass

class XPlaneGeometryPanel(XPlanePanelBase):
    """Panel for geometry settings"""
    
    bl_idname = "OBJECT_PT_xplane_geometry"
    bl_label = "Geometry Commands"
    bl_parent_id = "OBJECT_PT_xplane"
    
    def get_icon(self):
        return 'MESH_DATA'
    
    def is_available(self, obj):
        return obj.type == 'MESH'
    
    def draw_content(self, layout, obj, context):
        geometry_props = obj.xplane.geometry
        
        # Geometry type selection
        layout.prop(geometry_props, 'geometry_type')
        
        # Type-specific settings
        if geometry_props.geometry_type in ['LINES', 'LINE_STRIP']:
            layout.prop(geometry_props, 'enable_vline')
        
        # Validation feedback
        self.draw_validation_feedback(layout, geometry_props, context)
    
    def draw_validation_feedback(self, layout, props, context):
        """Draw validation feedback"""
        validation_result = props.validate(context)
        
        if validation_result.errors:
            box = layout.box()
            box.alert = True
            for error in validation_result.errors:
                box.label(text=error.message, icon='ERROR')
        
        if validation_result.warnings:
            box = layout.box()
            for warning in validation_result.warnings:
                box.label(text=warning.message, icon='INFO')

class XPlaneWeatherPanel(XPlanePanelBase):
    """Panel for weather system settings"""
    
    bl_idname = "OBJECT_PT_xplane_weather"
    bl_label = "Weather System (X-Plane 12+)"
    bl_parent_id = "OBJECT_PT_xplane"
    
    def get_icon(self):
        return 'WORLD'
    
    def is_available(self, obj):
        return (hasattr(obj.xplane, 'layer') and 
                obj.xplane.layer.export_type == 'AIRCRAFT')
    
    def draw_content(self, layout, obj, context):
        rain_props = obj.xplane.layer.rain
        
        # Rain system
        box = layout.box()
        box.label(text="Rain System", icon='WORLD')
        box.prop(rain_props, 'rain_scale')
        
        # Rain friction
        box.prop(rain_props, 'rain_friction_enabled')
        if rain_props.rain_friction_enabled:
            col = box.column()
            col.prop(rain_props, 'rain_friction_dataref')
            col.prop(rain_props, 'rain_friction_dry_coefficient')
            col.prop(rain_props, 'rain_friction_wet_coefficient')
        
        # Thermal system
        box = layout.box()
        box.label(text="Thermal System", icon='OUTLINER_OB_LIGHT')
        box.prop(rain_props, 'thermal_texture')
        
        # Thermal sources
        for i in range(1, 5):
            enabled_prop = f'thermal_source_{i}_enabled'
            if hasattr(rain_props, enabled_prop):
                box.prop(rain_props, enabled_prop, text=f"Thermal Source {i}")
```

### Operator Patterns

Operators follow consistent patterns for user actions:

```python
class XPlaneOperatorBase(bpy.types.Operator):
    """Base class for X-Plane operators"""
    
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the operator"""
        try:
            result = self.perform_operation(context)
            if result:
                self.report({'INFO'}, self.get_success_message())
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, self.get_error_message())
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Operation failed: {str(e)}")
            return {'CANCELLED'}
    
    def perform_operation(self, context) -> bool:
        """Perform the actual operation - override in subclasses"""
        raise NotImplementedError
    
    def get_success_message(self) -> str:
        """Get success message"""
        return "Operation completed successfully"