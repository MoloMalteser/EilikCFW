#!/usr/bin/env python3
"""
Search for resource folders and EL-related files in EnergizeLab.exe
"""

import os
import re
import struct

def search_resources():
    exe_path = "EnergizeLab.exe"
    
    with open(exe_path, 'rb') as f:
        data = f.read()
    
    print("=== SEARCHING FOR RESOURCE FOLDERS AND EL FILES ===")
    print()
    
    # Search for possible resource folder patterns
    resource_patterns = [
        rb'resources',
        rb'ressources', 
        rb'ressourcen',
        rb'assets',
        rb'data',
        rb'files',
        rb'firmware',
        rb'updates'
    ]
    
    print("Searching for resource folder patterns:")
    for pattern in resource_patterns:
        matches = list(re.finditer(pattern, data, re.IGNORECASE))
        if matches:
            print(f"  Found '{pattern.decode()}' {len(matches)} times:")
            for i, match in enumerate(matches[:5]):  # Show first 5 matches
                start = max(0, match.start() - 50)
                end = min(len(data), match.end() + 50)
                context = data[start:end]
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    print(f"    Position {match.start()}: ...{context_str}...")
                except:
                    print(f"    Position {match.start()}: Binary data")
    
    print()
    
    # Search for EL-related patterns
    el_patterns = [
        rb'EL_',
        rb'Eilik_',
        rb'robot_',
        rb'servo_',
        rb'firmware_',
        rb'update_',
        rb'bootloader_'
    ]
    
    print("Searching for EL-related patterns:")
    for pattern in el_patterns:
        matches = list(re.finditer(pattern, data, re.IGNORECASE))
        if matches:
            print(f"  Found '{pattern.decode()}' {len(matches)} times:")
            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                start = max(0, match.start() - 30)
                end = min(len(data), match.end() + 30)
                context = data[start:end]
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    print(f"    Position {match.start()}: ...{context_str}...")
                except:
                    print(f"    Position {match.start()}: Binary data")
    
    print()
    
    # Search for file extensions
    file_extensions = [
        rb'\.bin',
        rb'\.hex', 
        rb'\.fw',
        rb'\.firmware',
        rb'\.dat',
        rb'\.cfg',
        rb'\.json',
        rb'\.xml',
        rb'\.zip',
        rb'\.tar',
        rb'\.gz'
    ]
    
    print("Searching for file extensions:")
    for ext in file_extensions:
        matches = list(re.finditer(ext, data, re.IGNORECASE))
        if matches:
            print(f"  Found '{ext.decode()}' {len(matches)} times:")
            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                start = max(0, match.start() - 20)
                end = min(len(data), match.end() + 20)
                context = data[start:end]
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    print(f"    Position {match.start()}: ...{context_str}...")
                except:
                    print(f"    Position {match.start()}: Binary data")
    
    print()
    
    # Search for path-like strings
    path_patterns = [
        rb'[A-Za-z]:\\[^\\]*',
        rb'/[A-Za-z0-9_/]*',
        rb'\\\\[^\\]*',
        rb'resources/[^\\]*',
        rb'assets/[^\\]*',
        rb'data/[^\\]*'
    ]
    
    print("Searching for path-like strings:")
    for pattern in path_patterns:
        matches = list(re.finditer(pattern, data))
        if matches:
            print(f"  Found path pattern {len(matches)} times:")
            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                path_str = match.group().decode('utf-8', errors='ignore')
                print(f"    Position {match.start()}: {path_str}")
    
    print()
    
    # Search for possible embedded binary data
    print("Searching for embedded binary data:")
    
    # Look for common binary signatures
    signatures = {
        b'\x55\xaa': 'Bootloader signature',
        b'\xaa\x55': 'Alternative bootloader signature',
        b'\x7fELF': 'ELF format',
        b'MZ': 'PE format',
        b'PK\x03\x04': 'ZIP file',
        b'\x1f\x8b\x08': 'GZIP file',
        b'\x42\x5a\x68': 'BZIP2 file'
    }
    
    for sig, desc in signatures.items():
        count = data.count(sig)
        if count > 0:
            print(f"  Found {desc}: {count} occurrences")
            # Find first occurrence
            pos = data.find(sig)
            if pos != -1:
                start = max(0, pos - 10)
                end = min(len(data), pos + 20)
                context = data[start:end]
                print(f"    First at position {pos}: {context.hex()}")
    
    print()
    
    # Search for possible resource section
    print("Analyzing possible resource sections:")
    
    # Look for .rsrc section
    rsrc_pos = data.find(b'.rsrc')
    if rsrc_pos != -1:
        print(f"  Found .rsrc section at position {rsrc_pos}")
        
        # Try to extract some data around it
        start = max(0, rsrc_pos - 100)
        end = min(len(data), rsrc_pos + 200)
        rsrc_data = data[start:end]
        
        print(f"  .rsrc context (first 100 bytes): {rsrc_data[:100].hex()}")
        
        # Look for strings in .rsrc section
        strings_in_rsrc = []
        for i in range(rsrc_pos, min(len(data), rsrc_pos + 1000)):
            if 32 <= data[i] <= 126:  # Printable ASCII
                string_start = i
                while i < len(data) and 32 <= data[i] <= 126:
                    i += 1
                if i - string_start > 3:  # At least 4 characters
                    string_data = data[string_start:i]
                    strings_in_rsrc.append(string_data.decode('utf-8', errors='ignore'))
        
        if strings_in_rsrc:
            print(f"  Found {len(strings_in_rsrc)} strings in .rsrc section:")
            for s in strings_in_rsrc[:10]:  # Show first 10
                print(f"    {s}")
    
    print()
    print("Resource search completed.")

if __name__ == "__main__":
    search_resources()