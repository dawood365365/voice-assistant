import os
from dotenv import load_dotenv

load_dotenv()

class GroqKeyManager:
    def __init__(self):
        # Load all available keys
        self.keys = []
        i = 1
        while True:
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if not key:
                break
            self.keys.append(key)
            i += 1

        if not self.keys:
            raise ValueError("No GROQ API keys found in .env")

        self.current_index = 0
        print(f"✅ Loaded {len(self.keys)} Groq API keys")

    @property
    def current_key(self) -> str:
        return self.keys[self.current_index]

    def switch_key(self):
        """Switch to the next available key."""
        next_index = (self.current_index + 1) % len(self.keys)

        if next_index == self.current_index:
            print("❌ All Groq API keys exhausted!")
            return False

        self.current_index = next_index
        print(f"🔄 Switched to Groq key #{self.current_index + 1}")
        return True

# Global instance
key_manager = GroqKeyManager()