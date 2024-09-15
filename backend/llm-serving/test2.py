import requests

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/NYC9WEgkq1u4jiqBseQ9"

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": "sk_65946c9858aa90317f94dede6e9973e819e49517ed4a2039"
}

data = {
  "text": "Born and raised in the charming south, I can add a touch of sweet southern hospitality to your audiobooks and podcasts",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

response = requests.post(url, json=data, headers=headers)
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)




# from elevenlabs import VoiceSettings
# from elevenlabs.client import ElevenLabs

# client = ElevenLabs(
#     api_key="sk_65946c9858aa90317f94dede6e9973e819e49517ed4a2039",
# )
# client.text_to_speech.convert(
#     voice_id="pMsXgVXv3BLzUgSXRplE",
#     optimize_streaming_latency="0",
#     output_format="mp3_22050_32",
#     text="It sure does, Jackie… My mama always said: “In Carolina, the air's so thick you can wear it!”",
#     voice_settings=VoiceSettings(
#         stability=0.1,
#         similarity_boost=0.3,
#         style=0.2,
#     ),
# )