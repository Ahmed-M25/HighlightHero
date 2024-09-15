# Run python app.py from inside the backend directory

import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Hyperparameters
PROMPT = "Narrate this video as if you were a sports commentator."
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"
VOICE_ID = "NYC9WEgkq1u4jiqBseQ9"
CHUNK_SIZE = 1024
ELEVENLABS_API_KEY = "sk_65946c9858aa90317f94dede6e9973e819e49517ed4a2039"
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"
VIDEO_PATH = "./uploads/video.mp4"




if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file in request'}), 400

    file = request.files['video']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], "video.mp4")
        file.save(file_path)
        return process_video(file_path)
    else:
        return jsonify({'error': 'File type not allowed'}), 400

def process_video(file_path): # file_path is relative path
    print("Starting video processing...")
    response = requests.post(
        "https://xpbowler--hackmit-model-generate.modal.run",
        files ={
            "file": open(file_path,'rb')
        }
    )

    narration_text = response.json().get('answer',None)
    if narration_text is None:
        return jsonify({'error': 'Failed to generate narration'}), 500
    print("Narration text generation complete!")

    narration_path = generate_narration_sound(narration_text[0])
    print("Narration sound generation complete!")

    final_video_path = generate_final_video(narration_path, VIDEO_PATH)
    print("Final video generation complete!")

    return jsonify({'file_path': final_video_path})

def generate_narration_sound(narration_text):
    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": narration_text,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(ELEVENLABS_BASE_URL+VOICE_ID, json=data, headers=headers)
    narration_path = f"{UPLOAD_FOLDER}narration.mp3"
    with open(narration_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    
    return narration_path

import subprocess

def preprocess_video(input_path, output_path):
    try:
        command = [
            'ffmpeg',
            '-i', input_path,
            '-c', 'copy',
            '-video_track_timescale', '24',  # Set this to your desired default FPS
            output_path
        ]
        subprocess.run(command, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to preprocess video: {e}")
        return None

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import moviepy.audio.fx.all as afx

def generate_final_video(narration_path, video_path):
    new_video_path = "./uploads/new_video.mp4"
    preprocess_video(video_path, new_video_path)  # Ensure this function logs its output

    # Load the audio file
    print(f"Loading narration audio from: {narration_path}")
    narration_audio = AudioFileClip(narration_path, fps=44100)
    print(f"Narration audio duration: {narration_audio.duration}s")

    # Load the BackGround Music
    background_audio_path = './uploads/background.mp3'
    print(f"Loading background audio from: {background_audio_path}")
    background_audio = AudioFileClip(background_audio_path)
    print(f"Background audio duration: {background_audio.duration}s")

    background_audio = background_audio.volumex(0.3)


    # Load the video file
    print(f"Loading video from: {new_video_path}")
    video_clip = VideoFileClip(new_video_path)
    
    # Check for fps in the video
    if 'video_fps' not in video_clip.reader.infos:
        video_clip.reader.fps = 24
        print("FPS set to default 24.")
    else:
        print(f"Video FPS: {video_clip.reader.fps}")
    
    # Match audio duration to video duration
    narration_audio = narration_audio.fx(afx.audio_loop, duration=video_clip.duration)
    background_audio = background_audio.fx(afx.audio_loop, duration=video_clip.duration)

    mixed_audio = CompositeAudioClip([background_audio, narration_audio])
    
    # Set the audio of the video clip as the narration audio
    print("Setting audio to video...")
    final_video = video_clip.set_audio(mixed_audio)
    
    # Define the output file path
    output_path = new_video_path.replace('.mp4', '_with_audio.mp4')
    
    # Write the result to a file
    print(f"Writing final video to: {output_path}")
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    
    # Close clips to free resources
    narration_audio.close()
    video_clip.close()
    final_video.close()
    
    # Return the path of the final video
    return output_path

if __name__ == '__main__':
    app.run(debug=True)