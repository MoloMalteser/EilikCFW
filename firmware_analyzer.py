#!/usr/bin/env python3
"""
Eilik Firmware Analyzer
For analyzing firmware files when found
"""

import os
import sys
import struct
import binascii
import hashlib

class FirmwareAnalyzer:
    def __init__(self, firmware_path):
        self.firmware_path = firmware_path
        self.data = None
        
    def load_firmware(self):
        """Load firmware file"""
        if not os.path.exists(self.firmware_path):
            print(f"Error: {self.firmware_path} not found")
            return False
            
        with open(self.firmware_path, 'rb') as f:
            self.data = f.read()
        print(f"Loaded {len(self.data)} bytes from {self.firmware_path}")
        return True
    
    def analyze_header(self):
        """Analyze firmware header"""
        if not self.data:
            return
            
        print("=== FIRMWARE HEADER ANALYSIS ===")
        print()
        
        # Common firmware headers
        headers = {
            b'\x55\xaa': 'Bootloader signature (0x55AA)',
            b'\xaa\x55': 'Alternative bootloader signature (0xAA55)',
            b'\x7fELF': 'ELF format',
            b'MZ': 'PE format',
            b'\x1f\x8b\x08': 'GZIP compressed',
            b'PK\x03\x04': 'ZIP archive',
        }
        
        for sig, desc in headers.items():
            if self.data.startswith(sig):
                print(f"✅ Found header: {desc}")
                return sig
        
        print("❌ No recognized header found")
        print("First 32 bytes:", self.data[:32].hex())
        return None
    
    def analyze_structure(self):
        """Analyze firmware structure"""
        if not self.data:
            return
            
        print("=== FIRMWARE STRUCTURE ANALYSIS ===")
        print()
        
        # Look for common patterns
        patterns = {
            b'bootloader': 'Bootloader section',
            b'application': 'Application section',
            b'firmware': 'Firmware section',
            b'config': 'Configuration section',
            b'param': 'Parameter section',
            b'calib': 'Calibration section',
        }
        
        found_sections = []
        for pattern, desc in patterns.items():
            pos = 0
            while True:
                pos = self.data.find(pattern, pos)
                if pos == -1:
                    break
                found_sections.append((pos, desc))
                pos += len(pattern)
        
        if found_sections:
            print("Found sections:")
            for pos, desc in sorted(found_sections):
                print(f"  {desc} at offset 0x{pos:08X}")
        else:
            print("No clear sections identified")
        
        print()
        
        # Analyze data patterns
        print("Data pattern analysis:")
        
        # Count null bytes
        null_count = self.data.count(b'\x00')
        null_percent = (null_count / len(self.data)) * 100
        print(f"  Null bytes: {null_count} ({null_percent:.1f}%)")
        
        # Count printable ASCII
        printable = sum(1 for b in self.data if 32 <= b <= 126)
        printable_percent = (printable / len(self.data)) * 100
        print(f"  Printable ASCII: {printable} ({printable_percent:.1f}%)")
        
        # Look for repeated patterns
        print("  Looking for repeated patterns...")
        pattern_length = 16
        patterns = {}
        for i in range(0, len(self.data) - pattern_length, pattern_length):
            pattern = self.data[i:i+pattern_length]
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        repeated = [(p, c) for p, c in patterns.items() if c > 1]
        if repeated:
            print(f"  Found {len(repeated)} repeated patterns")
            for pattern, count in sorted(repeated, key=lambda x: x[1], reverse=True)[:5]:
                print(f"    Pattern {pattern.hex()}: {count} times")
    
    def extract_sections(self):
        """Extract potential firmware sections"""
        if not self.data:
            return
            
        print("=== EXTRACTING FIRMWARE SECTIONS ===")
        print()
        
        # Common section sizes
        section_sizes = [1024, 4096, 8192, 16384, 32768, 65536]
        
        for size in section_sizes:
            if len(self.data) >= size:
                section = self.data[:size]
                filename = f"section_{size//1024}k.bin"
                
                with open(filename, 'wb') as f:
                    f.write(section)
                print(f"Extracted {filename} ({len(section)} bytes)")
                
                # Calculate checksum
                checksum = hashlib.md5(section).hexdigest()
                print(f"  MD5: {checksum}")
    
    def analyze_hex_format(self):
        """Analyze if firmware is in Intel HEX format"""
        if not self.data:
            return
            
        print("=== HEX FORMAT ANALYSIS ===")
        print()
        
        # Check if it's Intel HEX format
        if self.data.startswith(b':'):
            print("✅ Intel HEX format detected")
            
            # Parse HEX records
            lines = self.data.split(b'\n')
            hex_records = []
            
            for line in lines:
                line = line.strip()
                if line.startswith(b':') and len(line) > 10:
                    try:
                        # Parse HEX record
                        data_len = int(line[1:3].decode(), 16)
                        addr = int(line[3:7].decode(), 16)
                        record_type = int(line[7:9].decode(), 16)
                        
                        hex_records.append({
                            'length': data_len,
                            'address': addr,
                            'type': record_type,
                            'data': line[9:9+data_len*2].decode()
                        })
                    except:
                        continue
            
            print(f"Found {len(hex_records)} HEX records")
            
            # Analyze record types
            record_types = {}
            for record in hex_records:
                record_types[record['type']] = record_types.get(record['type'], 0) + 1
            
            print("Record types:")
            for rtype, count in record_types.items():
                type_names = {
                    0: 'Data',
                    1: 'End of File',
                    2: 'Extended Segment Address',
                    3: 'Start Segment Address',
                    4: 'Extended Linear Address',
                    5: 'Start Linear Address'
                }
                name = type_names.get(rtype, f'Unknown ({rtype})')
                print(f"  {name}: {count}")
        else:
            print("❌ Not Intel HEX format")
    
    def generate_report(self):
        """Generate comprehensive firmware report"""
        if not self.data:
            return
            
        print("=== FIRMWARE ANALYSIS REPORT ===")
        print()
        
        print(f"File: {self.firmware_path}")
        print(f"Size: {len(self.data)} bytes ({len(self.data)/1024:.1f} KB)")
        print(f"MD5: {hashlib.md5(self.data).hexdigest()}")
        print(f"SHA1: {hashlib.sha1(self.data).hexdigest()}")
        print()
        
        # Analyze header
        header = self.analyze_header()
        
        # Analyze structure
        self.analyze_structure()
        
        # Check HEX format
        self.analyze_hex_format()
        
        print("=== RECOMMENDATIONS ===")
        print()
        
        if header:
            print("✅ Firmware format identified")
            print("   - Proceed with format-specific analysis")
        else:
            print("❓ Unknown firmware format")
            print("   - Try different analysis methods")
            print("   - Look for embedded headers")
        
        print()
        print("Next steps:")
        print("1. Extract firmware sections")
        print("2. Analyze bootloader if present")
        print("3. Identify application code")
        print("4. Reverse engineer communication protocol")
        print("5. Create custom firmware")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 firmware_analyzer.py <firmware_file>")
        print("Example: python3 firmware_analyzer.py firmware.bin")
        return
    
    firmware_path = sys.argv[1]
    analyzer = FirmwareAnalyzer(firmware_path)
    
    if analyzer.load_firmware():
        analyzer.generate_report()
        analyzer.extract_sections()

if __name__ == "__main__":
    main()