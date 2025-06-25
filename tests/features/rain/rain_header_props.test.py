import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers

__dirname__ = os.path.dirname(__file__)


class TestRainHeaderProps(XPlaneTestCase):
    def test_thermal_wiper_fixtures(self) -> None:
        filenames = [
            "test_thermal_options",
            "test_thermal2_options",
            "test_wiper_options",
        ]
        for filepath in [
            Path(__dirname__, "fixtures", f"{filename}.obj")
            for filename in filenames
        ]:
            with self.subTest(filepath=filepath):
                root_name = filepath.stem.replace("test_", "")
                self.assertExportableRootExportEqualsFixture(
                    root_object=root_name,
                    fixturePath=filepath,
                    filterCallback={"RAIN_scale", "THERMAL", "WIPER"},
                    tmpFilename=filepath.stem,
                )
    
    def test_enhanced_rain_features(self) -> None:
        """Test enhanced rain system features for X-Plane 12+"""
        filenames = [
            "test_rain_friction_options",
            "test_enhanced_thermal_options",
            "test_enhanced_wiper_options",
        ]
        for filepath in [
            Path(__dirname__, "fixtures", f"{filename}.obj")
            for filename in filenames
        ]:
            with self.subTest(filepath=filepath):
                root_name = filepath.stem.replace("test_", "")
                self.assertExportableRootExportEqualsFixture(
                    root_object=root_name,
                    fixturePath=filepath,
                    filterCallback={"RAIN_scale", "RAIN_friction", "THERMAL", "WIPER"},
                    tmpFilename=filepath.stem,
                )

    def test_no_options(self) -> None:
        filenames = [
            "test_inst_scenery_no_options",
            "test_scenery_no_options",
            "test_missing_paths_no_options",
            "test_none_enabled_no_options",
        ]
        for filepath in [
            Path(__dirname__, "fixtures", f"{filename}.obj")
            for filename in filenames
        ]:
            with self.subTest(filepath=filepath):
                root_name = filepath.stem.replace("test_", "")
                self.assertExportableRootExportEqualsFixture(
                    root_object=root_name,
                    fixturePath=filepath,
                    filterCallback={"RAIN_scale", "THERMAL", "WIPER"},
                    tmpFilename=filepath.stem,
                )

    def test_phase5_thermal_compatibility(self) -> None:
        """Test Phase 5 thermal source compatibility features"""
        filenames = [
            "test_thermal_source_xp12",
        ]
        for filepath in [
            Path(__dirname__, "fixtures", f"{filename}.obj")
            for filename in filenames
        ]:
            with self.subTest(filepath=filepath):
                root_name = filepath.stem.replace("test_", "")
                self.assertExportableRootExportEqualsFixture(
                    root_object=root_name,
                    fixturePath=filepath,
                    filterCallback={"THERMAL_texture", "THERMAL_source"},
                    tmpFilename=filepath.stem,
                )
    
    def test_complete_weather_system_integration(self) -> None:
        """Test complete weather system with all Phase 5 features"""
        filenames = [
            "test_complete_weather_system",
        ]
        for filepath in [
            Path(__dirname__, "fixtures", f"{filename}.obj")
            for filename in filenames
        ]:
            with self.subTest(filepath=filepath):
                root_name = filepath.stem.replace("test_", "")
                self.assertExportableRootExportEqualsFixture(
                    root_object=root_name,
                    fixturePath=filepath,
                    filterCallback={"RAIN_scale", "RAIN_friction", "THERMAL_texture", "THERMAL_source2", "WIPER_texture", "WIPER_param"},
                    tmpFilename=filepath.stem,
                )

    def test_errors(self) -> None:
        self.exportExportableRoot("thermal_errors",)
        self.assertLoggerErrors(0)
        self.exportExportableRoot("thermal2_errors",)
        self.assertLoggerErrors(4)
        self.exportExportableRoot("wiper_errors",)
        self.assertLoggerErrors(3)


runTestCases([TestRainHeaderProps])
