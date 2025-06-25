# Standard Shading Phase 4 Test Suite

This directory contains comprehensive tests for the Phase 4 Standard Shading features in XPlane2Blender.

## Test Files

- `standard_shading_phase4.test.py` - Main test suite for all standard shading features
- `fixtures/create_test_blend.py` - Script to generate test blend files
- `fixtures/standard_shading_test.blend` - Test blend file with standard shading setup

## Test Coverage

The test suite covers the following Phase 4 Standard Shading features:

### Core Commands
- `DECAL` - Basic decal application with scale and texture
- `DECAL_RGBA` - RGBA decal with alpha channel support
- `DECAL_KEYED` - Color-keyed decal with custom key values
- `TEXTURE_TILE` - Texture tiling with page support
- `NORMAL_DECAL` - Normal map decals with gloss control

### Material Controls
- `SPECULAR` - Specular ratio adjustment
- `BUMP_LEVEL` - Bump level ratio control

### Alpha Controls
- `DITHER_ALPHA` - Dithered alpha with softness and bleed
- `NO_ALPHA` - Alpha cutoff control
- `NO_BLEND` - Blend mode override

### Integration Features
- PBR workflow detection
- Standard shading compatibility analysis
- X-Plane version compatibility (requires X-Plane 12+)
- Multiple feature combinations

## Running the Tests

### Individual Test File
```bash
python -m pytest tests/materials/standard_shading/standard_shading_phase4.test.py -v
```

### All Standard Shading Tests
```bash
python -m pytest tests/materials/standard_shading/ -v
```

### From Blender
```python
import sys
sys.path.append("path/to/XPlane2Blender")
from tests.materials.standard_shading.standard_shading_phase4 import *
unittest.main()
```

## Creating Test Fixtures

To create the test blend file:

1. Open Blender
2. Install/enable the XPlane2Blender addon
3. Run the script: `fixtures/create_test_blend.py`
4. This will create `standard_shading_test.blend` in the fixtures directory

## Test Structure

### TestStandardShadingPhase4
Main test class that covers:
- Property existence validation
- Command export verification
- Feature interaction testing
- Version compatibility checks
- PBR workflow integration

### TestStandardShadingConstants
Tests for constant definitions:
- Shader command constants
- Default value constants

## Expected Outputs

The tests verify that the correct OBJ commands are exported:

```
DECAL 1.0 test_decal.png
DECAL_RGBA 1.5 test_decal_rgba.png
DECAL_KEYED 1.0 1.0 0.5 0.0 1.0 0.8 test_decal_keyed.png
TEXTURE_TILE 4 4 2 2 test_tile.png
NORMAL_DECAL 1.0 test_normal_decal.png 1.5
SPECULAR 1.5
BUMP_LEVEL 0.8
DITHER_ALPHA 0.7 0.3
NO_ALPHA
NO_BLEND 0.6
```

## Dependencies

- Blender 3.0+
- XPlane2Blender addon
- Python unittest framework
- X-Plane 12+ for standard shading features

## Notes

- Standard shading features are only available in X-Plane 12+
- Tests automatically handle scene setup and cleanup
- All tests use the XPlaneTestCase base class for consistency
- PBR workflow detection requires proper node setup in materials