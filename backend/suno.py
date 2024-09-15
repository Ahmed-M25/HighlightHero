import requests
import json
import time

API_TOKEN = 'uvbfboZucXoFZ0jSgldPeWw5ATROWhba'  
HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://suno.com',
    'Referer': 'https://suno.com/',
    'User-Agent': 'Mozilla/5.0 (compatible)'
}

def generate_instrumental_song():
    generate_endpoint = 'https://studio-api.suno.ai/api/generate/v2/'
    data = {
        "prompt": "",
        "gpt_description_prompt": "an instrumental song that's hype for a highlight reel", 
        "tags": "instrumental, upbeat", 
        "mv": "chirp-v3-5"  
    }

    response = requests.post(generate_endpoint, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        print("Generation request submitted successfully.")
        print("Response:", json.dumps(result, indent=2))
        clip_id = result.get('clips')[0]['id']  # Get the first clip ID from the response
        return clip_id
    else:
        print(f"Failed to submit generation request. Status code: {response.status_code}")
        print("Response:", response.text)
        return None

def poll_clip(clip_id, max_attempts=30, interval=10):
    clips_endpoint = 'https://studio-api.suno.ai/api/external/clips/'
    params = {
        'ids': clip_id
    }
    attempts = 0
    
    print("Waiting for the clip to be processed...")
    time.sleep(20)

    while attempts < max_attempts:
        response = requests.get(clips_endpoint, headers=HEADERS, params=params)
        if response.status_code == 200:
            result = response.json()
            clips = result
            if clips:
                clip = clips[0]
                status = clip.get('status')
                print(f"Clip ID: {clip_id} Status: {status}")
                if status == 'complete':
                    print("Clip has been generated.")
                    print("Clip Details:", json.dumps(clip, indent=2))
                    return clip
                elif status == 'error':
                    print("An error occurred during clip generation.")
                    print("Error Details:", json.dumps(clip, indent=2))
                    return None
                else:
                    print(f"Clip is not yet complete. Status: {status}. Waiting for {interval} seconds.")
                    time.sleep(interval)
                    attempts += 1
            else:
                print("No clips found in the response.")
                break
        elif response.status_code == 404:
            print("Clip not found yet. Retrying...")
            time.sleep(interval)
            attempts += 1
        else:
            print(f"Failed to retrieve clip details. Status code: {response.status_code}")
            print("Response:", response.text)
            break
    print("Maximum polling attempts reached.")
    return None

def download_content(clip):
    audio_url = clip.get('audio_url')
    video_url = clip.get('video_url')
    clip_id = clip.get('id')
    print(f"Clip ID: {clip_id}")
    print(f"Audio URL: {audio_url}")
    print(f"Video URL: {video_url}")
    # Download the audio content
    if audio_url:
        audio_response = requests.get(audio_url)
        if audio_response.status_code == 200:
            with open(f"{clip_id}.mp3", 'wb') as f:
                f.write(audio_response.content)
            print(f"Audio content saved as {clip_id}.mp3")
        else:
            print(f"Failed to download audio content for Clip ID: {clip_id}")
    else:
        print("No audio URL available.")

def main():
    clip_id = generate_instrumental_song()
    if clip_id:
        clip = poll_clip(clip_id)
        if clip:
            download_content(clip)
        else:
            print("Failed to retrieve generated clip.")
    else:
        print("Generation failed.")

if __name__ == "__main__":
    main()
