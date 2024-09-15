
import os
import time
import warnings
from uuid import uuid4
from typing import Optional
import modal
import requests


GPU_TYPE = os.environ.get("GPU_TYPE", "a100-80gb")
GPU_COUNT = os.environ.get("GPU_COUNT", 1)

GPU_CONFIG = f"{GPU_TYPE}:{GPU_COUNT}"

SGL_LOG_LEVEL = "error"  # try "debug" or "info" if you have issues

MINUTES = 60  # seconds


MODEL_PATH = "Qwen/Qwen2-VL-7B-Instruct"

# We download it from the Hugging Face Hub using the Python function below.

def download_model_to_image():
    import transformers
    from huggingface_hub import snapshot_download
    
    snapshot_download(
        MODEL_PATH,
        ignore_patterns=["*.pt", "*.bin"],
    )

    # otherwise, this happens on first inference
    transformers.utils.move_cache()


# Modal runs Python functions on containers in the cloud.
# The environment those functions run in is defined by the container's `Image`.
# The block of code below defines our example's `Image`.

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
        "accelerate>=0.26.0",
        "huggingface_hub",
        "numpy<2",
        "qwen_vl_utils"
    )
    .run_function(  # download the model by running a Python function
        download_model_to_image
    )
)

import numpy as np
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info

# Define the application class
app = modal.App("hackmit")

@app.cls(
    gpu=GPU_CONFIG,
    timeout=20 * MINUTES,
    container_idle_timeout=20 * MINUTES,
    allow_concurrent_inputs=100,
    image=vlm_image,  # Update if needed based on new requirements
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
        # Perform any necessary initialization here
        print("Video processing runtime initialized.")

    @modal.web_endpoint(method="POST", docs=True)
    def generate(self, request: dict):
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
                    },
                    {"type": "text", "text": "Describe this image."},
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