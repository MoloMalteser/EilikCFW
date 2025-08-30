#!/usr/bin/env python3
"""
Examine specific firmware-related areas in EnergizeLab.exe
"""

def examine_firmware_areas():
    exe_path = "EnergizeLab.exe"
    
    with open(exe_path, 'rb') as f:
        data = f.read()
    
    print("=== Examining Firmware-Related Areas ===")
    print()
    
    # Examine bootloader area
    bootloader_pos = 170442
    print(f"Bootloader area at position {bootloader_pos}:")
    start = max(0, bootloader_pos - 20)
    end = min(len(data), bootloader_pos + 100)
    context = data[start:end]
    print(f"Context: {context}")
    print()
    
    # Examine .bin file references
    bin_positions = [5798269, 5798318, 5798375, 5798445, 5798462]
    print("Examining .bin file references:")
    for i, pos in enumerate(bin_positions):
        print(f"  .bin reference {i+1} at position {pos}:")
        start = max(0, pos - 50)
        end = min(len(data), pos + 50)
        context = data[start:end]
        # Try to decode as string
        try:
            string_context = context.decode('utf-8', errors='ignore')
            print(f"    String context: {string_context}")
        except:
            print(f"    Binary context: {context[:20].hex()}")
        print()
    
    # Examine .fw file reference
    fw_pos = 1095793
    print(f".fw file reference at position {fw_pos}:")
    start = max(0, fw_pos - 50)
    end = min(len(data), fw_pos + 50)
    context = data[start:end]
    try:
        string_context = context.decode('utf-8', errors='ignore')
        print(f"String context: {string_context}")
    except:
        print(f"Binary context: {context[:20].hex()}")
    print()
    
    # Look for firmware update patterns
    print("Searching for firmware update patterns...")
    update_patterns = [
        b'firmware update',
        b'update firmware',
        b'flash write',
        b'write flash',
        b'bootloader',
        b'firmware.bin',
        b'update.bin'
    ]
    
    for pattern in update_patterns:
        pos = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            print(f"  Found '{pattern.decode()}' at position {pos}")
            pos += len(pattern)
    
    print()
    
    # Look for potential embedded firmware data
    print("Searching for potential embedded firmware data...")
    
    # Common firmware signatures
    signatures = [
        (b'\x55\xaa', 'Bootloader signature'),
        (b'\xaa\x55', 'Alternative bootloader signature'),
        (b'\x7fELF', 'ELF format'),
        (b'MZ', 'PE format'),
        (b'\x00\x00\x00\x00', 'Null padding'),
    ]
    
    for sig, desc in signatures:
        count = data.count(sig)
        if count > 0:
            print(f"  {desc}: {count} occurrences")
    
    print()
    
    # Look for resource patterns
    print("Searching for resource patterns...")
    resource_patterns = [
        b'RESOURCE',
        b'RT_',
        b'.rsrc',
        b'ICON',
        b'VERSION',
        b'MANIFEST'
    ]
    
    for pattern in resource_patterns:
        pos = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            print(f"  Found '{pattern.decode()}' at position {pos}")
            pos += len(pattern)

if __name__ == "__main__":
    examine_firmware_areas()