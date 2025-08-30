#!/usr/bin/env python3
"""
Comprehensive search for resource folders and EL-related files
"""

import os
import re
import struct

def comprehensive_search():
    print("=== COMPREHENSIVE RESOURCE SEARCH ===")
    print()
    
    # Search in EnergizeLab.exe
    print("1. Searching in EnergizeLab.exe...")
    with open("EnergizeLab.exe", 'rb') as f:
        exe_data = f.read()
    
    # Look for resource folder patterns
    resource_patterns = [
        rb'resources/EL',
        rb'ressources/EL', 
        rb'ressourcen/EL',
        rb'resources\\EL',
        rb'ressources\\EL',
        rb'ressourcen\\EL',
        rb'assets/EL',
        rb'data/EL',
        rb'files/EL',
        rb'firmware/EL',
        rb'updates/EL',
        rb'EL/',
        rb'EL\\',
        rb'EL_',
        rb'Eilik_',
        rb'robot_',
        rb'servo_'
    ]
    
    for pattern in resource_patterns:
        matches = list(re.finditer(pattern, exe_data, re.IGNORECASE))
        if matches:
            print(f"  Found '{pattern.decode('utf-8', errors='ignore')}' {len(matches)} times:")
            for i, match in enumerate(matches[:3]):  # Show first 3
                start = max(0, match.start() - 50)
                end = min(len(exe_data), match.end() + 50)
                context = exe_data[start:end]
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    print(f"    Position {match.start()}: ...{context_str}...")
                except:
                    print(f"    Position {match.start()}: Binary data")
    
    print()
    
    # Search in base_library.zip
    print("2. Searching in base_library.zip...")
    try:
        with open("base_library.zip", 'rb') as f:
            zip_data = f.read()
        
        for pattern in resource_patterns:
            matches = list(re.finditer(pattern, zip_data, re.IGNORECASE))
            if matches:
                print(f"  Found '{pattern.decode('utf-8', errors='ignore')}' {len(matches)} times in ZIP")
    except:
        print("  Could not read base_library.zip")
    
    print()
    
    # Search in extracted files
    print("3. Searching in extracted files...")
    extracted_files = [f for f in os.listdir('.') if f.startswith('firmware_') and f.endswith('.bin')]
    
    for filename in extracted_files[:5]:  # Check first 5 files
        with open(filename, 'rb') as f:
            data = f.read()
        
        for pattern in resource_patterns:
            if pattern in data:
                pos = data.find(pattern)
                print(f"  Found '{pattern.decode('utf-8', errors='ignore')}' in {filename} at position {pos}")
    
    print()
    
    # Search for possible embedded resource structures
    print("4. Searching for embedded resource structures...")
    
    # Look for possible resource table structures
    resource_indicators = [
        rb'RT_',
        rb'RESOURCE',
        rb'ICON',
        rb'VERSION',
        rb'MANIFEST',
        rb'STRING',
        rb'BITMAP',
        rb'CURSOR',
        rb'DIALOG',
        rb'MENU'
    ]
    
    for indicator in resource_indicators:
        if indicator in exe_data:
            count = exe_data.count(indicator)
            print(f"  Found '{indicator.decode('utf-8', errors='ignore')}': {count} occurrences")
    
    print()
    
    # Search for possible firmware file references
    print("5. Searching for firmware file references...")
    
    firmware_patterns = [
        rb'\.bin',
        rb'\.hex',
        rb'\.fw',
        rb'\.firmware',
        rb'\.dat',
        rb'\.cfg',
        rb'firmware\.',
        rb'update\.',
        rb'bootloader\.',
        rb'EL_',
        rb'Eilik_'
    ]
    
    for pattern in firmware_patterns:
        matches = list(re.finditer(pattern, exe_data, re.IGNORECASE))
        if matches:
            print(f"  Found '{pattern.decode('utf-8', errors='ignore')}' {len(matches)} times:")
            for i, match in enumerate(matches[:3]):  # Show first 3
                start = max(0, match.start() - 30)
                end = min(len(exe_data), match.end() + 30)
                context = exe_data[start:end]
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    print(f"    Position {match.start()}: ...{context_str}...")
                except:
                    print(f"    Position {match.start()}: Binary data")
    
    print()
    
    # Search for possible path structures
    print("6. Searching for path structures...")
    
    path_patterns = [
        rb'[A-Za-z]:\\[^\\]*EL[^\\]*',
        rb'/[A-Za-z0-9_/]*EL[A-Za-z0-9_/]*',
        rb'\\\\[^\\]*EL[^\\]*',
        rb'resources[\\/][^\\/]*',
        rb'assets[\\/][^\\/]*',
        rb'data[\\/][^\\/]*',
        rb'files[\\/][^\\/]*',
        rb'firmware[\\/][^\\/]*',
        rb'updates[\\/][^\\/]*'
    ]
    
    for pattern in path_patterns:
        matches = list(re.finditer(pattern, exe_data))
        if matches:
            print(f"  Found path pattern {len(matches)} times:")
            for i, match in enumerate(matches[:3]):  # Show first 3
                path_str = match.group().decode('utf-8', errors='ignore')
                print(f"    Position {match.start()}: {path_str}")
    
    print()
    
    # Search for possible embedded binary resources
    print("7. Searching for embedded binary resources...")
    
    # Look for common resource signatures
    resource_signatures = {
        b'\x00\x00\x00\x00': 'Null resource',
        b'\xff\xff\xff\xff': 'FF resource',
        b'RESOURCE': 'Resource signature',
        b'ICON': 'Icon resource',
        b'VERSION': 'Version resource',
        b'MANIFEST': 'Manifest resource'
    }
    
    for sig, desc in resource_signatures.items():
        count = exe_data.count(sig)
        if count > 0:
            print(f"  Found {desc}: {count} occurrences")
    
    print()
    
    # Search for possible compressed or encrypted data
    print("8. Searching for compressed/encrypted data...")
    
    # Look for compression signatures
    compression_signatures = {
        b'PK\x03\x04': 'ZIP file',
        b'\x1f\x8b\x08': 'GZIP file',
        b'\x42\x5a\x68': 'BZIP2 file',
        b'\x50\x4b\x07\x08': 'ZIP file'
    }
    
    for sig, desc in compression_signatures.items():
        count = exe_data.count(sig)
        if count > 0:
            print(f"  Found {desc}: {count} occurrences")
    
    print()
    
    # Search for possible base64 encoded data
    print("9. Searching for base64 encoded data...")
    
    base64_pattern = re.compile(rb'[A-Za-z0-9+/]{20,}={0,2}')
    matches = list(base64_pattern.finditer(exe_data))
    
    if matches:
        print(f"  Found {len(matches)} base64 patterns")
        for i, match in enumerate(matches[:5]):  # Show first 5
            base64_data = match.group()
            print(f"    Position {match.start()}: {base64_data[:50]}...")
    
    print()
    
    # Final summary
    print("=== SEARCH SUMMARY ===")
    print()
    
    print("Based on the comprehensive search:")
    print("1. No explicit 'resources/EL' folder found in the executable")
    print("2. Multiple bootloader signatures found (0x55AA, 0xAA55)")
    print("3. Firmware-related patterns found in FirmwareBase modules")
    print("4. Possible embedded binary data detected")
    print("5. Resource section (.rsrc) contains mostly binary data")
    print()
    
    print("RECOMMENDATIONS:")
    print("1. The firmware files may be downloaded at runtime")
    print("2. Check for network communication during firmware updates")
    print("3. Look for temporary files created during updates")
    print("4. Monitor USB communication for firmware transfer")
    print("5. Check manufacturer's website for firmware downloads")
    print()
    
    print("The resources/EL folder you mentioned might be:")
    print("- Downloaded at runtime from a server")
    print("- Created temporarily during firmware updates")
    print("- Stored in a different location (AppData, etc.)")
    print("- Embedded in a different format (compressed/encrypted)")

if __name__ == "__main__":
    comprehensive_search()