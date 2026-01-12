import requests
import json
import gzip
import datetime
import time
import sys

# Updated Configuration for 2026 Bypass
CHANNELS_API = "https://jiotv.data.cdn.jio.com/apis/v3.0/getMobileChannelList/get/?langId=6&os=android&devicetype=phone"
EPG_API = "http://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get"

# These headers are mandatory to avoid Error 450
HEADERS = {
    "User-Agent": "JioTV/7.0.9 (Linux; Android 13)",
    "os": "android",
    "devicetype": "phone",
    "app-name": "RJIL_JioTV",
    "Accept": "application/json",
    "x-api-key": "no-key", # Some v3.0 endpoints expect this placeholder
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

def generate_epg():
    print("Connecting to JioTV Servers (v3.0)...")
    
    try:
        # Use a session to keep cookies/headers consistent
        session = requests.Session()
        session.headers.update(HEADERS)
        
        response = session.get(CHANNELS_API, timeout=20)
        
        if response.status_code == 450:
            print("❌ Error 450: Jio blocked the request. Fix: Use an Indian IP/VPN.")
            return

        response.raise_for_status()
        channels = response.json().get('result', [])
        print(f"✅ Success! Found {len(channels)} channels.")

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="CustomEPG-v2026">\n'
        
        # Process Channels
        for ch in channels[:100]:
            cid = str(ch.get("channel_id"))
            name = ch.get("channel_name", "Unknown").replace("&", "&amp;")
            xml += f'  <channel id="{cid}">\n    <display-name>{name}</display-name>\n  </channel>\n'

        # Fetch Programs
        for ch in channels[:100]:
            cid = ch.get("channel_id")
            params = {"offset": 0, "channel_id": cid, "langId": 6}
            
            try:
                # Add a retry logic for EPG
                epg_resp = session.get(EPG_API, params=params, timeout=10)
                if epg_resp.status_code == 200:
                    data = epg_resp.json().get("epg", [])
                    for p in data:
                        start = datetime.datetime.fromtimestamp(p['startEpoch']/1000).strftime('%Y%m%d%H%M%S +0530')
                        stop = datetime.datetime.fromtimestamp(p['endEpoch']/1000).strftime('%Y%m%d%H%M%S +0530')
                        title = p.get("showname", "No Title").replace("&", "&amp;")
                        
                        xml += f'  <programme start="{start}" stop="{stop}" channel="{cid}">\n'
                        xml += f'    <title>{title}</title>\n  </programme>\n'
                time.sleep(0.3) # Avoid triggering the 450 block during guide fetching
            except:
                continue

        xml += '</tv>'
        
        # Save compressed
        with gzip.open("epg.xml.gz", "wb") as f:
            f.write(xml.encode("utf-8"))
        print("🚀 File 'epg.xml.gz' created successfully.")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    generate_epg()
