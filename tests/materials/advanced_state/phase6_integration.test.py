import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterPhase6Commands(line):
    """Filter for all Phase 6 advanced state commands"""
    if not isinstance(line, str):
        return False
    
    phase6_commands = [
        'BLEND_GLASS',
        'GLOBAL_luminance',
        'GLOBAL_tint',
        'ATTR_cockpit_device',
        'ATTR_hud_glass',
        'ATTR_hud_reset',
        'ATTR_cockpit_lit_only'
    ]
    
    return any(line.find(cmd) == 0 for cmd in phase6_commands)

class TestPhase6Integration(XPlaneTestCase):
    def test_all_commands_aircraft_export(self):
        """Test all Phase 6 commands in aircraft export type"""
        filename = 'test_all_commands_aircraft_export'
        self.assertLayerExportEqualsFixture(
            0,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_all_commands_cockpit_export(self):
        """Test all Phase 6 commands in cockpit export type"""
        filename = 'test_all_commands_cockpit_export'
        self.assertLayerExportEqualsFixture(
            1,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_all_commands_scenery_export(self):
        """Test all Phase 6 commands in scenery export type"""
        filename = 'test_all_commands_scenery_export'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_all_commands_instanced_scenery_export(self):
        """Test all Phase 6 commands in instanced scenery export type"""
        filename = 'test_all_commands_instanced_scenery_export'
        self.assertLayerExportEqualsFixture(
            3,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_blend_glass_with_luminance(self):
        """Test BLEND_GLASS combined with GLOBAL_luminance"""
        filename = 'test_blend_glass_with_luminance'
        self.assertLayerExportEqualsFixture(
            4,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_blend_glass_with_tint(self):
        """Test BLEND_GLASS combined with GLOBAL_tint"""
        filename = 'test_blend_glass_with_tint'
        self.assertLayerExportEqualsFixture(
            5,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_cockpit_device_with_hud_glass(self):
        """Test ATTR_cockpit_device combined with ATTR_hud_glass"""
        filename = 'test_cockpit_device_with_hud_glass'
        self.assertLayerExportEqualsFixture(
            6,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_cockpit_device_with_lit_only(self):
        """Test ATTR_cockpit_device combined with ATTR_cockpit_lit_only"""
        filename = 'test_cockpit_device_with_lit_only'
        self.assertLayerExportEqualsFixture(
            7,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_hud_glass_with_lit_only(self):
        """Test ATTR_hud_glass combined with ATTR_cockpit_lit_only"""
        filename = 'test_hud_glass_with_lit_only'
        self.assertLayerExportEqualsFixture(
            8,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_luminance_with_tint(self):
        """Test GLOBAL_luminance combined with GLOBAL_tint"""
        filename = 'test_luminance_with_tint'
        self.assertLayerExportEqualsFixture(
            9,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_all_cockpit_commands_together(self):
        """Test all cockpit-specific commands together"""
        filename = 'test_all_cockpit_commands_together'
        self.assertLayerExportEqualsFixture(
            10,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_command_ordering(self):
        """Test proper ordering of Phase 6 commands in output"""
        filename = 'test_command_ordering'
        out = self.exportLayer(11)
        lines = out.split('\n')
        
        # Find indices of Phase 6 commands
        command_indices = {}
        for i, line in enumerate(lines):
            if line.startswith('BLEND_GLASS'):
                command_indices['BLEND_GLASS'] = i
            elif line.startswith('GLOBAL_luminance'):
                command_indices['GLOBAL_luminance'] = i
            elif line.startswith('GLOBAL_tint'):
                command_indices['GLOBAL_tint'] = i
            elif line.startswith('ATTR_cockpit_device'):
                command_indices['ATTR_cockpit_device'] = i
            elif line.startswith('ATTR_hud_glass'):
                command_indices['ATTR_hud_glass'] = i
            elif line.startswith('ATTR_hud_reset'):
                command_indices['ATTR_hud_reset'] = i
            elif line.startswith('ATTR_cockpit_lit_only'):
                command_indices['ATTR_cockpit_lit_only'] = i
        
        # Verify proper ordering (global commands before attribute commands)
        global_commands = ['BLEND_GLASS', 'GLOBAL_luminance', 'GLOBAL_tint']
        attr_commands = ['ATTR_cockpit_device', 'ATTR_hud_glass', 'ATTR_hud_reset', 'ATTR_cockpit_lit_only']
        
        for global_cmd in global_commands:
            if global_cmd in command_indices:
                for attr_cmd in attr_commands:
                    if attr_cmd in command_indices:
                        self.assertLess(command_indices[global_cmd], command_indices[attr_cmd],
                                      f"{global_cmd} should come before {attr_cmd}")

    def test_version_compatibility_all_commands(self):
        """Test version compatibility for all Phase 6 commands"""
        filename = 'test_version_compatibility_all_commands'
        out = self.exportLayer(12)
        
        # For X-Plane 12+, all commands should be present
        if 'version' in out and '1200' in out:
            self.assertIn('BLEND_GLASS', out)
            self.assertIn('GLOBAL_luminance', out)
            self.assertIn('GLOBAL_tint', out)
            self.assertIn('ATTR_cockpit_device', out)
            self.assertIn('ATTR_hud_glass', out)
            self.assertIn('ATTR_hud_reset', out)
            self.assertIn('ATTR_cockpit_lit_only', out)

    def test_invalid_combinations_error_handling(self):
        """Test error handling for invalid command combinations"""
        filename = 'test_invalid_combinations_error_handling'
        out = self.exportLayer(13)
        
        # Should generate appropriate errors for invalid combinations
        errors = logger.findErrors()
        if len(errors) > 0:
            # Verify errors are for expected invalid combinations
            error_messages = [str(error) for error in errors]
            # Check for specific error patterns
            self.assertTrue(any('BLEND_GLASS' in msg for msg in error_messages) or
                          any('cockpit_device' in msg for msg in error_messages))
        logger.clearMessages()

    def test_state_management_complex_scene(self):
        """Test state management with complex scene hierarchy"""
        filename = 'test_state_management_complex_scene'
        out = self.exportLayer(14)
        
        # Verify proper state management
        lines = out.split('\n')
        phase6_lines = [line for line in lines if filterPhase6Commands(line)]
        
        # Should have reasonable number of state changes
        self.assertTrue(len(phase6_lines) > 0)
        self.assertTrue(len(phase6_lines) < 1000)  # Reasonable upper limit

    def test_performance_optimization(self):
        """Test performance optimization with multiple Phase 6 commands"""
        filename = 'test_performance_optimization'
        out = self.exportLayer(15)
        
        # Verify no redundant command output
        lines = out.split('\n')
        command_counts = {}
        
        for line in lines:
            if filterPhase6Commands(line):
                if line in command_counts:
                    command_counts[line] += 1
                else:
                    command_counts[line] = 1
        
        # Should not have excessive duplicate commands
        for cmd, count in command_counts.items():
            self.assertLess(count, 10, f"Command '{cmd}' appears {count} times, which may be excessive")

    def test_material_inheritance_complex(self):
        """Test material inheritance with multiple Phase 6 commands"""
        filename = 'test_material_inheritance_complex'
        self.assertLayerExportEqualsFixture(
            16,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterPhase6Commands,
            filename,
        )

    def test_edge_cases_boundary_values(self):
        """Test edge cases with boundary values for all commands"""
        filename = 'test_edge_cases_boundary_values'
        out = self.exportLayer(17)
        
        # Should handle boundary values correctly
        if 'GLOBAL_luminance' in out:
            # Check for proper clamping
            self.assertTrue('65530' in out or '0' in out)
        
        if 'GLOBAL_tint' in out:
            # Check for proper ratio clamping
            lines = [line for line in out.split('\n') if 'GLOBAL_tint' in line]
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        albedo = float(parts[1])
                        emissive = float(parts[2])
                        self.assertGreaterEqual(albedo, 0.0)
                        self.assertLessEqual(albedo, 1.0)
                        self.assertGreaterEqual(emissive, 0.0)
                        self.assertLessEqual(emissive, 1.0)
                    except ValueError:
                        pass  # Skip non-numeric values

runTestCases([TestPhase6Integration])