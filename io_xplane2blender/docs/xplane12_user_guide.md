# X-Plane 12+ User Guide for XPlane2Blender

## Overview

This guide covers the new X-Plane 12+ features available in XPlane2Blender, including rain effects, thermal systems, wiper functionality, and enhanced material integration with Blender 4+.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Rain System](#rain-system)
3. [Thermal System](#thermal-system)
4. [Wiper System](#wiper-system)
5. [Landing Gear Enhancements](#landing-gear-enhancements)
6. [Blender 4+ Material Integration](#blender-4-material-integration)
7. [Workflow Examples](#workflow-examples)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Requirements

- **Blender**: 4.0+ (recommended: 4.4.3 or later)
- **X-Plane**: 12.0+ for full feature support
- **XPlane2Blender**: Latest version with X-Plane 12 support

### Enabling X-Plane 12 Features

1. Open your Blender project
2. Ensure XPlane2Blender addon is enabled
3. Select your exportable root object
4. Navigate to the **Object Properties** panel
5. Expand the **X-Plane** section
6. Set **Export Type** to **Aircraft** (required for most X-Plane 12 features)

## Rain System

The X-Plane 12 rain system provides realistic precipitation effects on aircraft surfaces.

### Rain Scale (RAIN_scale)

Controls the overall intensity of rain effects on your aircraft.

**Location**: Object Properties → X-Plane → Layer → Rain → Rain Scale

**Settings**:
- **Rain Scale**: Float value (0.0 - 1.0)
  - `0.0`: No rain effects
  - `0.5`: Moderate rain effects
  - `1.0`: Maximum rain effects

**Example**:
```
Rain Scale: 0.7  // 70% rain intensity
```

### Rain Friction (RAIN_friction)

Simulates the effect of rain on surface friction, particularly important for runway and ground vehicle interactions.

**Location**: Object Properties → X-Plane → Layer → Rain → Rain Friction

**Settings**:
- **Enable Rain Friction**: Checkbox to enable the system
- **Friction Dataref**: Custom dataref for rain intensity
- **Dry Coefficient**: Friction when dry (typically 1.0)
- **Wet Coefficient**: Friction when wet (typically 0.3-0.7)

**Example Configuration**:
```
Enable Rain Friction: ✓
Friction Dataref: sim/weather/rain_percent
Dry Coefficient: 1.0
Wet Coefficient: 0.3
```

**Common Datarefs**:
- `sim/weather/rain_percent`: Built-in X-Plane rain percentage
- `sim/weather/precipitation_on_aircraft_ratio`: Aircraft-specific precipitation
- Custom datarefs: Create your own for specific effects

## Thermal System

The thermal system simulates window defogging and heating effects.

### Thermal Texture (THERMAL_texture)

Specifies the texture used for thermal effects visualization.

**Location**: Object Properties → X-Plane → Layer → Rain → Thermal Texture

**Settings**:
- **Thermal Texture**: Path to thermal effect texture file

**Recommended Texture Specifications**:
- **Format**: PNG or DDS
- **Size**: 512x512 or 1024x1024
- **Channels**: RGBA (alpha for transparency effects)

### Thermal Sources

Configure up to 4 thermal sources for different window areas.

**Available Sources**:
1. **Pilot Side Window** (`thermal_source_1`)
2. **Copilot Side Window** (`thermal_source_2`)
3. **Front Window** (`thermal_source_3`)
4. **Additional Source** (`thermal_source_4`)

**Settings for Each Source**:
- **Enable**: Checkbox to activate the thermal source
- **Defrost Time**: Time in seconds for full defrost effect
- **On/Off Dataref**: Dataref controlling the thermal source state

**Example Configuration**:
```
Pilot Side Window:
  Enable: ✓
  Defrost Time: 30.0
  On/Off Dataref: sim/cockpit/electrical/thermal_pilot

Front Window:
  Enable: ✓
  Defrost Time: 45.0
  On/Off Dataref: sim/cockpit/electrical/thermal_front
```

## Wiper System

The wiper system provides realistic windshield wiper effects.

### Wiper Texture (WIPER_texture)

Specifies the gradient texture used for wiper effects.

**Location**: Object Properties → X-Plane → Layer → Rain → Wiper Texture

**Settings**:
- **Wiper Texture**: Path to wiper gradient texture

### Wiper Configuration

Configure up to 4 individual wipers with independent settings.

**Settings for Each Wiper**:
- **Enable**: Checkbox to activate the wiper
- **Object Name**: Name of the wiper object in your scene
- **Dataref**: Dataref controlling wiper position/animation
- **Nominal Width**: Width of the wiper blade effect (typically 0.001)

**Example Configuration**:
```
Wiper 1:
  Enable: ✓
  Object Name: wiper_pilot
  Dataref: sim/cockpit/wipers/wiper_pilot_position
  Nominal Width: 0.001

Wiper 2:
  Enable: ✓
  Object Name: wiper_copilot
  Dataref: sim/cockpit/wipers/wiper_copilot_position
  Nominal Width: 0.001
```

### Wiper Gradient Texture Generation

XPlane2Blender includes a built-in operator to generate wiper gradient textures.

**To Generate Wiper Texture**:
1. Navigate to Object Properties → X-Plane → Layer → Rain
2. Click **Bake Wiper Gradient Texture**
3. Configure texture parameters in the dialog
4. Save the generated texture to your aircraft's texture folder

## Landing Gear Enhancements

X-Plane 12 includes enhanced landing gear simulation capabilities.

### Gear Configuration

**Location**: Object Properties → X-Plane → Special Empty Props → Wheel Props

**Settings**:
- **Gear Type**: Type of landing gear
  - `NOSE`: Nose gear
  - `LEFT_MAIN`: Left main gear
  - `RIGHT_MAIN`: Right main gear
- **Gear Index**: Specific gear index for complex aircraft
- **Wheel Index**: Individual wheel index
- **Enable Retraction**: Allow gear retraction animation

**Example**:
```
Nose Gear:
  Gear Type: NOSE
  Gear Index: GEAR_INDEX_NOSE
  Wheel Index: 0
  Enable Retraction: ✓
```

## Blender 4+ Material Integration

XPlane2Blender provides seamless integration with Blender 4+ material nodes.

### Enabling Material Integration

**Location**: Object Properties → X-Plane → Layer → Texture Maps

**Settings**:
- **Blender Material Integration**: Enable automatic material detection
- **Auto-detect Principled BSDF**: Automatically find and use Principled BSDF nodes
- **Auto-detect Normal Map Nodes**: Automatically detect normal map connections
- **Auto-detect Image Texture Nodes**: Automatically find texture nodes

### Supported Node Types

**Automatically Detected**:
- **Principled BSDF**: Main material shader
- **Image Texture**: Diffuse, normal, and other texture maps
- **Normal Map**: Normal mapping nodes
- **ColorRamp**: Color gradients and adjustments
- **Mix**: Color and factor mixing

### Material Workflow

1. **Create Material**: Add a new material to your object
2. **Enable Nodes**: Ensure "Use Nodes" is enabled
3. **Build Node Tree**: Create your material using Blender 4+ nodes
4. **Enable Integration**: Turn on Blender Material Integration
5. **Export**: XPlane2Blender will automatically convert compatible nodes

**Example Node Setup**:
```
Image Texture (Diffuse) → Principled BSDF → Material Output
Image Texture (Normal) → Normal Map → Principled BSDF (Normal)
```

## Workflow Examples

### Complete Aircraft Rain Setup

1. **Configure Rain Scale**:
   ```
   Rain Scale: 0.8
   ```

2. **Setup Rain Friction**:
   ```
   Enable Rain Friction: ✓
   Friction Dataref: sim/weather/rain_percent
   Dry Coefficient: 1.0
   Wet Coefficient: 0.4
   ```

3. **Configure Thermal System**:
   ```
   Thermal Texture: thermal_effects.png
   
   Pilot Side Window:
     Enable: ✓
     Defrost Time: 30.0
     On/Off Dataref: sim/cockpit/electrical/thermal_pilot
   
   Front Window:
     Enable: ✓
     Defrost Time: 45.0
     On/Off Dataref: sim/cockpit/electrical/thermal_front
   ```

4. **Setup Wipers**:
   ```
   Wiper Texture: wiper_gradient.png
   
   Pilot Wiper:
     Enable: ✓
     Object Name: wiper_pilot_obj
     Dataref: sim/cockpit/wipers/wiper_pilot_position
     Nominal Width: 0.001
   ```

### Material Integration Workflow

1. **Create Blender 4+ Material**:
   - Add new material
   - Enable "Use Nodes"
   - Add Image Texture nodes for diffuse, normal, specular

2. **Connect Nodes**:
   ```
   Diffuse Texture → Principled BSDF (Base Color)
   Normal Texture → Normal Map → Principled BSDF (Normal)
   Roughness Texture → Principled BSDF (Roughness)
   ```

3. **Enable Integration**:
   - Object Properties → X-Plane → Layer → Texture Maps
   - Enable "Blender Material Integration"
   - Enable auto-detection options

4. **Export**: XPlane2Blender automatically converts the node tree

## Troubleshooting

### Common Issues

**Rain Effects Not Visible**:
- Ensure X-Plane version is 12.0+
- Check that Rain Scale > 0.0
- Verify export type is set to "Aircraft"

**Thermal System Not Working**:
- Confirm thermal texture exists and is accessible
- Check dataref names for typos
- Ensure defrost time is > 0.0

**Wiper Animation Issues**:
- Verify wiper object names match scene objects
- Check dataref connections in X-Plane
- Ensure nominal width is appropriate (typically 0.001)

**Material Integration Problems**:
- Confirm Blender version is 4.0+
- Check that "Use Nodes" is enabled on materials
- Verify Principled BSDF nodes are present
- Enable auto-detection options

### Validation Messages

XPlane2Blender includes comprehensive validation for X-Plane 12 features:

**Error Types**:
- **Configuration Errors**: Invalid property values
- **Missing Resources**: Textures or objects not found
- **Compatibility Issues**: Features not supported in target X-Plane version

**Warning Types**:
- **Performance Warnings**: Settings that may impact performance
- **Best Practice Suggestions**: Recommended configuration improvements

### Performance Optimization

**Rain System**:
- Use appropriate rain scale values (avoid unnecessary maximum values)
- Optimize thermal textures (use appropriate resolution)

**Material Integration**:
- Minimize complex node trees for better export performance
- Use efficient texture sizes
- Avoid unnecessary auto-detection if not needed

### Getting Help

**Resources**:
- [XPlane2Blender Documentation](../README.md)
- [X-Plane Developer Documentation](https://developer.x-plane.com/)
- [Blender Material Nodes Guide](https://docs.blender.org/manual/en/latest/render/shader_nodes/)

**Community Support**:
- XPlane2Blender GitHub Issues
- X-Plane Developer Forums
- Blender Community Forums

---

*This guide covers X-Plane 12+ features in XPlane2Blender. For general usage instructions, see the main documentation.*