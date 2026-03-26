import csv
import collections
import argparse
import os
import sys
from datetime import datetime

def analyze(input_file, mode):
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    # Counters
    total_rows = 0
    cachebuster_errors = 0
    guid_counts = collections.Counter()
    ip_counts = collections.Counter()
    ua_counts = collections.Counter()
    country_counts = collections.Counter()
    ip_minute_counts = collections.Counter()
    hour_counts = collections.Counter()
    
    # Samples for CSV reports
    cb_error_samples = []
    
    # Campaign Start Tracking
    placement_stats = collections.defaultdict(lambda: {'imps': 0, 'clicks': 0})

    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Dynamic Header Mapping
            mapping = {
                'guid': next((h for h in headers if h.lower() in ['guid', 'user_id', 'visitor_id']), None),
                'ip': next((h for h in headers if h.lower() in ['ip_address', 'request_ip_address', 'ip']), None),
                'ua': next((h for h in headers if h.lower() in ['agent_string', 'user_agent', 'browser']), None),
                'country': next((h for h in headers if h.lower() in ['country_name', 'country', 'geo_country']), None),
                'time': next((h for h in headers if h.lower() in ['event_time', 'timestamp', 'time']), None),
                'query': next((h for h in headers if h.lower() in ['query_string', 'url', 'params']), None),
                'placement': next((h for h in headers if h.lower() in ['idspotlight', 'placement_id', 'campaign_id', 'idplacement']), None)
            }

            for row in reader:
                total_rows += 1
                
                # GUID Analysis
                guid_val = '99999999999999'
                if mapping['guid']:
                    guid_val = row.get(mapping['guid'], '99999999999999')
                    guid_counts[guid_val] += 1
                
                # IP Analysis
                ip_val = 'UNKNOWN'
                if mapping['ip']:
                    ip_val = row.get(mapping['ip'], 'UNKNOWN')
                    ip_counts[ip_val] += 1
                
                # UA Analysis
                ua_val = 'UNKNOWN'
                if mapping['ua']:
                    ua_val = row.get(mapping['ua'], 'UNKNOWN')
                    ua_counts[ua_val] += 1
                
                # Geography
                if mapping['country']:
                    country = row.get(mapping['country'], 'UNKNOWN')
                    country_counts[country] += 1
                
                # Cachebuster Check
                if mapping['query']:
                    qs = row.get(mapping['query'], '')
                    if '[%RANDOM_NUMBER%]' in qs:
                        cachebuster_errors += 1
                        if len(cb_error_samples) < 1000:
                            cb_error_samples.append({
                                'IP': ip_val,
                                'Time': row.get(mapping['time'], 'N/A'),
                                'Query': qs,
                                'Issue': 'Unreplaced Macro'
                            })
                
                # Time Analysis
                if mapping['time']:
                    raw_time = row.get(mapping['time'], '').strip()
                    if raw_time:
                        dt = None
                        try:
                            base_time = raw_time.split('.')[0] if '.' in raw_time else raw_time
                            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y %H:%M:%S'):
                                try:
                                    dt = datetime.strptime(base_time, fmt)
                                    break
                                except:
                                    continue
                            
                            if dt:
                                hour_counts[dt.hour] += 1
                                minute = raw_time[:16]
                                if mapping['ip']:
                                    ip_minute_counts[(ip_val, minute)] += 1
                        except:
                            pass
                
                # Placement Stats
                if mode == 'campaign' and mapping['placement']:
                    pid = row.get(mapping['placement'], 'Default')
                    placement_stats[pid]['imps'] += 1

    except Exception as e:
        print(f"Error processing: {e}")
        return

    # --- GENERATE CSV REPORTS ---
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_folder = f"Audit_{base_name}_{timestamp}"
    os.makedirs(report_folder, exist_ok=True)

    # 1. Summary CSV
    with open(f'{report_folder}/01_Summary.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Metric', 'Count', 'Percentage'])
        w.writerow(['Total Rows', total_rows, '100%'])
        w.writerow(['Cachebuster Errors', cachebuster_errors, f"{cachebuster_errors/max(1,total_rows)*100:.2f}%"])
        w.writerow(['Placeholder GUIDs (99s)', guid_counts.get('99999999999999', 0), f"{guid_counts.get('99999999999999', 0)/max(1,total_rows)*100:.2f}%"])
        w.writerow(['Unique IPs', len(ip_counts), '-'])

    # 2. Top IPs CSV
    with open(f'{report_folder}/02_Top_IPs.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['IP_Address', 'Count', 'Share'])
        for ip, count in ip_counts.most_common(500):
            w.writerow([ip, count, f"{count/max(1,total_rows)*100:.2f}%"])

    # 3. Frequency CSV (Spikes)
    with open(f'{report_folder}/03_Frequency_Spikes.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['IP', 'Minute', 'Requests_Per_Minute'])
        sorted_freq = sorted(ip_minute_counts.items(), key=lambda x: x[1], reverse=True)
        for (ip, minute), count in sorted_freq:
            if count > 5:
                w.writerow([ip, minute, count])
            else:
                break

    # 4. Error Samples CSV
    if cb_error_samples:
        with open(f'{report_folder}/04_Implementation_Errors.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['IP', 'Time', 'Query', 'Issue'])
            w.writeheader()
            w.writerows(cb_error_samples)

    # --- OUTPUT FOR AGENT ---
    print(f"REPORT_FOLDER|{report_folder}")
    print(f"TOTAL_ROWS|{total_rows}")
    print(f"AVAILABLE_COLS|{','.join([k for k,v in mapping.items() if v])}")
    print(f"CACHEBUSTER_ERRORS|{cachebuster_errors}")
    print(f"GUID_PLACEHOLDERS|{guid_counts.get('99999999999999', 0)}")
    print(f"UNIQUE_IPS|{len(ip_counts)}")
    
    print("HOURLY_DISTRIBUTION")
    for h in range(24):
        print(f"{h}|{hour_counts[h]}")
        
    print("TOP_IPS")
    for ip, count in ip_counts.most_common(10):
        print(f"{ip}|{count}")

    print("TOP_UA")
    for ua, count in ua_counts.most_common(5):
        print(f"{ua[:100]}|{count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-m', '--mode', choices=['fraud', 'campaign'], default='fraud')
    args = parser.parse_args()
    analyze(args.file, args.mode)
