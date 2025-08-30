#!/usr/bin/env python3
"""
Analyze extracted firmware files and look for resources/EL structure
"""

import os
import struct
import hashlib
import binascii

def analyze_extracted_firmware():
    print("=== ANALYZING EXTRACTED FIRMWARE FILES ===")
    print()
    
    # Get all firmware files
    firmware_files = [f for f in os.listdir('.') if f.startswith('firmware_') and f.endswith('.bin')]
    
    print(f"Found {len(firmware_files)} firmware files")
    print()
    
    # Analyze each file
    for filename in firmware_files[:10]:  # Analyze first 10 files
        print(f"Analyzing {filename}...")
        
        with open(filename, 'rb') as f:
            data = f.read()
        
        print(f"  Size: {len(data)} bytes")
        
        # Look for signatures
        signatures = {
            b'\x55\xaa': 'Bootloader signature (0x55AA)',
            b'\xaa\x55': 'Alternative bootloader signature (0xAA55)',
            b'EILK': 'Eilik firmware signature',
            b'EILIK': 'Eilik firmware signature',
            b'FIRMWARE': 'Firmware signature',
            b'BOOTLOADER': 'Bootloader signature'
        }
        
        found_signatures = []
        for sig, desc in signatures.items():
            if sig in data:
                pos = data.find(sig)
                found_signatures.append((desc, pos))
        
        if found_signatures:
            print(f"  Found signatures:")
            for desc, pos in found_signatures:
                print(f"    {desc} at position {pos}")
        
        # Look for EL-related patterns
        el_patterns = [
            b'EL_',
            b'Eilik_',
            b'robot_',
            b'servo_',
            b'firmware_',
            b'update_',
            b'bootloader_',
            b'resources',
            b'ressources',
            b'ressourcen'
        ]
        
        found_patterns = []
        for pattern in el_patterns:
            if pattern in data:
                pos = data.find(pattern)
                found_patterns.append((pattern.decode('utf-8', errors='ignore'), pos))
        
        if found_patterns:
            print(f"  Found patterns:")
            for pattern, pos in found_patterns:
                print(f"    '{pattern}' at position {pos}")
        
        # Look for file extensions
        extensions = [b'.bin', b'.hex', b'.fw', b'.firmware', b'.dat', b'.cfg']
        found_extensions = []
        for ext in extensions:
            if ext in data:
                pos = data.find(ext)
                found_extensions.append((ext.decode('utf-8', errors='ignore'), pos))
        
        if found_extensions:
            print(f"  Found file extensions:")
            for ext, pos in found_extensions:
                print(f"    '{ext}' at position {pos}")
        
        # Calculate checksum
        checksum = hashlib.md5(data).hexdigest()
        print(f"  MD5: {checksum}")
        
        # Look for printable strings
        strings = []
        current_string = ""
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += chr(byte)
            else:
                if len(current_string) > 3:
                    strings.append(current_string)
                current_string = ""
        
        if strings:
            print(f"  Found {len(strings)} strings:")
            for s in strings[:5]:  # Show first 5
                print(f"    '{s}'")
        
        print()
    
    print()
    
    # Look for resources/EL folder structure
    print("=== SEARCHING FOR RESOURCES/EL STRUCTURE ===")
    print()
    
    # Search in all firmware files for resources/EL patterns
    for filename in firmware_files:
        with open(filename, 'rb') as f:
            data = f.read()
        
        # Look for resources/EL patterns
        patterns = [
            b'resources/EL',
            b'ressources/EL',
            b'ressourcen/EL',
            b'resources\\EL',
            b'ressources\\EL',
            b'ressourcen\\EL',
            b'EL/',
            b'EL\\',
            b'EL_',
            b'Eilik_'
        ]
        
        for pattern in patterns:
            if pattern in data:
                pos = data.find(pattern)
                print(f"Found '{pattern.decode('utf-8', errors='ignore')}' in {filename} at position {pos}")
                
                # Extract context
                start = max(0, pos - 50)
                end = min(len(data), pos + 100)
                context = data[start:end]
                
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    print(f"  Context: ...{context_str}...")
                except:
                    print(f"  Context: {context.hex()}")
    
    print()
    
    # Look for possible embedded firmware data
    print("=== SEARCHING FOR EMBEDDED FIRMWARE DATA ===")
    print()
    
    # Check if any of the extracted files contain actual firmware
    for filename in firmware_files[:5]:  # Check first 5 files
        with open(filename, 'rb') as f:
            data = f.read()
        
        # Look for firmware-like patterns
        firmware_indicators = 0
        
        # Check for bootloader signatures
        if b'\x55\xaa' in data or b'\xaa\x55' in data:
            firmware_indicators += 1
        
        # Check for binary data patterns
        null_count = data.count(b'\x00')
        null_ratio = null_count / len(data)
        
        if null_ratio > 0.1:  # More than 10% null bytes
            firmware_indicators += 1
        
        # Check for repeated patterns
        pattern_count = 0
        for i in range(0, len(data) - 4, 4):
            pattern = data[i:i+4]
            if data.count(pattern) > 2:  # Pattern appears more than twice
                pattern_count += 1
        
        if pattern_count > 5:  # Multiple repeated patterns
            firmware_indicators += 1
        
        if firmware_indicators >= 2:
            print(f"{filename} appears to contain firmware data:")
            print(f"  - Bootloader signatures: {'Yes' if b'\x55\xaa' in data or b'\xaa\x55' in data else 'No'}")
            print(f"  - Null byte ratio: {null_ratio:.2%}")
            print(f"  - Repeated patterns: {pattern_count}")
            print(f"  - Size: {len(data)} bytes")
            
            # Save as potential firmware
            new_filename = f"potential_firmware_{filename}"
            with open(new_filename, 'wb') as f:
                f.write(data)
            print(f"  - Saved as {new_filename}")
            print()
    
    print("Analysis completed.")

if __name__ == "__main__":
    analyze_extracted_firmware()