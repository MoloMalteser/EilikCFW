#!/usr/bin/env python3
"""
Eilik CFW Development Tools
"""

import os
import sys
import struct
import zlib

class EilikCFWAnalyzer:
    def __init__(self, exe_path="EnergizeLab.exe"):
        self.exe_path = exe_path
        self.data = None
        
    def load_executable(self):
        """Load the executable file"""
        if not os.path.exists(self.exe_path):
            print(f"Error: {self.exe_path} not found")
            return False
            
        with open(self.exe_path, 'rb') as f:
            self.data = f.read()
        print(f"Loaded {len(self.data)} bytes from {self.exe_path}")
        return True
    
    def find_python_modules(self):
        """Find Python module references"""
        if not self.data:
            print("No data loaded")
            return
            
        modules = []
        # Look for common patterns
        patterns = [
            b'FirmwareBase',
            b'ui_py_files_v2',
            b'EilikPerameter',
            b'FirmwareUpdate',
            b'SearchDevice'
        ]
        
        for pattern in patterns:
            pos = 0
            while True:
                pos = self.data.find(pattern, pos)
                if pos == -1:
                    break
                # Try to extract context
                start = max(0, pos - 50)
                end = min(len(self.data), pos + len(pattern) + 50)
                context = self.data[start:end]
                modules.append((pattern.decode(), pos, context))
                pos += len(pattern)
        
        return modules
    
    def analyze_communication(self):
        """Analyze communication patterns"""
        print("Analyzing communication patterns...")
        
        # Look for USB/serial patterns
        usb_patterns = [b'USB', b'HID', b'COM', b'Serial']
        for pattern in usb_patterns:
            count = self.data.count(pattern)
            if count > 0:
                print(f"Found {count} instances of {pattern}")
    
    def extract_strings(self):
        """Extract readable strings"""
        strings = []
        current_string = ""
        
        for byte in self.data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += chr(byte)
            else:
                if len(current_string) > 4:
                    strings.append(current_string)
                current_string = ""
        
        return [s for s in strings if len(s) > 4]

def main():
    analyzer = EilikCFWAnalyzer()
    
    if not analyzer.load_executable():
        return
    
    print("=== Eilik CFW Analysis ===")
    
    # Find Python modules
    modules = analyzer.find_python_modules()
    print(f"\nFound {len(modules)} module references:")
    for name, pos, context in modules[:10]:
        print(f"  {name} at position {pos}")
    
    # Analyze communication
    analyzer.analyze_communication()
    
    # Extract strings
    strings = analyzer.extract_strings()
    print(f"\nExtracted {len(strings)} strings")
    
    # Look for interesting strings
    interesting = [s for s in strings if any(keyword in s.lower() 
                for keyword in ['firmware', 'update', 'usb', 'serial', 'eilik'])]
    
    print(f"\nInteresting strings ({len(interesting)}):")
    for s in interesting[:20]:
        print(f"  {s}")

if __name__ == "__main__":
    main()
