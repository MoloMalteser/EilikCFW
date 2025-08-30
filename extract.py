#!/usr/bin/env python3
import os
import sys

def analyze_exe():
    exe_path = "EnergizeLab.exe"
    if not os.path.exists(exe_path):
        print(f"Executable {exe_path} not found")
        return
    
    print(f"Analyzing {exe_path}...")
    
    with open(exe_path, 'rb') as f:
        data = f.read()
    
    # Look for PyInstaller magic
    magic = b'MEI\014\013\012\013\016'
    pos = data.rfind(magic)
    
    if pos != -1:
        print(f"Found PyInstaller archive at position {pos}")
        print(f"Archive size: {len(data) - pos} bytes")
        
        # Look for Python strings
        python_strings = []
        for i in range(pos, len(data) - 4):
            if data[i:i+4] == b'.pyc':
                # Try to find start of string
                start = i
                while start > pos and data[start-1] >= 32 and data[start-1] <= 126:
                    start -= 1
                if start < i:
                    string = data[start:i+4].decode('utf-8', errors='ignore')
                    if string.endswith('.pyc') and len(string) > 4:
                        python_strings.append(string)
        
        print(f"Found {len(python_strings)} Python module references:")
        for s in sorted(set(python_strings))[:20]:
            print(f"  {s}")
    else:
        print("PyInstaller archive not found")

if __name__ == "__main__":
    analyze_exe()
