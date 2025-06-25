#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner for XPlane2Blender

This script runs all validation tests including:
- Blender 4+ compatibility tests
- X-Plane 12 feature validation
- Material integration tests
- Performance tests
- Integration scenarios

Usage:
    blender --python tests/test_suite_runner.py
    blender --python tests/test_suite_runner.py -- --filter rain
    blender --python tests/test_suite_runner.py -- --performance
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

import bpy

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import validation test modules
try:
    from test_addon_registration import main as test_addon_registration
    from test_critical_validation import main as test_critical_validation
    from test_complete_validation import main as test_complete_validation
    from test_blender4_xplane12_validation import main as test_blender4_validation
except ImportError as e:
    print(f"Warning: Could not import validation modules: {e}")

# Import integration test
try:
    from tests.test_blender4_xplane12_integration import TestBlender4XPlane12Integration
    from io_xplane2blender.tests import XPlaneTestCase
    integration_tests_available = True
except ImportError as e:
    print(f"Warning: Integration tests not available: {e}")
    integration_tests_available = False


class TestSuiteRunner:
    """Comprehensive test suite runner for XPlane2Blender"""
    
    def __init__(self):
        self.results = {
            'addon_registration': None,
            'critical_validation': None,
            'complete_validation': None,
            'blender4_validation': None,
            'integration_tests': None,
            'performance_tests': None
        }
        self.start_time = time.time()
        self.test_filter = None
        self.run_performance = False
        self.verbose = False
    
    def parse_args(self):
        """Parse command line arguments"""
        # Blender passes args after -- to the script
        if '--' in sys.argv:
            script_args = sys.argv[sys.argv.index('--') + 1:]
        else:
            script_args = []
        
        parser = argparse.ArgumentParser(description='XPlane2Blender Test Suite Runner')
        parser.add_argument('--filter', help='Filter tests by keyword', type=str)
        parser.add_argument('--performance', help='Run performance tests', action='store_true')
        parser.add_argument('--verbose', help='Verbose output', action='store_true')
        parser.add_argument('--quick', help='Run only critical tests', action='store_true')
        
        if script_args:
            args = parser.parse_args(script_args)
            self.test_filter = args.filter
            self.run_performance = args.performance
            self.verbose = args.verbose
            self.quick_mode = args.quick
        else:
            self.quick_mode = False
    
    def should_run_test(self, test_name: str) -> bool:
        """Check if test should run based on filter"""
        if not self.test_filter:
            return True
        return self.test_filter.lower() in test_name.lower()
    
    def run_addon_registration_tests(self) -> Dict[str, Any]:
        """Run addon registration diagnostic tests"""
        if not self.should_run_test('addon_registration'):
            return {'skipped': True}
        
        print("\n" + "="*60)
        print("RUNNING ADDON REGISTRATION TESTS")
        print("="*60)
        
        try:
            results = test_addon_registration()
            return {
                'success': True,
                'results': results,
                'passed': sum(1 for _, success in results if success),
                'total': len(results)
            }
        except Exception as e:
            print(f"Addon registration tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_critical_validation_tests(self) -> Dict[str, Any]:
        """Run critical validation tests"""
        if not self.should_run_test('critical_validation'):
            return {'skipped': True}
        
        print("\n" + "="*60)
        print("RUNNING CRITICAL VALIDATION TESTS")
        print("="*60)
        
        try:
            results = test_critical_validation()
            return {
                'success': True,
                'results': results,
                'passed': sum(1 for _, success in results if success),
                'total': len(results)
            }
        except Exception as e:
            print(f"Critical validation tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_complete_validation_tests(self) -> Dict[str, Any]:
        """Run complete validation tests"""
        if not self.should_run_test('complete_validation') or self.quick_mode:
            return {'skipped': True}
        
        print("\n" + "="*60)
        print("RUNNING COMPLETE VALIDATION TESTS")
        print("="*60)
        
        try:
            results = test_complete_validation()
            return {
                'success': True,
                'results': results,
                'passed': sum(1 for _, success in results if success),
                'total': len(results)
            }
        except Exception as e:
            print(f"Complete validation tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_blender4_validation_tests(self) -> Dict[str, Any]:
        """Run Blender 4+ validation tests"""
        if not self.should_run_test('blender4_validation') or self.quick_mode:
            return {'skipped': True}
        
        print("\n" + "="*60)
        print("RUNNING BLENDER 4+ VALIDATION TESTS")
        print("="*60)
        
        try:
            results = test_blender4_validation()
            return {
                'success': True,
                'results': results,
                'passed': len([r for r in results if r.get('success', False)]),
                'total': len(results)
            }
        except Exception as e:
            print(f"Blender 4+ validation tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests using unittest framework"""
        if not self.should_run_test('integration') or not integration_tests_available or self.quick_mode:
            return {'skipped': True}
        
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        try:
            import unittest
            
            # Create test suite
            suite = unittest.TestSuite()
            
            # Add integration tests
            test_case = TestBlender4XPlane12Integration()
            test_case.setUp()
            
            # Run individual test methods
            test_methods = [
                'test_ui_panel_compatibility',
                'test_blender4_integration_properties',
                'test_xplane12_rain_system',
                'test_xplane12_thermal_system',
                'test_xplane12_wiper_system',
                'test_landing_gear_system',
                'test_material_integration',
                'test_complex_integration_scenarios',
                'test_error_handling_and_graceful_degradation'
            ]
            
            results = []
            for method_name in test_methods:
                if hasattr(test_case, method_name):
                    try:
                        method = getattr(test_case, method_name)
                        method()
                        results.append((method_name, True, "Passed"))
                        print(f"✓ {method_name}")
                    except Exception as e:
                        results.append((method_name, False, str(e)))
                        print(f"✗ {method_name}: {e}")
            
            return {
                'success': True,
                'results': results,
                'passed': sum(1 for _, success, _ in results if success),
                'total': len(results),
                'test_results': test_case.test_results
            }
            
        except Exception as e:
            print(f"Integration tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        if not self.run_performance or not integration_tests_available:
            return {'skipped': True}
        
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        try:
            test_case = TestBlender4XPlane12Integration()
            test_case.setUp()
            
            start_time = time.time()
            test_case.test_export_performance()
            performance_time = time.time() - start_time
            
            return {
                'success': True,
                'performance_time': performance_time,
                'test_results': test_case.test_results.get('performance_tests', [])
            }
            
        except Exception as e:
            print(f"Performance tests failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print("XPLANE2BLENDER COMPREHENSIVE TEST SUITE")
        print("="*60)
        print(f"Blender Version: {bpy.app.version}")
        print(f"Blender Version String: {bpy.app.version_string}")
        print(f"Test Filter: {self.test_filter or 'None'}")
        print(f"Performance Tests: {'Enabled' if self.run_performance else 'Disabled'}")
        print(f"Quick Mode: {'Enabled' if self.quick_mode else 'Disabled'}")
        print("")
        
        # Run test suites in order
        self.results['addon_registration'] = self.run_addon_registration_tests()
        self.results['critical_validation'] = self.run_critical_validation_tests()
        
        if not self.quick_mode:
            self.results['complete_validation'] = self.run_complete_validation_tests()
            self.results['blender4_validation'] = self.run_blender4_validation_tests()
            self.results['integration_tests'] = self.run_integration_tests()
        
        if self.run_performance:
            self.results['performance_tests'] = self.run_performance_tests()
        
        return self.results
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report"""
        total_time = time.time() - self.start_time
        
        report = []
        report.append("\n" + "="*60)
        report.append("COMPREHENSIVE TEST SUITE SUMMARY")
        report.append("="*60)
        
        total_passed = 0
        total_tests = 0
        suite_results = []
        
        for suite_name, result in self.results.items():
            if result is None or result.get('skipped'):
                suite_results.append((suite_name, "SKIPPED", 0, 0))
                continue
            
            if not result.get('success', False):
                suite_results.append((suite_name, "FAILED", 0, 0))
                continue
            
            passed = result.get('passed', 0)
            total = result.get('total', 0)
            total_passed += passed
            total_tests += total
            
            status = "PASS" if passed == total else "PARTIAL"
            suite_results.append((suite_name, status, passed, total))
        
        # Suite summary
        for suite_name, status, passed, total in suite_results:
            if status == "SKIPPED":
                report.append(f"[SKIP] {suite_name.replace('_', ' ').title()}")
            elif status == "FAILED":
                report.append(f"[FAIL] {suite_name.replace('_', ' ').title()}")
            else:
                report.append(f"[{status}] {suite_name.replace('_', ' ').title()}: {passed}/{total}")
        
        # Overall summary
        report.append("")
        report.append(f"Overall Results: {total_passed}/{total_tests} tests passed")
        if total_tests > 0:
            percentage = (total_passed / total_tests) * 100
            report.append(f"Success Rate: {percentage:.1f}%")
        
        report.append(f"Total Execution Time: {total_time:.2f} seconds")
        
        # Detailed results for failed tests
        failed_tests = []
        for suite_name, result in self.results.items():
            if result and result.get('success') and 'results' in result:
                for test_result in result['results']:
                    if isinstance(test_result, tuple) and len(test_result) >= 2:
                        test_name, success = test_result[0], test_result[1]
                        if not success:
                            failed_tests.append(f"{suite_name}: {test_name}")
                    elif isinstance(test_result, dict) and not test_result.get('success', True):
                        failed_tests.append(f"{suite_name}: {test_result.get('test', 'Unknown')}")
        
        if failed_tests:
            report.append("")
            report.append("Failed Tests:")
            for failed_test in failed_tests:
                report.append(f"  - {failed_test}")
        
        # Performance summary
        if self.results.get('performance_tests') and not self.results['performance_tests'].get('skipped'):
            perf_result = self.results['performance_tests']
            if perf_result.get('success'):
                perf_time = perf_result.get('performance_time', 0)
                report.append("")
                report.append(f"Performance Test Time: {perf_time:.2f} seconds")
        
        # Recommendations
        report.append("")
        report.append("Recommendations:")
        
        if total_tests == 0:
            report.append("  - No tests were executed. Check test availability and filters.")
        elif total_passed == total_tests:
            report.append("  - ✓ All tests passed! XPlane2Blender is ready for production use.")
            report.append("  - Consider running performance tests if not already done.")
        elif total_passed / total_tests >= 0.9:
            report.append("  - ✓ Most tests passed. Minor issues may need attention.")
            report.append("  - Review failed tests and address any critical issues.")
        else:
            report.append("  - ⚠ Significant test failures detected.")
            report.append("  - Review and fix failed tests before production use.")
            report.append("  - Consider running individual test suites for detailed debugging.")
        
        return "\n".join(report)
    
    def save_detailed_report(self, filename: str = "test_results.txt"):
        """Save detailed test results to file"""
        try:
            report_lines = []
            report_lines.append("XPlane2Blender Detailed Test Results")
            report_lines.append("="*50)
            report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Blender Version: {bpy.app.version_string}")
            report_lines.append("")
            
            for suite_name, result in self.results.items():
                if result is None or result.get('skipped'):
                    continue
                
                report_lines.append(f"\n{suite_name.replace('_', ' ').title()}:")
                report_lines.append("-" * 30)
                
                if not result.get('success', False):
                    report_lines.append(f"FAILED: {result.get('error', 'Unknown error')}")
                    continue
                
                if 'results' in result:
                    for test_result in result['results']:
                        if isinstance(test_result, tuple):
                            test_name, success = test_result[0], test_result[1]
                            status = "PASS" if success else "FAIL"
                            report_lines.append(f"  [{status}] {test_name}")
                        elif isinstance(test_result, dict):
                            test_name = test_result.get('test', 'Unknown')
                            success = test_result.get('success', False)
                            message = test_result.get('message', '')
                            status = "PASS" if success else "FAIL"
                            report_lines.append(f"  [{status}] {test_name}: {message}")
                
                # Add integration test details
                if 'test_results' in result:
                    test_results = result['test_results']
                    for category, tests in test_results.items():
                        if tests and category != 'errors':
                            report_lines.append(f"\n  {category.replace('_', ' ').title()}:")
                            for test in tests:
                                if isinstance(test, dict):
                                    test_name = test.get('test', 'Unknown')
                                    success = test.get('success', False)
                                    message = test.get('message', '')
                                    status = "PASS" if success else "FAIL"
                                    report_lines.append(f"    [{status}] {test_name}: {message}")
            
            # Write to file
            with open(filename, 'w') as f:
                f.write("\n".join(report_lines))
            
            print(f"\nDetailed report saved to: {filename}")
            
        except Exception as e:
            print(f"Failed to save detailed report: {e}")


def main():
    """Main test runner function"""
    runner = TestSuiteRunner()
    runner.parse_args()
    
    try:
        # Run all tests
        results = runner.run_all_tests()
        
        # Generate and display summary
        summary = runner.generate_summary_report()
        print(summary)
        
        # Save detailed report
        runner.save_detailed_report()
        
        # Return appropriate exit code
        total_passed = sum(r.get('passed', 0) for r in results.values() if r and r.get('success'))
        total_tests = sum(r.get('total', 0) for r in results.values() if r and r.get('success'))
        
        if total_tests == 0:
            print("\nWarning: No tests were executed.")
            return 1
        elif total_passed == total_tests:
            print(f"\n✓ All {total_tests} tests passed successfully!")
            return 0
        else:
            print(f"\n⚠ {total_tests - total_passed} of {total_tests} tests failed.")
            return 1
            
    except Exception as e:
        print(f"\nTest suite execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    # Note: sys.exit() doesn't work reliably in Blender scripts
    if exit_code != 0:
        print(f"Test suite completed with exit code: {exit_code}")