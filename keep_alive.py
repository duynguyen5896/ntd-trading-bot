import time
import requests

# Replace with your actual Render URL
URL = "https://ntd-trading-bot.onrender.com/health"

def keep_alive():
    print(f"🚀 Starting Keep-Alive for {URL}")
    while True:
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                print(f"✅ Ping success: {response.status_code}")
            else:
                print(f"⚠️ Ping returned: {response.status_code}")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
        
        # Ping every 5 minutes (300 seconds)
        # Render sleeps after 15 mins, so 5-10 mins is safe
        time.sleep(300)

if __name__ == "__main__":
    keep_alive()
