# Landing Gear System Documentation

## Overview

The XPlane2Blender Landing Gear System provides comprehensive support for X-Plane 12+ landing gear configuration, including automatic detection, validation, animation integration, and export functionality.

## Features

### Core Functionality
- **Automatic Gear Detection**: Intelligent detection of gear types from object names and hierarchy
- **Comprehensive Validation**: Extensive validation of gear configurations and settings
- **Animation Integration**: Support for retraction and door animations
- **Export Compatibility**: Full integration with X-Plane 12+ ATTR_landing_gear directive
- **Multiple Configurations**: Support for tricycle, taildragger, and custom gear setups

### Enhanced Properties
- **Gear Type Classification**: Automatic classification of nose, main, tail, and custom gear
- **Index Management**: Automatic and manual gear/wheel index assignment
- **Animation Settings**: Retraction and door animation configuration
- **Validation Controls**: Configurable validation and error reporting

## Usage

### Basic Setup

1. **Create Empty Object**: Add an Empty object where you want the landing gear
2. **Set Special Type**: Set the Empty's special type to "Wheel"
3. **Configure Properties**: Set gear type, indices, and animation settings
4. **Enable Auto-Detection**: Optionally enable automatic configuration

### Gear Types

#### Standard Gear Types
- **Nose Gear**: Front landing gear (gear_index = 0)
- **Main Left**: Left main landing gear (gear_index = 1)
- **Main Right**: Right main landing gear (gear_index = 2)
- **Tail Gear**: Rear landing gear for taildraggers (gear_index = 3)
- **Custom**: User-defined gear configuration

#### Gear Configurations
- **Tricycle**: Nose + Main Left + Main Right
- **Taildragger**: Main Left + Main Right + Tail
- **Complex**: Multiple wheels per gear, custom arrangements

### Properties Reference

#### Basic Properties
```
gear_index: int (0-15)
    Landing gear index (0=nose, 1=left main, 2=right main, etc.)

wheel_index: int (0-7)
    Wheel index within the gear (0=first wheel, 1=second wheel, etc.)

gear_type: enum
    Type of landing gear (NOSE, MAIN_LEFT, MAIN_RIGHT, TAIL, CUSTOM)

auto_detect_gear: bool
    Automatically detect gear type and index from object hierarchy and naming
```

#### Animation Properties
```
enable_retraction: bool
    Enable gear retraction animation

retraction_dataref: string
    Dataref controlling gear retraction (0=extended, 1=retracted)
    Default: "sim/aircraft/parts/acf_gear_retract"

enable_doors: bool
    Enable gear door animation

door_dataref: string
    Dataref controlling gear door position (0=closed, 1=open)
    Default: "sim/aircraft/parts/acf_gear_door"
```

#### Validation Properties
```
validation_enabled: bool
    Enable landing gear validation and error checking

show_advanced: bool
    Show advanced landing gear configuration options
```

### Auto-Detection

The system automatically detects gear configuration based on:

#### Naming Patterns
- **nose**, **front** → Nose Gear
- **main_left**, **main_l**, **left_main**, **left** → Main Left
- **main_right**, **main_r**, **right_main**, **right** → Main Right
- **tail**, **rear** → Tail Gear

#### Spatial Position
- Forward position (Y > 0.5) → Nose Gear
- Rear position (Y < -0.5) → Tail Gear
- Left position (X < -0.1) → Main Left
- Right position (X > 0.1) → Main Right

#### Hierarchy Analysis
- Parent object names containing gear-related keywords
- Sibling relationships for door detection

### Validation System

#### Automatic Validation
- Gear index range validation (0-15)
- Wheel index range validation (0-7)
- Dataref format validation
- Configuration consistency checks
- Scene-wide gear analysis

#### Error Types
- **Errors**: Critical issues that prevent proper export
- **Warnings**: Potential issues that should be reviewed
- **Info**: Informational messages about configuration

#### Common Validation Issues
- Invalid gear/wheel indices
- Duplicate gear indices
- Missing datarefs for animation
- Inconsistent gear type assignments
- Unbalanced gear configurations

### Animation Integration

#### Retraction Animation
```python
# Enable retraction
wheel_props.enable_retraction = True
wheel_props.retraction_dataref = "sim/aircraft/parts/acf_gear_retract"

# Create animation keyframes
# Extended position at frame 1
# Retracted position at frame 30
```

#### Door Animation
```python
# Enable doors
wheel_props.enable_doors = True
wheel_props.door_dataref = "sim/aircraft/parts/acf_gear_door"

# Door objects detected automatically from hierarchy
# or can be manually configured
```

#### Complex Animations
- Multi-stage retraction sequences
- Rotating gear mechanisms
- Folding gear assemblies
- Coordinated gear and door movement

### Export Format

The system exports X-Plane 12+ compatible ATTR_landing_gear directives:

```
ATTR_landing_gear <x> <y> <z> <phi> <theta> <psi> <gear_index> <wheel_index>
```

Where:
- `x, y, z`: Position coordinates in X-Plane coordinate system
- `phi, theta, psi`: Rotation angles (yaw, pitch, roll) in degrees
- `gear_index`: Landing gear index (0-based)
- `wheel_index`: Wheel index within gear (0-based)

### API Reference

#### Detection Functions
```python
from io_xplane2blender.xplane_utils.xplane_gear_detection import (
    detect_gear_configuration,
    apply_auto_configuration,
    detect_all_gear_in_scene
)

# Detect single gear
result = detect_gear_configuration(gear_object)

# Apply auto-configuration
success = apply_auto_configuration(gear_object)

# Detect all gear in scene
all_gear = detect_all_gear_in_scene()
```

#### Validation Functions
```python
from io_xplane2blender.xplane_utils.xplane_gear_validation import (
    validate_gear_object,
    validate_scene_gear_configuration,
    get_gear_configuration_recommendations
)

# Validate single gear
result = validate_gear_object(gear_object)

# Validate entire scene
scene_result = validate_scene_gear_configuration()

# Get recommendations
recommendations = get_gear_configuration_recommendations()
```

#### Animation Functions
```python
from io_xplane2blender.xplane_utils.xplane_gear_animation import (
    detect_gear_animation,
    create_retraction_animation,
    validate_animation_compatibility
)

# Detect animation setup
setup = detect_gear_animation(gear_object)

# Create retraction animation
success = create_retraction_animation(
    gear_object, 
    extended_position, 
    retracted_position
)

# Validate animation
issues = validate_animation_compatibility(gear_object)
```

### Best Practices

#### Naming Conventions
- Use descriptive names: `nose_gear`, `main_left_gear`, `tail_wheel`
- Include gear type in name for auto-detection
- Use consistent naming across related objects

#### Positioning
- Position gear objects at wheel contact points
- Use realistic spacing for aircraft type
- Consider ground clearance and stability

#### Animation Setup
- Create smooth retraction sequences
- Coordinate gear and door animations
- Test animation timing and datarefs

#### Validation
- Enable validation during development
- Review and address all warnings
- Test with different gear configurations

### Troubleshooting

#### Common Issues

**Auto-detection not working**
- Check object naming conventions
- Verify object is set as Empty with Wheel type
- Enable auto_detect_gear property

**Validation errors**
- Check gear/wheel index ranges (0-15, 0-7)
- Ensure unique gear indices
- Verify dataref format for animations

**Export issues**
- Confirm X-Plane version is 1210 or higher
- Check export type is set to Aircraft
- Verify gear objects are in export hierarchy

**Animation problems**
- Check dataref paths are correct
- Verify animation keyframes exist
- Test dataref values in X-Plane

#### Debug Information
Enable debug mode to see detailed information:
```python
from io_xplane2blender.xplane_config import setDebug
setDebug(True)
```

### Version Compatibility

- **X-Plane 12.10+**: Full ATTR_landing_gear support
- **X-Plane 11.30+**: Limited compatibility (no ATTR_landing_gear)
- **Blender 2.80+**: Full feature support
- **XPlane2Blender 4.0+**: Complete integration

### Examples

#### Simple Tricycle Gear
```python
# Create nose gear
nose_gear = create_gear_empty("nose_gear", (0, 2, -1))
nose_gear.xplane.special_empty_props.wheel_props.gear_type = "NOSE"
nose_gear.xplane.special_empty_props.wheel_props.gear_index = 0

# Create main gears
main_left = create_gear_empty("main_left", (-2, 0, -1))
main_left.xplane.special_empty_props.wheel_props.gear_type = "MAIN_LEFT"
main_left.xplane.special_empty_props.wheel_props.gear_index = 1

main_right = create_gear_empty("main_right", (2, 0, -1))
main_right.xplane.special_empty_props.wheel_props.gear_type = "MAIN_RIGHT"
main_right.xplane.special_empty_props.wheel_props.gear_index = 2
```

#### Retractable Gear with Doors
```python
# Create retractable nose gear
nose_gear = create_gear_empty("retractable_nose", (0, 2, -1))
wheel_props = nose_gear.xplane.special_empty_props.wheel_props

# Enable retraction
wheel_props.enable_retraction = True
wheel_props.retraction_dataref = "sim/aircraft/parts/acf_gear_retract"

# Enable doors
wheel_props.enable_doors = True
wheel_props.door_dataref = "sim/aircraft/parts/acf_gear_door"
```

### Testing

The system includes comprehensive test suites:

- **Unit Tests**: Individual component testing
- **Integration Tests**: System-wide functionality
- **Export Tests**: X-Plane compatibility verification
- **Validation Tests**: Error detection and reporting

Run tests with:
```bash
python -m pytest tests/features/landing_gear/
```

### Contributing

When contributing to the landing gear system:

1. Follow existing code patterns and conventions
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Validate with multiple gear configurations
5. Test export compatibility with X-Plane

### Support

For issues and questions:
- Check validation messages and recommendations
- Review debug output for detailed information
- Consult test cases for usage examples
- Report bugs with detailed reproduction steps