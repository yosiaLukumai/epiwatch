#!/usr/bin/env python3
"""
Prepare EpiWatch sensor data as CSV for Edge Impulse web upload
Simple CSV format that works with Edge Impulse web interface
"""

import pandas as pd
import os
import argparse
from datetime import datetime

def convert_to_csv_format(csv_file, output_dir, train_ratio=0.8, window_size=100, overlap=50):
    """Convert CSV data to Edge Impulse CSV format"""
    
    # Read CSV data
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} samples from {csv_file}")
    
    # Get label from the data
    label = df['label'].iloc[0]
    
    # Prepare sensor data (remove timestamp and label columns)
    sensor_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    sensor_data = df[sensor_columns].values
    
    # Create sliding windows
    windows = []
    for i in range(0, len(sensor_data) - window_size + 1, overlap):
        window = sensor_data[i:i + window_size]
        if len(window) == window_size:
            windows.append(window)
    
    print(f"Created {len(windows)} windows of {window_size} samples each")
    
    # Split into train and test
    split_idx = int(len(windows) * train_ratio)
    train_windows = windows[:split_idx]
    test_windows = windows[split_idx:]
    
    def create_csv_samples(windows_list, split_name):
        rows = []
        for i, window in enumerate(windows_list):
            # Flatten window data - each row is one time series sample
            sample_row = {f'timestamp': i}  # Simple incrementing timestamp
            
            # Add all sensor readings in sequence
            for t in range(window_size):
                sample_row[f'accel_x_{t}'] = window[t][0]
                sample_row[f'accel_y_{t}'] = window[t][1] 
                sample_row[f'accel_z_{t}'] = window[t][2]
                sample_row[f'gyro_x_{t}'] = window[t][3]
                sample_row[f'gyro_y_{t}'] = window[t][4]
                sample_row[f'gyro_z_{t}'] = window[t][5]
            
            sample_row['label'] = label
            rows.append(sample_row)
        
        return pd.DataFrame(rows)
    
    # Create DataFrames
    train_df = create_csv_samples(train_windows, "train")
    test_df = create_csv_samples(test_windows, "test")
    
    # Save CSV files
    os.makedirs(output_dir, exist_ok=True)
    
    train_file = os.path.join(output_dir, f"{label}_train.csv")
    test_file = os.path.join(output_dir, f"{label}_test.csv")
    
    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f"Train data: {len(train_df)} samples -> {train_file}")
    print(f"Test data: {len(test_df)} samples -> {test_file}")
    
    return train_df, test_df

def create_simple_csv_format(csv_file, output_dir, window_size=100, overlap=50):
    """Create simple CSV format for Edge Impulse - one file per window"""
    
    # Read CSV data
    df = pd.read_csv(csv_file)
    label = df['label'].iloc[0]
    
    # Prepare sensor data
    sensor_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    sensor_data = df[sensor_columns].copy()
    
    # Add timestamp column (20ms intervals for 50Hz)
    sensor_data.insert(0, 'timestamp', range(0, len(sensor_data) * 20, 20))
    
    # Create output directory
    os.makedirs(os.path.join(output_dir, label), exist_ok=True)
    
    # Create windows and save as separate CSV files
    window_count = 0
    for i in range(0, len(sensor_data) - window_size + 1, overlap):
        window = sensor_data.iloc[i:i + window_size].copy()
        
        if len(window) == window_size:
            # Reset timestamp to start from 0 for each window
            window['timestamp'] = range(0, len(window) * 20, 20)
            
            # Save window as individual CSV file
            output_file = os.path.join(output_dir, label, f"{label}_{window_count:04d}.csv")
            window.to_csv(output_file, index=False)
            window_count += 1
    
    print(f"Created {window_count} individual CSV files in {output_dir}/{label}/")
    return window_count

def main():
    parser = argparse.ArgumentParser(description="Prepare CSV data for Edge Impulse web upload")
    parser.add_argument('--input-dir', '-i', default='../dataset', help='Input directory with CSV files')
    parser.add_argument('--output-dir', '-o', default='edge_impulse_csv', help='Output directory for CSV files')
    parser.add_argument('--format', choices=['merged', 'individual'], default='individual', 
                       help='Output format: merged CSV or individual files')
    
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
    
    total_files = 0
    
    if args.format == 'individual':
        print("\nCreating individual CSV files (recommended for Edge Impulse web interface)...")
        for csv_file in csv_files:
            print(f"\nProcessing {csv_file}...")
            count = create_simple_csv_format(csv_file, args.output_dir)
            total_files += count
    else:
        print("\nCreating merged CSV files...")
        train_dfs = []
        test_dfs = []
        
        for csv_file in csv_files:
            print(f"\nProcessing {csv_file}...")
            train_df, test_df = convert_to_csv_format(csv_file, args.output_dir)
            train_dfs.append(train_df)
            test_dfs.append(test_df)
        
        # Merge all data
        final_train = pd.concat(train_dfs, ignore_index=True)
        final_test = pd.concat(test_dfs, ignore_index=True)
        
        final_train.to_csv(os.path.join(args.output_dir, "training_data.csv"), index=False)
        final_test.to_csv(os.path.join(args.output_dir, "testing_data.csv"), index=False)
        
        total_files = 2
    
    print(f"\n✅ Data preparation complete!")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"📄 Created {total_files} CSV files for Edge Impulse upload")
    
    if args.format == 'individual':
        print(f"\n🔧 Upload instructions:")
        print(f"1. Go to Edge Impulse project > Data acquisition")
        print(f"2. Click 'Upload data' > 'Select a folder'")
        print(f"3. Upload each label folder (normal/, seizure/) separately")
        print(f"4. Set correct category (Training/Testing) and label")

if __name__ == "__main__":
    main()