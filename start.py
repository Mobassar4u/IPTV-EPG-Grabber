# Updated Configuration
headers = {
    "User-Agent": "JioTV 7.0.5 (Android 10)", # Updated User-Agent
    "appkey": "NzNiMDhlYzQyNjJm",           # Required app key for 2026
    "devicetype": "phone",
    "os": "android",
    "versionCode": "300",                    # Latest version code
    "Accept": "application/json"
}

def getChannels():
    print("Fetching Channel List...")
    # Updated 2026 Endpoint
    reqUrl = "https://jiotv.data.cdn.jio.com/apis/v1.3/getMobileChannelList/get/?os=android&devicetype=phone&version=300"
    try:
        response = requests.get(reqUrl, headers=headers, timeout=15)
        if response.status_code == 200:
            apiData = response.json()
            channels = apiData.get("result", [])
            print(f"Success! Found {len(channels)} channels.")
            return channels
        else:
            print(f"Blocked: Status {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def getEpg(channelId, offset, langId):
    # Updated EPG Endpoint
    reqUrl = f"https://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get?channel_id={channelId}&offset={offset}&langId={langId}"
    try:
        response = requests.get(reqUrl, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("epg", [])
        return []
    except Exception:
        return []
