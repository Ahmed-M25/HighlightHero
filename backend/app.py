# Run python app.py from inside the backend directory

import asyncio
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
    (chunks,num_chunks) = split_video_into_chunks(file_path)
    chunk_narrations = []
    for chunk in chunks:
        response = requests.post(
            "https://ahmed-m25--hackmit-model-generate.modal.run",
            files ={
                "file": open(chunk,'rb')
            }
        )
        chunk_narrations.append(response.json().get('answer',None)[0])
        if chunk_narrations is None:
            return jsonify({'error': 'Failed to generate narration'}), 500
        
    print(f"Narration text generation complete! {chunk_narrations}")

    for (index,narration) in enumerate(chunk_narrations):
        if is_interesting(narration):
            generate_narration_sound(narration, index)
        else:
            generate_narration_sound(narration, index)


    print("Narration sound generation complete!")

    final_video_path = generate_final_video(VIDEO_PATH, num_chunks)
    print("Final video generation complete!")

    return jsonify({'file_path': final_video_path})

from openai import OpenAI
client = OpenAI()

def is_interesting(narration):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Return True or False, indicating whether this narration indicates anything of interest going on, with respect to sports. Return True only if a significant event has happened: {narration}"
            }
        ]
    )
    msg = completion.choices[0].message.content
    print(msg)
    if "true" in msg.lower():
        return True
    else:
        return False


def generate_narration_sound(narration_text, index):

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
    narration_path = f"./chunks/narration_{index}.mp3"
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
            '-y',
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

def split_video_into_chunks(video_path, chunk_duration=8):
    res = []
    # Load the video
    video = VideoFileClip(video_path)
    
    # Get the total duration of the video
    total_duration = video.duration
    
    # Calculate the number of chunks
    num_chunks = int(total_duration // chunk_duration)
    # Split the video into chunks
    for i in range(num_chunks):
        start_time = i * chunk_duration
        end_time = min((i + 1) * chunk_duration, total_duration)
        # Create a subclip for each chunk
        chunk = video.subclip(start_time, end_time)
        
        # Write the chunk to a file
        output_filename = f"./chunks/chunk_{i}.mp4"
        chunk.write_videofile(output_filename, codec="libx264")
        res.append(output_filename)
        chunk.close()
    
    return (res, num_chunks)


def generate_final_video(video_path, num_chunks):

    # Load the BackGround Music
    background_audio_path = './uploads/background.mp3'
    print(f"Loading background audio from: {background_audio_path}")
    background_audio = AudioFileClip(background_audio_path)
    print(f"Background audio duration: {background_audio.duration}s")

    background_audio = background_audio.volumex(0.3)

    for i in range(num_chunks):
        video_path = f"./chunks/chunk_{i}.mp4"

        narration_path = f"./chunks/narration_{i}.mp3"
        if not os.path.exists(narration_path):
            pass
        # Load the audio file
        narration_audio = AudioFileClip(narration_path, fps=44100)

        # Load the video file
        print(f"Loading video from: {video_path}")
        video_clip = VideoFileClip(video_path)
        
        # Check for fps in the video
        if 'video_fps' not in video_clip.reader.infos:
            video_clip.reader.fps = 24
            print("FPS set to default 24.")
        else:
            print(f"Video FPS: {video_clip.reader.fps}")
        
        # Match audio duration to video duration
        narration_audio = narration_audio.fx(afx.audio_loop, duration=video_clip.duration)
        background_audio = background_audio.copy().fx(afx.audio_loop, duration=video_clip.duration)

        mixed_audio = CompositeAudioClip([background_audio, narration_audio])
        
        # Set the audio of the video clip as the narration audio
        print("Setting audio to video...")
        final_video = video_clip.set_audio(mixed_audio)
        
        # Define the output file path
        output_path = video_path.replace(".mp4", "_new.mp4").replace("chunks","final")
        
        # Write the result to a file
        print(f"Writing final video to: {output_path}")
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        # Close clips to free resources
        narration_audio.close()
        video_clip.close()
        final_video.close()

    generate_final_video_inner()

def generate_final_video_inner():
    video_dir = './final/'
    os.listdir(video_dir)
    # List of video files
    video_files = ["./final/"+f for f in os.listdir(video_dir) if f.endswith('.mp4')]
    print(video_files)

    # Create a temporary text file listing all video files
    with open('filelist.txt', 'w') as file:
        for video in video_files:
            file.write(f"file '{video}'\n")


    # FFmpeg command to concatenate videos
    command = 'ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy ../Frontend/output.mp4'
    subprocess.run(command, shell=True)

    # Remove the temporary file
    os.remove('filelist.txt')

    cleanup()

import shutil
def cleanup():
    shutil.rmtree('./chunks')
    shutil.rmtree('./final')
    
    os.makedirs('./chunks')
    os.makedirs('./final')

if __name__ == '__main__':
    app.run(debug=True)