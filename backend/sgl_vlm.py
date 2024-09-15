
import os
import warnings
import modal
import json
import numpy as np
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

GPU_TYPE = os.environ.get("GPU_TYPE", "a100-80gb")
GPU_COUNT = os.environ.get("GPU_COUNT", 1)
GPU_CONFIG = f"{GPU_TYPE}:{GPU_COUNT}"
SGL_LOG_LEVEL = "error" 
MINUTES = 60 
MODEL_PATH = "Qwen/Qwen2-VL-7B-Instruct"


def download_model_to_image():
    import transformers
    from huggingface_hub import snapshot_download
    
    snapshot_download(
        MODEL_PATH,
        ignore_patterns=["*.pt", "*.bin"],
    )
    transformers.utils.move_cache()


# local_assets = modal.Mount.from_local_dir(local_path="./resources",remote_path="/resources",recursive=True)
key = modal.Secret.from_name("ghp_")
vlm_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_private_repos(
        "github.com/huggingface/transformers",
        git_user="xpbowler",
        secrets=[key],
    )
    .pip_install( 
        "torch",
        "torchvision",
        "torchaudio",
        "av",
        "accelerate>=0.26.0",
        "huggingface_hub",
        "numpy<2",
        "qwen_vl_utils",
        "moviepy"
    )
    .run_function(  # download the model by running a Python function
        download_model_to_image
    )
)

from moviepy.editor import VideoFileClip
from fastapi import FastAPI, File, UploadFile, Form
app = modal.App("hackmit")
@app.cls(
    gpu=GPU_CONFIG,
    timeout=20 * MINUTES,
    container_idle_timeout=20 * MINUTES,
    allow_concurrent_inputs=100,
    image=vlm_image,
    # mounts=[local_assets],
)
class Model:
    def __init__(self):
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen2-VL-7B-Instruct", torch_dtype="auto", device_map="auto"
        ).to("cuda")
        self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

    @modal.enter()
    def start_runtime(self):
        """Initializes video processing capabilities."""
        print("Video processing runtime initialized.")

    @modal.web_endpoint(method="POST", docs=True)
    async def generate(self, file: UploadFile = File(...)):
        # Read the video file
        print(file.filename)
        # Folder where uploaded files will be stored
        UPLOAD_DIRECTORY = "/uploaded_files"
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

        file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"

        with open(file_location, "wb") as data:
            while content := await file.read(1024):  # Read chunks of 1024 bytes
                data.write(content)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "video",
                        "video": f"file:///uploaded_files/{file.filename}",
                        "fps": 1.0,
                        "max_pixels": 512 * 512,
                    },
                    {"type": "text", "text": "Narrate this video as if you were a sports commentator."},
                ],
            }
        ]

        # Preparation for inference
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return {"answer": output_text}

    def read_video_pyav(self, container, indices):
        frames = []
        container.seek(0)
        for frame in container.decode(video=0):
            frames.append(frame)
            if len(frames) >= indices[-1] + 1:
                break
        return np.stack([x.to_ndarray(format="rgb24") for x in frames[indices]])

    @modal.exit()
    def shutdown_runtime(self):
        print("Shutting down video processing runtime.")


warnings.filterwarnings(  # filter warning from the terminal image library
    "ignore",
    message="It seems this process is not running within a terminal. Hence, some features will behave differently or be disabled.",
    category=UserWarning,
)
