import requests
import time
from datetime import datetime
from telegram import Bot

# === CONFIGURATION ===

BOT_TOKEN = "8255221201:AAHRLChPb6JS0yvUWdT_GAjkSDGDL_6p8Rk"  # Put your token here
CHAT_ID = "2122441306"      # Put your chat ID here
MINER_URL = "http://192.168.0.113/api/system/info"
INTERVAL_MINUTES = 15  # how often to send alerts
HASHRATE_ALERT = 3000  # in GH/s (set threshold)
TEMP_ALERT = 70        # in °C (set threshold)

bot = Bot(token=BOT_TOKEN)

def get_miner_stats():
    try:
        response = requests.get(MINER_URL, timeout=5)
        data = response.json()

        return {
            "hashrate": data.get("hashRate"),
            "best_share": data.get("bestDiff"),
            "temp": data.get("temp"),
            "vrTemp": data.get("vrTemp"),
            "power": data.get("power"),
            "voltage": data.get("voltage"),
            "freq": data.get("frequency"),
            "shares_accepted": data.get("sharesAccepted"),
            "shares_rejected": data.get("sharesRejected"),
            "uptime": data.get("uptimeSeconds"),
            "stratum": data.get("stratumURL"),
            "version": data.get("version")
        }

    except Exception as e:
        return {"error": str(e)}

def send_telegram_message(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("⚠️ Telegram error:", e)

def main():
    while True:
        stats = get_miner_stats()

        if "error" in stats:
            message = f"⚠️ Error fetching miner data:\n{stats['error']}"
        else:
            message = (
                f"⛏️ *Bitaxe SupraHex Stats* ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
                f"🏷️ Version: {stats['version']}\n"
                f"🌐 Pool: {stats['stratum']}\n"
                f"📊 Hashrate: {stats['hashrate']:.2f} GH/s\n"
                f"🔥 Temp: {stats['temp']}°C  (VR: {stats['vrTemp']}°C)\n"
                f"⚡ Power: {stats['power']:.1f} W @ {stats['voltage']} mV\n"
                f"🎯 Best Share: {stats['best_share']}\n"
                f"🧠 Freq: {stats['freq']} MHz\n"
                f"✅ Shares: {stats['shares_accepted']}  ❌ Rejected: {stats['shares_rejected']}\n"
                f"⏱️ Uptime: {stats['uptime']} sec"
            )

            # Alert conditions
            if stats["hashrate"] < HASHRATE_ALERT:
                message = "⚠️ *Low Hashrate Alert!* ⚠️\n" + message
            if stats["temp"] > TEMP_ALERT:
                message = "🔥 *High Temperature Alert!* 🔥\n" + message

        print(message)
        send_telegram_message(message)
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
