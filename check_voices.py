import os, requests
from dotenv import load_dotenv
load_dotenv()

headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
response = requests.get("https://api.elevenlabs.io/v2/voices", headers=headers)
data = response.json()

for v in data["voices"]:
    print(v["voice_id"], "-", v["name"], "-", v.get("category"), "-", v.get("available_for_tiers"))