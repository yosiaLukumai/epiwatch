#!/usr/bin/env python3
"""
EpiWatch Data Collector
Collects sensor data from ESP32 via serial port for Edge Impulse training
"""

import serial
import csv
import datetime
import time
import argparse
import os
import sys

def find_serial_port():
    """Try to find the ESP32 serial port automatically"""
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    esp32_ports = []
    
    for port in ports:
        # Common ESP32 USB-to-serial chip manufacturers
        if any(vendor in (port.manufacturer or "").lower() for vendor in 
               ["silicon labs", "ftdi", "prolific", "ch340", "cp210x"]):
            esp32_ports.append(port.device)
    
    return esp32_ports

def collect_data(port, baudrate, output_file, duration, label):
    """Collect sensor data from ESP32"""
    
    print(f"Connecting to {port} at {baudrate} baud...")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for connection to establish
        
        print(f"Connected! Starting data collection for label: {label}")
        print(f"Collection will last {duration} seconds")
        print("Press Ctrl+C to stop early")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'accel_x', 'accel_y', 'accel_z', 
                         'gyro_x', 'gyro_y', 'gyro_z', 'label']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Send START command to ESP32
            ser.write(b'START\n')
            
            start_time = time.time()
            sample_count = 0
            
            try:
                while (time.time() - start_time) < duration:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                    except UnicodeDecodeError:
                        continue  # Skip lines with encoding issues
                    
                    if not line:  # Skip empty lines
                        continue
                        
                    if line.startswith('DATA_COLLECTION_STARTED'):
                        print("ESP32 confirmed data collection started")
                        continue
                    elif line.startswith(('READY:', 'FORMAT:', 'ERROR:')):
                        print(f"ESP32: {line}")
                        continue
                    
                    # Parse CSV data line
                    if ',' in line and not line.startswith(('READY', 'FORMAT', 'ERROR')):
                        try:
                            parts = line.split(',')
                            if len(parts) == 7:  # timestamp + 6 sensor values
                                # Validate that all parts are numeric (except timestamp)
                                float(parts[1])  # Test if accel_x is numeric
                                float(parts[2])  # Test if accel_y is numeric
                                float(parts[3])  # Test if accel_z is numeric
                                float(parts[4])  # Test if gyro_x is numeric
                                float(parts[5])  # Test if gyro_y is numeric
                                float(parts[6])  # Test if gyro_z is numeric
                                
                                writer.writerow({
                                    'timestamp': parts[0],
                                    'accel_x': parts[1],
                                    'accel_y': parts[2],
                                    'accel_z': parts[3],
                                    'gyro_x': parts[4],
                                    'gyro_y': parts[5],
                                    'gyro_z': parts[6],
                                    'label': label
                                })
                                sample_count += 1
                                
                                if sample_count % 50 == 0:  # Progress update every 50 samples
                                    elapsed = time.time() - start_time
                                    print(f"Collected {sample_count} samples in {elapsed:.1f}s")
                        
                        except (ValueError, IndexError):
                            continue  # Skip malformed lines
                            
            except KeyboardInterrupt:
                print("\nCollection interrupted by user")
            
            # Send STOP command to ESP32
            ser.write(b'STOP\n')
            time.sleep(0.5)
            
            elapsed = time.time() - start_time
            print(f"\nData collection completed!")
            print(f"Total samples: {sample_count}")
            print(f"Duration: {elapsed:.1f} seconds")
            print(f"Average sample rate: {sample_count/elapsed:.1f} Hz")
            print(f"Data saved to: {output_file}")
            
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        sys.exit(1)
    
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def main():
    parser = argparse.ArgumentParser(description="Collect sensor data from ESP32 for Edge Impulse")
    parser.add_argument('--port', '-p', help='Serial port (e.g., /dev/ttyUSB0, COM3)')
    parser.add_argument('--baudrate', '-b', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file path')
    parser.add_argument('--duration', '-d', type=int, default=30, help='Collection duration in seconds (default: 30)')
    parser.add_argument('--label', '-l', required=True, help='Data label (e.g., "normal", "seizure", "walking")')
    
    args = parser.parse_args()
    
    # Auto-detect port if not specified
    if not args.port:
        available_ports = find_serial_port()
        if not available_ports:
            print("No ESP32-compatible serial ports found!")
            print("Please specify port manually with --port")
            sys.exit(1)
        elif len(available_ports) == 1:
            args.port = available_ports[0]
            print(f"Auto-detected port: {args.port}")
        else:
            print("Multiple possible ports found:")
            for i, port in enumerate(available_ports):
                print(f"  {i+1}: {port}")
            choice = input("Select port number: ")
            try:
                args.port = available_ports[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice")
                sys.exit(1)
    
    collect_data(args.port, args.baudrate, args.output, args.duration, args.label)

if __name__ == "__main__":
    main()