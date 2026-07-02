from elevenlabs.client import ElevenLabs

# Initialize the client
client = ElevenLabs(api_key="sk_777017a84b08e0e9828cf8219a86bfd43d37007ff8882042")

try:
    # Use convert() instead of generate()
    audio = client.text_to_speech.convert(
        text="Hello, this is a test.",
        voice_id="SAz9YHcvj6GT2YYXdXww", # Use the specific voice ID string
        model_id="eleven_flash_v2_5"
    )
    
    # Save or play the audio
    # Note: 'audio' here is a generator, so you'll need to iterate to save it
    with open("output.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)
            
    print("Success: Audio generated and saved to output.mp3!")
except Exception as e:
    print(f"Failed: {e}")