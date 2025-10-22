import requests
import csv
import os
from datetime import datetime
from pathlib import Path

# Configuration
REPO = os.environ['REPO']
TOKEN = os.environ['GH_TOKEN']

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

base_url = f'https://api.github.com/repos/{REPO}'

def fetch_traffic_data():
    """Fetch all traffic data from GitHub API"""
    return {
        'views': requests.get(f'{base_url}/traffic/views', headers=headers).json(),
        'clones': requests.get(f'{base_url}/traffic/clones', headers=headers).json(),
        'paths': requests.get(f'{base_url}/traffic/popular/paths', headers=headers).json(),
        'referrers': requests.get(f'{base_url}/traffic/popular/referrers', headers=headers).json()
    }

def append_to_csv(filename, data, fieldnames):
    """Append data to CSV, creating file with headers if it doesn't exist"""
    file_exists = Path(filename).exists()
    
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        if isinstance(data, list):
            writer.writerows(data)
        else:
            writer.writerow(data)

def process_views_and_clones(data, data_type):
    """Process views or clones data into daily records"""
    records = []
    
    for item in data.get(data_type, []):
        records.append({
            'date': item['timestamp'][:10],  # Just the date part
            'timestamp': item['timestamp'],
            'count': item['count'],
            'uniques': item['uniques']
        })
    
    return records

def process_paths(paths_data):
    """Process popular paths data"""
    today = datetime.now().date().isoformat()
    records = []
    
    for path in paths_data:
        records.append({
            'date': today,
            'path': path['path'],
            'title': path['title'],
            'count': path['count'],
            'uniques': path['uniques']
        })
    
    return records

def process_referrers(referrers_data):
    """Process referrers data"""
    today = datetime.now().date().isoformat()
    records = []
    
    for referrer in referrers_data:
        records.append({
            'date': today,
            'referrer': referrer['referrer'],
            'count': referrer['count'],
            'uniques': referrer['uniques']
        })
    
    return records

def deduplicate_csv(filename, key_fields):
    """Remove duplicate rows based on key fields, keeping the latest entry"""
    if not Path(filename).exists():
        return
    
    # Read all rows
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Deduplicate - keep last occurrence of each key
    seen = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        seen[key] = row
    
    # Write back
    if seen:
        fieldnames = rows[0].keys()
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(seen.values())

def main():
    # Create data directory if it doesn't exist
    Path('data').mkdir(exist_ok=True)
    
    print("Fetching traffic data from GitHub API...")
    traffic_data = fetch_traffic_data()
    
    # Process and append views
    print("Processing views data...")
    views_records = process_views_and_clones(traffic_data['views'], 'views')
    append_to_csv('data/traffic_views.csv', views_records, 
                  ['date', 'timestamp', 'count', 'uniques'])
    deduplicate_csv('data/traffic_views.csv', ['date'])
    
    # Process and append clones
    print("Processing clones data...")
    clones_records = process_views_and_clones(traffic_data['clones'], 'clones')
    append_to_csv('data/traffic_clones.csv', clones_records,
                  ['date', 'timestamp', 'count', 'uniques'])
    deduplicate_csv('data/traffic_clones.csv', ['date'])
    
    # Process and append paths
    print("Processing popular paths...")
    paths_records = process_paths(traffic_data['paths'])
    append_to_csv('data/traffic_paths.csv', paths_records,
                  ['date', 'path', 'title', 'count', 'uniques'])
    deduplicate_csv('data/traffic_paths.csv', ['date', 'path'])
    
    # Process and append referrers
    print("Processing referrers...")
    referrers_records = process_referrers(traffic_data['referrers'])
    append_to_csv('data/traffic_referrers.csv', referrers_records,
                  ['date', 'referrer', 'count', 'uniques'])
    deduplicate_csv('data/traffic_referrers.csv', ['date', 'referrer'])
    
    # Summary
    print("\n✓ Traffic data processed successfully!")
    print(f"  - Views: {len(views_records)} records")
    print(f"  - Clones: {len(clones_records)} records")
    print(f"  - Paths: {len(paths_records)} records")
    print(f"  - Referrers: {len(referrers_records)} records")

if __name__ == '__main__':
    main()
