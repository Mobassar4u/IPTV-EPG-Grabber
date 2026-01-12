import requests
import gzip
import datetime
import time

# NEW 2026 API ENDPOINT
CHANNELS_API = "https://jiotv.data.cdn.jio.com/apis/v3.0/getMobileChannelList/get/?langId=6&os=android&devicetype=phone"
EPG_API = "http://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get"

# These headers are the most common bypass for 450 errors
HEADERS = {
    "User-Agent": "JioTV/7.0.9 (Linux; Android 13)",
    "os": "android",
    "devicetype": "phone",
    "app-name": "RJIL_JioTV",
    "x-api-key": "no-key",  # Placeholder required by some v3 servers
    "Accept": "application/json",
    "Connection": "keep-alive"
}

# --- PROXY CONFIGURATION ---
# If you are on GitHub Actions, you MUST use an Indian Proxy.
# You can find free Indian proxies online or use a service like ScraperAPI.
PROXIES = {
    # "http": "http://username:password@indian-proxy-ip:port",
    # "https": "http://username:password@indian-proxy-ip:port"
}

def generate_epg():
    session = requests.Session()
    session.headers.update(HEADERS)
    if PROXIES:
        session.proxies.update(PROXIES)

    try:
        print("Requesting Channel List...")
        response = session.get(CHANNELS_API, timeout=20)
        
        if response.status_code == 450:
            print("❌ Still Blocked (Error 450). Your IP is likely not Indian or is flagged.")
            return

        channels = response.json().get('result', [])
        print(f"✅ Found {len(channels)} channels.")

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="CustomEPG-v2026">\n'
        
        # Limit to 30 channels for a test run
        for ch in channels[:30]:
            cid = str(ch.get("channel_id"))
            name = ch.get("channel_name", "Unknown").replace("&", "&amp;")
            xml += f'  <channel id="{cid}">\n    <display-name>{name}</display-name>\n  </channel>\n'

            # Fetch Guide
            params = {"offset": 0, "channel_id": cid, "langId": 6}
            try:
                g_resp = session.get(EPG_API, params=params, timeout=10)
                if g_resp.status_code == 200:
                    for p in g_resp.json().get("epg", []):
                        start = datetime.datetime.fromtimestamp(p['startEpoch']/1000).strftime('%Y%m%d%H%M%S +0530')
                        stop = datetime.datetime.fromtimestamp(p['endEpoch']/1000).strftime('%Y%m%d%H%M%S +0530')
                        title = p.get("showname", "No Title").replace("&", "&amp;")
                        xml += f'  <programme start="{start}" stop="{stop}" channel="{cid}">\n    <title>{title}</title>\n  </programme>\n'
                time.sleep(0.5) # Human-like delay
            except:
                continue

        xml += '</tv>'
        with gzip.open("epg.xml.gz", "wb") as f:
            f.write(xml.encode("utf-8"))
        print("🚀 Successfully created epg.xml.gz")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_epg()
