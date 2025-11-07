#!/usr/bin/env python3
"""
Prepare Seattle Customer Service Request data for 3D visualization.
Filters to 2024-2025 data and exports to JSON format for deck.gl.
"""

import pandas as pd
import json
from datetime import datetime

def prepare_data():
    print("Loading CSV data...")

    # Load the CSV file
    df = pd.read_csv('Customer_Service_Requests_20251106.csv')

    print(f"Total records loaded: {len(df):,}")

    # Convert Created Date to datetime
    df['Created Date'] = pd.to_datetime(df['Created Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

    # Filter to 2024-2025 data
    df_filtered = df[df['Created Date'].dt.year.isin([2024, 2025])].copy()

    print(f"Records from 2024-2025: {len(df_filtered):,}")

    # Filter out records without valid coordinates
    df_filtered = df_filtered.dropna(subset=['Latitude', 'Longitude'])

    print(f"Records with valid coordinates: {len(df_filtered):,}")

    # Create simplified dataset for visualization
    viz_data = []

    for idx, row in df_filtered.iterrows():
        viz_data.append({
            'lat': float(row['Latitude']),
            'lon': float(row['Longitude']),
            'type': str(row['Service Request Type']) if pd.notna(row['Service Request Type']) else 'Unknown',
            'department': str(row['City Department']) if pd.notna(row['City Department']) else 'Unknown',
            'date': row['Created Date'].strftime('%Y-%m-%d') if pd.notna(row['Created Date']) else None,
            'status': str(row['Status']) if pd.notna(row['Status']) else 'Unknown',
            'community': str(row['Community Reporting Area']) if pd.notna(row['Community Reporting Area']) else 'Unknown'
        })

    # Generate statistics
    stats = {
        'total_records': len(viz_data),
        'date_range': {
            'start': df_filtered['Created Date'].min().strftime('%Y-%m-%d'),
            'end': df_filtered['Created Date'].max().strftime('%Y-%m-%d')
        },
        'top_request_types': df_filtered['Service Request Type'].value_counts().head(10).to_dict(),
        'top_departments': df_filtered['City Department'].value_counts().head(5).to_dict(),
        'bounds': {
            'min_lat': float(df_filtered['Latitude'].min()),
            'max_lat': float(df_filtered['Latitude'].max()),
            'min_lon': float(df_filtered['Longitude'].min()),
            'max_lon': float(df_filtered['Longitude'].max())
        }
    }

    # Export to JSON
    output = {
        'data': viz_data,
        'stats': stats
    }

    print("\nWriting JSON file...")
    with open('seattle_requests_2024_2025.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Successfully created seattle_requests_2024_2025.json")
    print(f"\nDataset Statistics:")
    print(f"  Total records: {stats['total_records']:,}")
    print(f"  Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    print(f"  Geographic bounds:")
    print(f"    Latitude: {stats['bounds']['min_lat']:.4f} to {stats['bounds']['max_lat']:.4f}")
    print(f"    Longitude: {stats['bounds']['min_lon']:.4f} to {stats['bounds']['max_lon']:.4f}")
    print(f"\nTop 5 Request Types:")
    for req_type, count in list(stats['top_request_types'].items())[:5]:
        print(f"    {req_type}: {count:,}")

if __name__ == '__main__':
    prepare_data()
