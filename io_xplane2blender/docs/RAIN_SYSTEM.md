# Rain/Weather System for X-Plane 12+

This document describes the comprehensive Rain/Weather System implementation in XPlane2Blender for X-Plane 12 and later versions.

## Overview

The Rain/Weather System provides advanced rain effects, thermal anti-icing, and windshield wiper functionality for aircraft models. This system is designed specifically for X-Plane 12+ and includes extensive validation and optimization features.

## Features

### 1. Basic Rain Settings

#### Rain Scale
- **Property**: `rain_scale`
- **Range**: 0.1 - 1.0
- **Default**: 1.0
- **Description**: Scales the visual output of rain to match texture resolution
- **Export**: `RAIN_scale` directive (only exported if < 1.0)

### 2. Rain Friction System (X-Plane 12+)

The rain friction system allows surfaces to have different friction coefficients when wet vs dry.

#### Properties
- **Enable Rain Friction**: `rain_friction_enabled`
- **Rain Friction Dataref**: `rain_friction_dataref`
- **Dry Friction Coefficient**: `rain_friction_dry_coefficient` (0.0 - 2.0, default: 1.0)
- **Wet Friction Coefficient**: `rain_friction_wet_coefficient` (0.0 - 2.0, default: 0.3)

#### Export Format
```
RAIN_friction <dataref> <dry_coefficient> <wet_coefficient>
```

#### Example
```
RAIN_friction sim/weather/rain_percent 1.000 0.300
```

### 3. Thermal Anti-Icing System (X-Plane 12.1+)

The thermal system provides realistic windshield and window defogging/deicing effects.

#### Basic Properties
- **Thermal Texture**: `thermal_texture` - Path to thermal effect texture
- **Thermal Sources**: Up to 4 configurable thermal sources

#### Advanced Management Features
- **Auto-validation**: `thermal_auto_validation` - Automatically validate configurations
- **Defrost Optimization**: `thermal_defrost_optimization` - Optimize defrost calculations
- **Source Priority**: `thermal_source_priority` - Control activation order
  - `sequential`: Activate sources in order 1-4
  - `priority`: Activate based on importance (lower numbers = higher priority)
  - `simultaneous`: All sources can be active simultaneously

#### Thermal Source Configuration
Each thermal source (1-4) has:
- **Enabled**: Enable/disable the source
- **Defrost Time**: Time in seconds or dataref for defrost duration
- **On/Off Dataref**: Dataref controlling source activation

#### Export Format
```
THERMAL_texture <texture_path>
THERMAL_source2 <source_index> <defrost_time> <on_off_dataref>
```

### 4. Wiper System (X-Plane 12+)

Advanced windshield wiper system with texture baking and optimization.

#### Basic Properties
- **Wiper Texture**: `wiper_texture` - Path to wiper gradient texture
- **Exterior Glass Object**: `wiper_ext_glass_object` - Blender object for texture baking

#### Texture Baking Optimization
- **Bake Resolution**: `wiper_bake_resolution`
  - 512x512 (Low, for testing)
  - 1024x1024 (Standard)
  - 2048x2048 (High)
  - 4096x4096 (Ultra high)
- **Bake Quality**: `wiper_bake_quality`
  - Draft (Fast, lower quality)
  - Standard (Balanced)
  - High (High quality, slower)
  - Ultra (Maximum quality, very slow)
- **Antialiasing**: `wiper_bake_antialiasing` - Smooth wiper edges
- **Auto-optimize**: `wiper_auto_optimize` - Optimize animation paths

#### Wiper Configuration
Each wiper (1-4) has:
- **Enabled**: Enable/disable the wiper
- **Object Name**: Blender object for texture baking
- **Dataref**: Animation control dataref
- **Start/End Values**: Animation range
- **Nominal Width**: Wiper thickness (0.0 - 1.0)

#### Export Format
```
WIPER_texture <texture_path>
WIPER_param <dataref> <start> <end> <nominal_width>
```

### 5. Comprehensive Validation System

The validation system provides extensive checking and error reporting.

#### Validation Settings
- **Enable Validation**: `validation_enabled` - Master validation toggle
- **Strict Mode**: `validation_strict_mode` - Treat warnings as errors
- **Error Reporting Level**: `error_reporting_level`
  - Minimal: Only critical errors
  - Standard: Errors and important warnings
  - Verbose: All errors, warnings, and info
  - Debug: All messages including debug info

#### Validation Checks
- **Dataref Validation**: `validation_check_datarefs` - Validate dataref formats
- **Texture Validation**: `validation_check_textures` - Check texture file paths
- **Object Validation**: `validation_check_objects` - Verify Blender object references
- **Performance Warnings**: `validation_performance_warnings` - Performance impact alerts

## Usage Examples

### Basic Rain Setup
```python
# Enable basic rain scaling
rain_props.rain_scale = 0.8
```

### Rain Friction Setup
```python
# Enable rain friction effects
rain_props.rain_friction_enabled = True
rain_props.rain_friction_dataref = "sim/weather/rain_percent"
rain_props.rain_friction_dry_coefficient = 1.0
rain_props.rain_friction_wet_coefficient = 0.3
```

### Thermal System Setup
```python
# Configure thermal anti-icing
rain_props.thermal_texture = "thermal_effects.png"
rain_props.thermal_source_priority = "priority"
rain_props.thermal_defrost_optimization = True

# Configure pilot windshield thermal source
rain_props.thermal_source_1_enabled = True
rain_props.thermal_source_1.defrost_time = "30.0"
rain_props.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_pilot"
```

### Wiper System Setup
```python
# Configure wiper system
rain_props.wiper_texture = "wiper_gradient.png"
rain_props.wiper_ext_glass_object = "Windshield"
rain_props.wiper_bake_resolution = "2048"
rain_props.wiper_bake_quality = "high"
rain_props.wiper_auto_optimize = True

# Configure pilot wiper
rain_props.wiper_1_enabled = True
rain_props.wiper_1.object_name = "Wiper_Pilot"
rain_props.wiper_1.dataref = "sim/cockpit/electrical/wiper_pilot"
rain_props.wiper_1.start = 0.0
rain_props.wiper_1.end = 1.0
rain_props.wiper_1.nominal_width = 0.01
```

## Validation and Error Handling

The system includes comprehensive validation that checks:

1. **Configuration Validity**
   - Required properties are set
   - Value ranges are within limits
   - Dependencies are satisfied

2. **Dataref Format Validation**
   - Basic format checking
   - Common prefix validation
   - Custom dataref warnings

3. **File Path Validation**
   - Texture file existence
   - File format validation
   - Relative path resolution

4. **Performance Analysis**
   - High-resolution texture warnings
   - Multiple source/wiper impact
   - Optimization suggestions

5. **Object Reference Validation**
   - Blender object existence
   - Naming consistency
   - Reference integrity

## Performance Considerations

### Thermal Sources
- Multiple thermal sources may impact performance on lower-end systems
- Use `sequential` or `priority` activation for better performance
- Enable `thermal_defrost_optimization` for improved calculations

### Wiper System
- Higher resolution textures (4K) may impact performance
- Ultra quality baking is very slow but provides best results
- Auto-optimization can improve runtime performance

### Validation
- Disable validation in production builds for better performance
- Use `minimal` error reporting for release versions
- Enable debug mode only during development

## Troubleshooting

### Common Issues

1. **Rain friction not working**
   - Ensure X-Plane version is 12.0+
   - Verify dataref is valid and accessible
   - Check coefficient ranges (0.0 - 2.0)

2. **Thermal system not activating**
   - Requires X-Plane 12.1+
   - Thermal texture must be specified
   - At least one thermal source must be enabled

3. **Wiper texture baking fails**
   - Verify exterior glass object exists
   - Check Blender object names
   - Ensure sufficient memory for high-resolution baking

4. **Validation errors**
   - Check error reporting level settings
   - Verify all required properties are set
   - Review dataref format and accessibility

### Performance Issues

1. **Slow texture baking**
   - Reduce bake resolution
   - Use lower quality settings
   - Disable antialiasing for faster baking

2. **Runtime performance impact**
   - Reduce number of active thermal sources
   - Use lower resolution wiper textures
   - Enable optimization features

## API Reference

### Main Classes
- `XPlaneRainSettings`: Main rain system configuration
- `XPlaneThermalSourceSettings`: Individual thermal source configuration
- `XPlaneWiperSettings`: Individual wiper configuration
- `RainSystemValidator`: Comprehensive validation system

### Validation Functions
- `validate_rain_system()`: Main validation entry point
- `RainSystemValidator.validate_all()`: Complete system validation
- Individual validation methods for each subsystem

### Constants
All rain-related constants are defined in `xplane_constants.py`:
- `RAIN_SCALE_*`: Rain scale limits and defaults
- `RAIN_FRICTION_*`: Friction coefficient limits
- `THERMAL_*`: Thermal system constants
- `WIPER_*`: Wiper system constants

## Version Compatibility

- **X-Plane 12.0+**: Rain scale, wiper system, rain friction
- **X-Plane 12.1+**: Thermal anti-icing system
- **Legacy versions**: Not supported (modernization focus)

## Future Enhancements

Potential future improvements:
1. Advanced weather integration
2. Dynamic rain intensity effects
3. Ice accumulation simulation
4. Enhanced thermal modeling
5. Automatic wiper activation
6. Weather-based friction curves