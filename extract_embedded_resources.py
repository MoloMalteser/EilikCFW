#!/usr/bin/env python3
"""
Extract and analyze embedded resources from EnergizeLab.exe
"""

import os
import struct
import zlib
import binascii

def extract_embedded_resources():
    exe_path = "EnergizeLab.exe"
    
    with open(exe_path, 'rb') as f:
        data = f.read()
    
    print("=== EXTRACTING EMBEDDED RESOURCES ===")
    print()
    
    # Look for .rsrc section
    rsrc_pos = data.find(b'.rsrc')
    if rsrc_pos != -1:
        print(f"Found .rsrc section at position {rsrc_pos}")
        
        # Extract .rsrc section
        # Find the end of .rsrc section by looking for next section
        next_sections = ['.reloc', '.idata', '.edata', '.pdata']
        rsrc_end = len(data)
        
        for section in next_sections:
            pos = data.find(section.encode(), rsrc_pos)
            if pos != -1 and pos < rsrc_end:
                rsrc_end = pos
        
        rsrc_data = data[rsrc_pos:rsrc_end]
        print(f"Extracted {len(rsrc_data)} bytes from .rsrc section")
        
        # Save .rsrc section
        with open("extracted_rsrc.bin", "wb") as f:
            f.write(rsrc_data)
        print("Saved .rsrc section to extracted_rsrc.bin")
        
        # Analyze .rsrc section
        analyze_rsrc_section(rsrc_data)
    
    print()
    
    # Look for embedded firmware data
    print("Searching for embedded firmware data...")
    
    # Common firmware signatures
    firmware_signatures = [
        (b'\x55\xaa', 'Bootloader signature'),
        (b'\xaa\x55', 'Alternative bootloader signature'),
        (b'EILK', 'Eilik firmware signature'),
        (b'EILIK', 'Eilik firmware signature'),
        (b'FIRMWARE', 'Firmware signature'),
        (b'BOOTLOADER', 'Bootloader signature')
    ]
    
    for sig, desc in firmware_signatures:
        pos = 0
        while True:
            pos = data.find(sig, pos)
            if pos == -1:
                break
            
            print(f"Found {desc} at position {pos}")
            
            # Extract context around signature
            start = max(0, pos - 50)
            end = min(len(data), pos + 200)
            context = data[start:end]
            
            # Save potential firmware data
            filename = f"firmware_{desc.replace(' ', '_').lower()}_{pos}.bin"
            with open(filename, "wb") as f:
                f.write(context)
            print(f"  Saved to {filename}")
            
            pos += len(sig)
    
    print()
    
    # Look for compressed data
    print("Searching for compressed data...")
    
    # Common compression signatures
    compression_signatures = [
        (b'PK\x03\x04', 'ZIP file'),
        (b'PK\x05\x06', 'ZIP file'),
        (b'PK\x07\x08', 'ZIP file'),
        (b'\x1f\x8b\x08', 'GZIP file'),
        (b'\x42\x5a\x68', 'BZIP2 file'),
        (b'\x50\x4b\x07\x08', 'ZIP file')
    ]
    
    for sig, desc in compression_signatures:
        pos = 0
        while True:
            pos = data.find(sig, pos)
            if pos == -1:
                break
            
            print(f"Found {desc} at position {pos}")
            
            # Try to extract compressed data
            try:
                if sig.startswith(b'PK'):
                    extract_zip_data(data, pos, f"compressed_{desc.replace(' ', '_').lower()}_{pos}")
                elif sig.startswith(b'\x1f\x8b'):
                    extract_gzip_data(data, pos, f"compressed_{desc.replace(' ', '_').lower()}_{pos}")
                elif sig.startswith(b'\x42\x5a'):
                    extract_bzip2_data(data, pos, f"compressed_{desc.replace(' ', '_').lower()}_{pos}")
            except Exception as e:
                print(f"  Failed to extract: {e}")
            
            pos += len(sig)
    
    print()
    
    # Look for base64 encoded data
    print("Searching for base64 encoded data...")
    
    # Look for base64 patterns
    import re
    base64_pattern = re.compile(rb'[A-Za-z0-9+/]{20,}={0,2}')
    matches = base64_pattern.finditer(data)
    
    count = 0
    for match in matches:
        if count >= 10:  # Limit to first 10 matches
            break
        
        base64_data = match.group()
        print(f"Found base64 data at position {match.start()}: {base64_data[:50]}...")
        
        # Try to decode
        try:
            decoded = binascii.a2b_base64(base64_data)
            if len(decoded) > 10:  # Only save if it's substantial
                filename = f"base64_decoded_{match.start()}.bin"
                with open(filename, "wb") as f:
                    f.write(decoded)
                print(f"  Decoded and saved to {filename}")
        except:
            pass
        
        count += 1
    
    print()
    print("Resource extraction completed.")

def analyze_rsrc_section(rsrc_data):
    """Analyze .rsrc section"""
    print("Analyzing .rsrc section...")
    
    # Look for resource types
    resource_types = {
        1: 'RT_CURSOR',
        2: 'RT_BITMAP', 
        3: 'RT_ICON',
        4: 'RT_MENU',
        5: 'RT_DIALOG',
        6: 'RT_STRING',
        7: 'RT_FONTDIR',
        8: 'RT_FONT',
        9: 'RT_ACCELERATOR',
        10: 'RT_RCDATA',
        11: 'RT_MESSAGETABLE',
        12: 'RT_GROUP_CURSOR',
        14: 'RT_GROUP_ICON',
        16: 'RT_VERSION',
        17: 'RT_DLGINCLUDE',
        19: 'RT_PLUGPLAY',
        20: 'RT_VXD',
        21: 'RT_ANICURSOR',
        22: 'RT_ANIICON',
        23: 'RT_HTML',
        24: 'RT_MANIFEST'
    }
    
    # Look for resource type strings
    for rtype_id, rtype_name in resource_types.items():
        if rtype_name.encode() in rsrc_data:
            print(f"  Found resource type: {rtype_name}")
    
    # Look for strings that might indicate firmware files
    firmware_indicators = [
        b'firmware',
        b'update',
        b'bootloader',
        b'bin',
        b'hex',
        b'fw',
        b'EL',
        b'Eilik'
    ]
    
    for indicator in firmware_indicators:
        if indicator in rsrc_data:
            print(f"  Found firmware indicator: {indicator.decode()}")
    
    # Look for binary data that might be firmware
    # Count non-printable bytes
    non_printable = sum(1 for b in rsrc_data if b < 32 or b > 126)
    printable_ratio = (len(rsrc_data) - non_printable) / len(rsrc_data)
    
    print(f"  Printable ratio: {printable_ratio:.2%}")
    
    if printable_ratio < 0.3:  # Mostly binary data
        print("  Section contains mostly binary data - possible firmware")
        
        # Look for patterns
        patterns = [
            (b'\x00' * 16, 'Null padding'),
            (b'\xff' * 16, 'FF padding'),
            (b'\x55\xaa', 'Bootloader signature'),
            (b'\xaa\x55', 'Alternative bootloader signature')
        ]
        
        for pattern, desc in patterns:
            count = rsrc_data.count(pattern)
            if count > 0:
                print(f"    Found {count} occurrences of {desc}")

def extract_zip_data(data, pos, filename):
    """Extract ZIP data"""
    # Find end of ZIP file
    end_pos = pos
    while end_pos < len(data):
        if data[end_pos:end_pos+4] == b'PK\x05\x06':  # End of central directory
            end_pos += 22  # Skip to end
            break
        end_pos += 1
    
    zip_data = data[pos:end_pos]
    with open(f"{filename}.zip", "wb") as f:
        f.write(zip_data)
    print(f"  Extracted ZIP data to {filename}.zip")

def extract_gzip_data(data, pos, filename):
    """Extract GZIP data"""
    # GZIP files are self-contained, so we need to find the end
    # This is a simplified approach
    end_pos = pos + 1000  # Assume max 1KB for now
    gzip_data = data[pos:end_pos]
    with open(f"{filename}.gz", "wb") as f:
        f.write(gzip_data)
    print(f"  Extracted GZIP data to {filename}.gz")

def extract_bzip2_data(data, pos, filename):
    """Extract BZIP2 data"""
    # BZIP2 files are self-contained
    end_pos = pos + 1000  # Assume max 1KB for now
    bzip2_data = data[pos:end_pos]
    with open(f"{filename}.bz2", "wb") as f:
        f.write(bzip2_data)
    print(f"  Extracted BZIP2 data to {filename}.bz2")

if __name__ == "__main__":
    extract_embedded_resources()