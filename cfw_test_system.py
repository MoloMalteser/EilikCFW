#!/usr/bin/env python3
"""
CFW Test System
Connects CFW with Eilik Emulator for comprehensive testing
"""

import time
import struct
import threading
from eilik_emulator import EilikEmulator
from cfw_design import CFWFirmware

class CFWTestSystem:
    def __init__(self):
        self.emulator = EilikEmulator()
        self.cfw = CFWFirmware()
        self.test_results = []
        self.running = True
        
        # Start test monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_system)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_system(self):
        """Monitor system performance during tests"""
        while self.running:
            # Get performance metrics
            cfw_metrics = self.cfw.get_performance_metrics()
            emulator_status = self.emulator.get_servo_status()
            
            # Check for issues
            for servo_id, servo in cfw_metrics['servo_status'].items():
                if servo['temperature'] > 70:
                    print(f"⚠️  WARNING: Servo {servo_id} temperature high: {servo['temperature']}°C")
                
                if servo['voltage'] < 4.5 or servo['voltage'] > 5.5:
                    print(f"⚠️  WARNING: Servo {servo_id} voltage out of range: {servo['voltage']}V")
            
            time.sleep(1.0)  # Monitor every second
    
    def test_basic_communication(self):
        """Test basic communication protocol"""
        print("=== TESTING BASIC COMMUNICATION ===")
        
        # Test device info
        print("1. Testing device info...")
        cmd = struct.pack('<HBB', 0xAA55, 0x01, 0x00)
        response = self.emulator.process_command(cmd)
        print(f"   Response: {response.hex()}")
        
        if response[2] == 0x82:  # DATA response
            print("   ✅ Device info test PASSED")
            self.test_results.append(("Device Info", "PASSED"))
        else:
            print("   ❌ Device info test FAILED")
            self.test_results.append(("Device Info", "FAILED"))
        
        # Test servo control
        print("2. Testing servo control...")
        cmd = struct.pack('<HBBH', 0xAA55, 0x05, 0x04, 0x01)  # Set servo 0 position
        cmd += struct.pack('<H', 750)  # Position 750
        response = self.emulator.process_command(cmd)
        print(f"   Response: {response.hex()}")
        
        if response[2] == 0x80:  # ACK response
            print("   ✅ Servo control test PASSED")
            self.test_results.append(("Servo Control", "PASSED"))
        else:
            print("   ❌ Servo control test FAILED")
            self.test_results.append(("Servo Control", "FAILED"))
        
        print()
    
    def test_cfw_features(self):
        """Test CFW specific features"""
        print("=== TESTING CFW FEATURES ===")
        
        # Test enhanced servo control
        print("1. Testing enhanced servo control...")
        success = self.cfw.set_servo_position(0, 800, 90, 20)
        if success:
            print("   ✅ Enhanced servo control PASSED")
            self.test_results.append(("Enhanced Servo Control", "PASSED"))
        else:
            print("   ❌ Enhanced servo control FAILED")
            self.test_results.append(("Enhanced Servo Control", "FAILED"))
        
        # Test custom animations
        print("2. Testing custom animations...")
        success = self.cfw.play_animation('wave')
        if success:
            print("   ✅ Custom animations PASSED")
            self.test_results.append(("Custom Animations", "PASSED"))
        else:
            print("   ❌ Custom animations FAILED")
            self.test_results.append(("Custom Animations", "FAILED"))
        
        # Test custom behaviors
        print("3. Testing custom behaviors...")
        success = self.cfw.set_behavior('curious')
        if success:
            print("   ✅ Custom behaviors PASSED")
            self.test_results.append(("Custom Behaviors", "PASSED"))
        else:
            print("   ❌ Custom behaviors FAILED")
            self.test_results.append(("Custom Behaviors", "FAILED"))
        
        # Test performance monitoring
        print("4. Testing performance monitoring...")
        metrics = self.cfw.get_performance_metrics()
        if metrics and 'system_health' in metrics:
            print("   ✅ Performance monitoring PASSED")
            self.test_results.append(("Performance Monitoring", "PASSED"))
        else:
            print("   ❌ Performance monitoring FAILED")
            self.test_results.append(("Performance Monitoring", "FAILED"))
        
        print()
    
    def test_firmware_update(self):
        """Test firmware update process"""
        print("=== TESTING FIRMWARE UPDATE ===")
        
        # Generate CFW firmware
        print("1. Generating CFW firmware...")
        firmware_binary = self.cfw.generate_firmware_binary()
        print(f"   Firmware size: {len(firmware_binary)} bytes")
        
        # Test firmware update command
        print("2. Testing firmware update...")
        cmd = struct.pack('<HBB', 0xAA55, 0x02, len(firmware_binary))
        cmd += firmware_binary
        response = self.emulator.process_command(cmd)
        
        if response[2] == 0x80:  # ACK response
            print("   ✅ Firmware update test PASSED")
            self.test_results.append(("Firmware Update", "PASSED"))
        else:
            print("   ❌ Firmware update test FAILED")
            self.test_results.append(("Firmware Update", "FAILED"))
        
        print()
    
    def test_safety_features(self):
        """Test safety features"""
        print("=== TESTING SAFETY FEATURES ===")
        
        # Test safety limits
        print("1. Testing safety limits...")
        limits = {'min': 100, 'max': 900, 'max_temp': 75}
        success = self.cfw.set_safety_limits(0, limits)
        
        if success:
            print("   ✅ Safety limits test PASSED")
            self.test_results.append(("Safety Limits", "PASSED"))
        else:
            print("   ❌ Safety limits test FAILED")
            self.test_results.append(("Safety Limits", "FAILED"))
        
        # Test out-of-range position
        print("2. Testing out-of-range protection...")
        success = self.cfw.set_servo_position(0, 1200)  # Out of range
        if not success:
            print("   ✅ Out-of-range protection PASSED")
            self.test_results.append(("Out-of-Range Protection", "PASSED"))
        else:
            print("   ❌ Out-of-range protection FAILED")
            self.test_results.append(("Out-of-Range Protection", "FAILED"))
        
        print()
    
    def test_custom_movements(self):
        """Test custom movement sequences"""
        print("=== TESTING CUSTOM MOVEMENTS ===")
        
        # Create custom movement sequence
        movements = [
            {'servo': 0, 'position': 700, 'speed': 60, 'delay': 0.5},
            {'servo': 1, 'position': 300, 'speed': 40, 'delay': 0.5},
            {'servo': 2, 'position': 600, 'speed': 50, 'delay': 0.5},
            {'servo': 0, 'position': 500, 'speed': 30, 'delay': 0.5},
            {'servo': 1, 'position': 500, 'speed': 30, 'delay': 0.5},
            {'servo': 2, 'position': 500, 'speed': 30, 'delay': 0.0}
        ]
        
        print("1. Testing custom movement sequence...")
        success = self.cfw.custom_move(movements)
        
        if success:
            print("   ✅ Custom movements test PASSED")
            self.test_results.append(("Custom Movements", "PASSED"))
        else:
            print("   ❌ Custom movements test FAILED")
            self.test_results.append(("Custom Movements", "FAILED"))
        
        print()
    
    def test_debug_features(self):
        """Test debugging features"""
        print("=== TESTING DEBUG FEATURES ===")
        
        # Test debug logging
        print("1. Testing debug logging...")
        self.cfw.log_debug("Test debug message", "DEBUG")
        self.cfw.log_debug("Test warning message", "WARNING")
        self.cfw.log_debug("Test error message", "ERROR")
        
        log_entries = self.cfw.get_debug_log(3)
        if len(log_entries) >= 3:
            print("   ✅ Debug logging test PASSED")
            self.test_results.append(("Debug Logging", "PASSED"))
        else:
            print("   ❌ Debug logging test FAILED")
            self.test_results.append(("Debug Logging", "FAILED"))
        
        # Test log clearing
        print("2. Testing log clearing...")
        self.cfw.clear_debug_log()
        log_entries = self.cfw.get_debug_log()
        if len(log_entries) == 1:  # Only the "cleared" message
            print("   ✅ Log clearing test PASSED")
            self.test_results.append(("Log Clearing", "PASSED"))
        else:
            print("   ❌ Log clearing test FAILED")
            self.test_results.append(("Log Clearing", "FAILED"))
        
        print()
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("=== EILIK CFW COMPREHENSIVE TEST SUITE ===")
        print()
        
        # Run all tests
        self.test_basic_communication()
        self.test_cfw_features()
        self.test_firmware_update()
        self.test_safety_features()
        self.test_custom_movements()
        self.test_debug_features()
        
        # Wait for movements to complete
        print("Waiting for movements to complete...")
        time.sleep(3)
        
        # Generate test report
        self.generate_test_report()
        
        # Cleanup
        self.running = False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("=== TEST REPORT ===")
        print()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result in self.test_results if result == "PASSED")
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        print("Detailed Results:")
        for test_name, result in self.test_results:
            status = "✅" if result == "PASSED" else "❌"
            print(f"  {status} {test_name}: {result}")
        
        print()
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! CFW is ready for deployment.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Review and fix issues.")
        
        print()
        
        # Save test report
        with open("cfw_test_report.txt", "w") as f:
            f.write("EILIK CFW TEST REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n\n")
            
            f.write("Detailed Results:\n")
            for test_name, result in self.test_results:
                f.write(f"  {test_name}: {result}\n")
        
        print("Test report saved to cfw_test_report.txt")

def main():
    """Run the test system"""
    test_system = CFWTestSystem()
    
    try:
        test_system.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        test_system.running = False
    except Exception as e:
        print(f"\nTest error: {e}")
        test_system.running = False

if __name__ == "__main__":
    main()