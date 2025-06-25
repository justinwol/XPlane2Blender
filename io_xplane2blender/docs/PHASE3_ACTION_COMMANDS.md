# Phase 3: Action Commands Implementation

## Overview
Phase 3 implements advanced action commands for the XPlane2Blender addon, providing support for smoke effects, enhanced particle emitters, and VR magnet attachment points.

## Implemented Features

### 1. Smoke Commands
Support for smoke particle effects at specified locations.

#### SMOKE_BLACK Command
- **Purpose**: Creates black smoke puff effects
- **Usage**: Set Empty object special type to "Smoke Black"
- **Export Format**: `SMOKE_BLACK <x> <y> <z> <size>`
- **Parameters**:
  - Position: Automatically calculated from Empty object location
  - Size: Configurable smoke puff size (0.1-10.0, default 1.0)

#### SMOKE_WHITE Command
- **Purpose**: Creates white smoke puff effects
- **Usage**: Set Empty object special type to "Smoke White"
- **Export Format**: `SMOKE_WHITE <x> <y> <z> <size>`
- **Parameters**:
  - Position: Automatically calculated from Empty object location
  - Size: Configurable smoke puff size (0.1-10.0, default 1.0)

### 2. Enhanced EMITTER Commands
Advanced particle emitter system with optional parameters.

#### Basic Mode (Backward Compatible)
- **Export Format**: `EMITTER <name> <x> <y> <z> <psi> <theta> <phi> [index]`
- **Usage**: Same as previous implementation

#### Advanced Mode
- **Export Format**: `EMITTER <name> <x> <y> <z> <psi> <theta> <phi> [index] [intensity] [duration]`
- **Additional Parameters**:
  - Intensity: Particle emission intensity (0.0-10.0, default 1.0)
  - Duration: Emission duration in seconds (0.1-60.0, default 5.0)
- **Usage**: Enable "Advanced Mode" checkbox in emitter settings

### 3. MAGNET Commands (Pre-existing, Enhanced)
VR attachment points for tablets and devices.

- **Export Format**: `MAGNET <name> <type> <x> <y> <z> <psi> <theta> <phi>`
- **Types**: xpad, flashlight, or combination
- **Usage**: Set Empty object special type to "Magnet"

## User Interface

### Smoke Settings
When an Empty object's special type is set to "Smoke Black" or "Smoke White":
- **Size Slider**: Controls the smoke puff size parameter

### Enhanced Emitter Settings
When an Empty object's special type is set to "Emitter Particle" or "Emitter Sound":
- **Name Field**: Particle system name from .pss file
- **Index Controls**: Optional array index settings
- **Advanced Mode Checkbox**: Enables advanced parameters
- **Advanced Parameters** (when enabled):
  - **Intensity Slider**: Particle emission intensity
  - **Duration Slider**: Emission duration in seconds

### Magnet Settings
When an Empty object's special type is set to "Magnet":
- **Debug Name Field**: Human-readable identifier
- **Type Checkboxes**: xpad and/or flashlight

## Implementation Details

### File Structure
- **Constants**: `io_xplane2blender/xplane_constants.py`
- **Properties**: `io_xplane2blender/xplane_props.py`
- **Export Logic**: `io_xplane2blender/xplane_types/xplane_empty.py`
- **User Interface**: `io_xplane2blender/xplane_ui.py`

### Test Coverage
- **Smoke Commands**: `tests/particles/smoke_commands.test.py`
- **Enhanced Emitters**: `tests/particles/enhanced_emitter.test.py`
- **Existing Tests**: All existing particle and magnet tests continue to pass

### Coordinate System
All action commands use the X-Plane coordinate system:
- **Position**: Converted from Blender to X-Plane coordinates
- **Orientation**: Euler angles (psi, theta, phi) in degrees
- **Transformation**: Applied via `getBakeMatrixForAttached()`

## Usage Examples

### Creating Smoke Effects
1. Add an Empty object in Blender
2. Set its special type to "Smoke Black" or "Smoke White"
3. Position the Empty where you want the smoke effect
4. Adjust the size parameter as needed
5. Export to generate SMOKE_BLACK or SMOKE_WHITE commands

### Creating Advanced Emitters
1. Add an Empty object in Blender
2. Set its special type to "Emitter Particle"
3. Configure the particle name and index
4. Enable "Advanced Mode" for additional parameters
5. Set intensity and duration values
6. Export to generate enhanced EMITTER commands

### Creating VR Magnets
1. Add an Empty object in Blender
2. Set its special type to "Magnet"
3. Set a debug name for identification
4. Choose magnet types (xpad/flashlight)
5. Position and orient the Empty as needed
6. Export to generate MAGNET commands

## Backward Compatibility
- All existing EMITTER commands continue to work unchanged
- Advanced parameters are only exported when explicitly enabled
- No breaking changes to existing workflows
- All previous test cases continue to pass

## Integration with Animation System
Action commands integrate with the existing animation and dataref systems:
- Position and orientation can be animated
- Commands respect bone hierarchy and transformations
- Compatible with existing export pipeline and state management