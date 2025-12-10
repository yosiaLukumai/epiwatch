#!/usr/bin/env python3
"""
Prepare EpiWatch sensor data for Edge Impulse training
Converts CSV data to Edge Impulse format and splits train/test sets
"""

import pandas as pd
import numpy as np
import json
import os
import argparse
from datetime import datetime

def convert_to_edge_impulse_format(csv_file, output_dir, train_ratio=0.8):
    """Convert CSV data to Edge Impulse JSON format"""
    
    # Read CSV data
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} samples from {csv_file}")
    
    # Get label from the data
    label = df['label'].iloc[0]
    
    # Prepare sensor data (remove timestamp and label columns)
    sensor_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    sensor_data = df[sensor_columns].values
    
    # Calculate window size for 2-second windows at ~50Hz
    window_size = 100  # 2 seconds * 50Hz
    overlap = 50       # 50% overlap
    
    windows = []
    timestamps = []
    
    # Create sliding windows
    for i in range(0, len(sensor_data) - window_size + 1, overlap):
        window = sensor_data[i:i + window_size]
        if len(window) == window_size:
            windows.append(window)
            timestamps.append(int(datetime.now().timestamp() * 1000) + i)
    
    print(f"Created {len(windows)} windows of {window_size} samples each")
    
    # Split into train and test
    split_idx = int(len(windows) * train_ratio)
    train_windows = windows[:split_idx]
    test_windows = windows[split_idx:]
    train_timestamps = timestamps[:split_idx]
    test_timestamps = timestamps[split_idx:]
    
    # Create Edge Impulse format (single sample per file format)
    def create_ei_samples(windows_list, timestamps_list, split_name):
        samples = []
        for i, (window, timestamp) in enumerate(zip(windows_list, timestamps_list)):
            # Flatten the window data and interleave sensor readings
            flattened_values = []
            for sample_idx in range(window_size):
                flattened_values.extend(window[sample_idx])  # [ax, ay, az, gx, gy, gz]
            
            sample = {
                "protected": {
                    "ver": "v1",
                    "alg": "none",
                    "iat": timestamp // 1000  # Convert to seconds
                },
                "signature": "",
                "payload": {
                    "device_name": "ESP32-EpiWatch",
                    "device_type": "ESP32",
                    "interval_ms": 20,
                    "sensors": [
                        {"name": "accX", "units": "m/s2"},
                        {"name": "accY", "units": "m/s2"},
                        {"name": "accZ", "units": "m/s2"},
                        {"name": "gyrX", "units": "dps"},
                        {"name": "gyrY", "units": "dps"},
                        {"name": "gyrZ", "units": "dps"}
                    ],
                    "values": flattened_values,
                    "label": label
                }
            }
            samples.append(sample)
        return samples
    
    train_samples = create_ei_samples(train_windows, train_timestamps, "train")
    test_samples = create_ei_samples(test_windows, test_timestamps, "test")
    
    # Save files
    os.makedirs(output_dir, exist_ok=True)
    
    train_file = os.path.join(output_dir, f"{label}_train.json")
    test_file = os.path.join(output_dir, f"{label}_test.json")
    
    with open(train_file, 'w') as f:
        json.dump(train_samples, f, indent=2)
    
    with open(test_file, 'w') as f:
        json.dump(test_samples, f, indent=2)
    
    print(f"Train data: {len(train_samples)} samples -> {train_file}")
    print(f"Test data: {len(test_samples)} samples -> {test_file}")
    
    return train_samples, test_samples

def merge_datasets(json_files, output_file):
    """Merge multiple JSON files into a single dataset"""
    all_samples = []
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            samples = json.load(f)
            all_samples.extend(samples)
            print(f"Added {len(samples)} samples from {json_file}")
    
    with open(output_file, 'w') as f:
        json.dump(all_samples, f, indent=2)
    
    print(f"Merged dataset: {len(all_samples)} total samples -> {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Prepare data for Edge Impulse training")
    parser.add_argument('--input-dir', '-i', default='../dataset', help='Input directory with CSV files')
    parser.add_argument('--output-dir', '-o', default='edge_impulse_data', help='Output directory for JSON files')
    parser.add_argument('--train-ratio', '-r', type=float, default=0.8, help='Train/test split ratio (default: 0.8)')
    
    args = parser.parse_args()
    
    # Process all CSV files in input directory
    csv_files = []
    for file in os.listdir(args.input_dir):
        if file.endswith('.csv'):
            csv_files.append(os.path.join(args.input_dir, file))
    
    if not csv_files:
        print(f"No CSV files found in {args.input_dir}")
        return
    
    print(f"Found CSV files: {[os.path.basename(f) for f in csv_files]}")
    
    train_files = []
    test_files = []
    
    # Convert each CSV file
    for csv_file in csv_files:
        print(f"\nProcessing {csv_file}...")
        train_samples, test_samples = convert_to_edge_impulse_format(
            csv_file, args.output_dir, args.train_ratio
        )
        
        label = os.path.basename(csv_file).replace('.csv', '')
        train_files.append(os.path.join(args.output_dir, f"{label}_train.json"))
        test_files.append(os.path.join(args.output_dir, f"{label}_test.json"))
    
    # Merge all training and test data
    print(f"\nMerging datasets...")
    merge_datasets(train_files, os.path.join(args.output_dir, "training_data.json"))
    merge_datasets(test_files, os.path.join(args.output_dir, "testing_data.json"))
    
    print(f"\n✅ Data preparation complete!")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"📄 Files ready for Edge Impulse upload:")
    print(f"   - training_data.json")
    print(f"   - testing_data.json")

if __name__ == "__main__":
    main()