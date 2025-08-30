#!/usr/bin/env python3
"""
Eilik Robot Emulator
For testing CFW development and communication protocols
"""

import time
import struct
import threading
import random
import math
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ServoState:
    """Servo state representation"""
    id: int
    position: int = 500  # 0-1000 range
    target: int = 500
    speed: int = 50      # 0-100 range
    torque: int = 100    # 0-100 range
    temperature: int = 25 # Celsius
    voltage: float = 5.0 # Volts
    status: int = 0      # Status flags
    moving: bool = False

class EilikEmulator:
    def __init__(self):
        self.servos: Dict[int, ServoState] = {}
        self.firmware_version = "1.0.0"
        self.device_id = "EILIK_EMU_001"
        self.connected = False
        self.bootloader_mode = False
        self.firmware_data = bytearray()
        
        # Initialize servos
        for i in range(8):
            self.servos[i] = ServoState(id=i)
        
        # Communication protocol
        self.commands = {
            0x01: self.cmd_device_info,
            0x02: self.cmd_firmware_update,
            0x03: self.cmd_parameter_read,
            0x04: self.cmd_parameter_write,
            0x05: self.cmd_servo_control,
            0x06: self.cmd_sensor_read,
            0x07: self.cmd_calibration,
            0x08: self.cmd_reset,
            0x09: self.cmd_bootloader_mode,
            0x0A: self.cmd_flash_write
        }
        
        self.responses = {
            0x80: "ACK",
            0x81: "NACK", 
            0x82: "DATA",
            0x83: "ERROR",
            0x84: "BUSY",
            0x85: "READY"
        }
        
        # Start servo simulation thread
        self.running = True
        self.servo_thread = threading.Thread(target=self._servo_simulation)
        self.servo_thread.daemon = True
        self.servo_thread.start()
    
    def _servo_simulation(self):
        """Simulate servo movement and sensor readings"""
        while self.running:
            for servo in self.servos.values():
                # Simulate movement towards target
                if servo.moving and servo.position != servo.target:
                    diff = servo.target - servo.position
                    step = servo.speed // 10
                    if abs(diff) <= step:
                        servo.position = servo.target
                        servo.moving = False
                    else:
                        servo.position += step if diff > 0 else -step
                
                # Simulate temperature changes
                if servo.moving:
                    servo.temperature = min(80, servo.temperature + random.randint(0, 2))
                else:
                    servo.temperature = max(20, servo.temperature - random.randint(0, 1))
                
                # Simulate voltage fluctuations
                servo.voltage = 5.0 + random.uniform(-0.2, 0.2)
            
            time.sleep(0.1)  # 100ms update rate
    
    def process_command(self, data: bytes) -> bytes:
        """Process incoming command and return response"""
        if len(data) < 4:
            return self._create_response(0x83, b"Invalid packet")
        
        # Parse packet header
        header = struct.unpack('<H', data[0:2])[0]
        if header != 0xAA55:
            return self._create_response(0x83, b"Invalid header")
        
        command = data[2]
        length = data[3]
        payload = data[4:4+length] if length > 0 else b''
        
        print(f"Received command: 0x{command:02X}, length: {length}")
        
        # Process command
        if command in self.commands:
            try:
                return self.commands[command](payload)
            except Exception as e:
                print(f"Command error: {e}")
                return self._create_response(0x83, str(e).encode())
        else:
            return self._create_response(0x83, b"Unknown command")
    
    def _create_response(self, response_type: int, data: bytes = b'') -> bytes:
        """Create response packet"""
        response = struct.pack('<HBB', 0xAA55, response_type, len(data))
        if data:
            response += data
        return response
    
    def cmd_device_info(self, payload: bytes) -> bytes:
        """Device information command"""
        info = struct.pack('<16s8sHH',
            self.device_id.encode(),
            self.firmware_version.encode(),
            0x0100,  # Hardware version
            0x0000   # Flags
        )
        return self._create_response(0x82, info)
    
    def cmd_firmware_update(self, payload: bytes) -> bytes:
        """Firmware update command"""
        if not payload:
            return self._create_response(0x81, b"No firmware data")
        
        # Store firmware data
        self.firmware_data.extend(payload)
        print(f"Received {len(payload)} bytes of firmware data")
        
        return self._create_response(0x80, b"Firmware data received")
    
    def cmd_parameter_read(self, payload: bytes) -> bytes:
        """Parameter read command"""
        if len(payload) < 2:
            return self._create_response(0x83, b"Invalid parameter address")
        
        addr = struct.unpack('<H', payload[0:2])[0]
        
        # Read parameter based on address
        if addr == 0x0000:  # Servo parameters
            data = bytearray()
            for servo in self.servos.values():
                servo_data = struct.pack('<BBHHBBBB',
                    servo.id,
                    servo.status,
                    servo.position,
                    servo.target,
                    servo.speed,
                    servo.torque,
                    int(servo.temperature),
                    int(servo.voltage * 10)
                )
                data.extend(servo_data)
            return self._create_response(0x82, data)
        else:
            return self._create_response(0x83, b"Invalid parameter address")
    
    def cmd_parameter_write(self, payload: bytes) -> bytes:
        """Parameter write command"""
        if len(payload) < 4:
            return self._create_response(0x83, b"Invalid parameter data")
        
        addr = struct.unpack('<H', payload[0:2])[0]
        data = payload[2:]
        
        # Write parameter based on address
        if addr == 0x0000:  # Servo parameters
            servo_id = data[0]
            if servo_id in self.servos:
                servo = self.servos[servo_id]
                if len(data) >= 8:
                    servo.target = struct.unpack('<H', data[1:3])[0]
                    servo.speed = data[3]
                    servo.torque = data[4]
                    servo.moving = True
                    print(f"Servo {servo_id}: target={servo.target}, speed={servo.speed}")
                    return self._create_response(0x80, b"Parameter written")
        
        return self._create_response(0x83, b"Invalid parameter")
    
    def cmd_servo_control(self, payload: bytes) -> bytes:
        """Servo control command"""
        if len(payload) < 4:
            return self._create_response(0x83, b"Invalid servo command")
        
        servo_id = payload[0]
        command_type = payload[1]
        
        if servo_id not in self.servos:
            return self._create_response(0x83, b"Invalid servo ID")
        
        servo = self.servos[servo_id]
        
        if command_type == 0x01:  # Set position
            if len(payload) >= 4:
                position = struct.unpack('<H', payload[2:4])[0]
                servo.target = position
                servo.moving = True
                print(f"Servo {servo_id} moving to position {position}")
                return self._create_response(0x80, b"Position set")
        
        elif command_type == 0x02:  # Set speed
            if len(payload) >= 3:
                speed = payload[2]
                servo.speed = speed
                print(f"Servo {servo_id} speed set to {speed}")
                return self._create_response(0x80, b"Speed set")
        
        elif command_type == 0x03:  # Read status
            status_data = struct.pack('<BBHHBBBB',
                servo.id,
                servo.status,
                servo.position,
                servo.target,
                servo.speed,
                servo.torque,
                int(servo.temperature),
                int(servo.voltage * 10)
            )
            return self._create_response(0x82, status_data)
        
        return self._create_response(0x83, b"Invalid servo command")
    
    def cmd_sensor_read(self, payload: bytes) -> bytes:
        """Sensor read command"""
        sensor_data = bytearray()
        
        # Simulate sensor readings
        for servo in self.servos.values():
            sensor_data.extend(struct.pack('<BBf',
                servo.id,
                int(servo.temperature),
                servo.voltage
            ))
        
        return self._create_response(0x82, sensor_data)
    
    def cmd_calibration(self, payload: bytes) -> bytes:
        """Calibration command"""
        print("Calibration command received")
        return self._create_response(0x80, b"Calibration started")
    
    def cmd_reset(self, payload: bytes) -> bytes:
        """Reset command"""
        print("Reset command received")
        # Reset servo positions
        for servo in self.servos.values():
            servo.position = 500
            servo.target = 500
            servo.moving = False
        return self._create_response(0x80, b"Reset completed")
    
    def cmd_bootloader_mode(self, payload: bytes) -> bytes:
        """Bootloader mode command"""
        self.bootloader_mode = True
        print("Entering bootloader mode")
        return self._create_response(0x80, b"Bootloader mode")
    
    def cmd_flash_write(self, payload: bytes) -> bytes:
        """Flash write command"""
        if not self.bootloader_mode:
            return self._create_response(0x83, b"Not in bootloader mode")
        
        print(f"Flash write: {len(payload)} bytes")
        return self._create_response(0x80, b"Flash write successful")
    
    def get_servo_status(self) -> Dict[int, Dict]:
        """Get current servo status"""
        status = {}
        for servo_id, servo in self.servos.items():
            status[servo_id] = {
                'position': servo.position,
                'target': servo.target,
                'speed': servo.speed,
                'torque': servo.torque,
                'temperature': servo.temperature,
                'voltage': servo.voltage,
                'moving': servo.moving
            }
        return status
    
    def simulate_behavior(self, behavior: str):
        """Simulate robot behaviors"""
        if behavior == "wave":
            # Wave animation
            self.servos[0].target = 800  # Right arm up
            self.servos[0].moving = True
            time.sleep(1)
            self.servos[0].target = 200  # Right arm down
            self.servos[0].moving = True
            print("Wave animation completed")
        
        elif behavior == "dance":
            # Dance animation
            for i in range(4):
                for servo in self.servos.values():
                    servo.target = random.randint(200, 800)
                    servo.moving = True
                time.sleep(0.5)
            print("Dance animation completed")
        
        elif behavior == "idle":
            # Idle behavior
            for servo in self.servos.values():
                servo.target = 500
                servo.moving = True
            print("Idle behavior activated")

def main():
    """Test the emulator"""
    print("=== EILIK ROBOT EMULATOR ===")
    print()
    
    emulator = EilikEmulator()
    
    print("Emulator initialized with 8 servos")
    print("Available commands:")
    for cmd_id, cmd_name in emulator.commands.items():
        print(f"  0x{cmd_id:02X}: {cmd_name.__name__}")
    print()
    
    # Test device info
    print("Testing device info command...")
    cmd = struct.pack('<HBB', 0xAA55, 0x01, 0x00)
    response = emulator.process_command(cmd)
    print(f"Response: {response.hex()}")
    print()
    
    # Test servo control
    print("Testing servo control...")
    cmd = struct.pack('<HBBH', 0xAA55, 0x05, 0x04, 0x01)  # Set servo 0 position
    cmd += struct.pack('<H', 750)  # Position 750
    response = emulator.process_command(cmd)
    print(f"Response: {response.hex()}")
    print()
    
    # Show servo status
    print("Current servo status:")
    status = emulator.get_servo_status()
    for servo_id, servo_status in status.items():
        print(f"  Servo {servo_id}: pos={servo_status['position']}, "
              f"target={servo_status['target']}, moving={servo_status['moving']}")
    
    print()
    print("Emulator ready for CFW testing!")

if __name__ == "__main__":
    main()