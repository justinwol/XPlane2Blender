# XPlane2Blender v5.1.0 - Major Modernization Release

## 📦 Installation Instructions

### For Blender Users:
1. Download `XPlane2Blender-v5.1.0-Release.zip`
2. Open Blender 4.0+
3. Go to Edit → Preferences → Add-ons
4. Click "Install..." button
5. Select the downloaded zip file
6. Enable "Import-Export: XPlane2Blender Export for X-Plane 12+ OBJs"

### Alternative Installation (Advanced):
Extract the zip and place the `io_xplane2blender` folder in your Blender addons directory:
- Windows: `%APPDATA%\Blender Foundation\Blender\4.x\scripts\addons\`
- macOS: `~/Library/Application Support/Blender/4.x/scripts/addons/`
- Linux: `~/.config/blender/4.x/scripts/addons/`

## 🚀 What's New in v5.1.0

### 🎯 Major Feature Implementation (Phases 3-6)

#### Phase 3: Action Commands
- **Enhanced Geometry Commands**: Complete support for lines, line strips, quad strips, fans, and triangle compatibility
- **Primitive System Overhaul**: Modernized primitive handling with improved performance
- **Mesh Processing**: Advanced mesh validation and optimization

#### Phase 4: Standard Shading Framework
- **Material System**: Foundation for advanced material processing
- **Shader Compatibility**: Preparation for X-Plane 12+ standard shading
- **Texture Pipeline**: Enhanced texture handling and validation

#### Phase 5: Complete Weather System
- **Rain System**: Full implementation of X-Plane 12+ rain effects
- **Thermal Sources**: Complete thermal source compatibility and validation
- **Weather Integration**: Seamless integration with X-Plane 12+ weather systems

#### Phase 6: Advanced State Commands
- **Blend Glass**: Aircraft and HUD glass rendering support
- **Cockpit Devices**: GNS430, cockpit lighting, and device integration
- **Global Effects**: Luminance control (100-65530 nits) and global tinting
- **Advanced Materials**: Instanced scenery, albedo-only modes

### 🔧 Core System Enhancements

#### Enhanced Particle System
- **Smoke Commands**: Black and white smoke with advanced parameters
- **Enhanced Emitters**: Basic and advanced particle emitter configurations
- **Performance Optimization**: Improved particle rendering efficiency

#### Light System Improvements
- **Cone Lights**: Advanced cone light support with proper falloff
- **Billboard Lights**: Enhanced billboard lighting with X-Plane 12+ compatibility
- **Light Validation**: Comprehensive light parameter validation

#### Material System Overhaul
- **Advanced State Commands**: Complete implementation of X-Plane 12+ material states
- **Cockpit Materials**: Specialized cockpit material handling
- **Glass Materials**: Blend glass and HUD glass support
- **Global Controls**: Luminance and tint controls for advanced rendering

### 📚 Comprehensive Documentation Suite
- **Architecture Guide**: Complete developer architecture documentation
- **Feature Compatibility Matrix**: X-Plane version compatibility tracking
- **Performance Impact Analysis**: Detailed performance considerations
- **Phase Implementation Guides**: Step-by-step implementation documentation
- **Test Results Summary**: Comprehensive test coverage documentation

### 🧪 Enhanced Testing Framework
- **Geometry Tests**: Complete geometry command validation
- **Light Tests**: Cone and billboard light testing
- **Particle Tests**: Smoke and emitter system validation
- **Material Tests**: Advanced state and standard shading tests
- **Weather Tests**: Rain system and thermal source testing
- **Integration Tests**: End-to-end feature validation

### 🔄 Core Module Updates
- **xplane_constants.py**: Updated with X-Plane 12+ constants
- **xplane_props.py**: Enhanced property definitions
- **xplane_types/**: Complete type system modernization
- **xplane_utils/**: Utility function enhancements

## 📋 System Requirements

- **Blender**: 4.0.0 or higher
- **X-Plane**: Optimized for X-Plane 12+ (backward compatible with X-Plane 11)
- **Python**: 3.10+ (included with Blender 4+)
- **Operating System**: Windows, macOS, Linux

## 🎯 Key Benefits

### For Aircraft Developers
- **Complete X-Plane 12+ Support**: All modern features implemented
- **Enhanced Rain Effects**: Realistic weather integration
- **Advanced Cockpit Features**: Modern avionics and lighting support
- **Performance Optimized**: Efficient export and rendering

### For Scenery Developers
- **Advanced Materials**: Global tinting and luminance controls
- **Enhanced Particles**: Smoke and advanced emitter systems
- **Thermal Sources**: Complete weather system integration
- **Optimized Geometry**: Improved primitive handling

### For All Users
- **Blender 4+ Native**: Full compatibility with modern Blender
- **Comprehensive Documentation**: Complete guides and references
- **Robust Testing**: Validated feature implementation
- **Active Maintenance**: Ongoing development and support

## 📚 Documentation

- **Comprehensive Documentation Index**: Complete feature documentation
- **Developer Architecture Guide**: Technical implementation details
- **Feature Compatibility Matrix**: Version compatibility tracking
- **Performance Impact Analysis**: Optimization guidelines
- **User Guide**: Step-by-step usage instructions
- **Repository**: https://github.com/justinwol/XPlane2Blender

## 🐛 Support

- **Issues**: Report bugs at https://github.com/justinwol/XPlane2Blender/issues
- **Documentation**: https://github.com/justinwol/XPlane2Blender/wiki
- **Community**: X-Plane developer community forums

## 🔄 Migration from v5.0.x

This release is fully backward compatible with v5.0.x projects. New features are automatically available, and existing projects will continue to work without modification.

### New Features Available:
- Enhanced weather system integration
- Advanced material state commands
- Improved particle systems
- Complete light system overhaul
- Comprehensive geometry command support

## 📄 License

This addon is released under the GNU General Public License v2.0.

## 🙏 Acknowledgments

- Original XPlane2Blender team: Ted Greene, Ben Supnik, Amy Parent, Maya F. Eroglu
- X-Plane developer community for feedback and testing
- Blender Foundation for the excellent Blender 4+ API

---

**Note**: This is a major modernization release featuring complete X-Plane 12+ and Blender 4+ compatibility with comprehensive feature implementation across all development phases.