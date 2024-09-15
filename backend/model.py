import av
import numpy as np
import torch
from transformers import LlavaNextVideoProcessor, LlavaNextVideoForConditionalGeneration, hf_hub_download

# Load the model and processor
model_id = "llava-hf/LLaVA-NeXT-Video-7B-hf"
model = LlavaNextVideoForConditionalGeneration.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda")
processor = LlavaNextVideoProcessor.from_pretrained(model_id)

# Read video
def read_video_pyav(container, indices):
    frames = []
    container.seek(0)
    for frame in container.decode(video=0):
        frames.append(frame)
        if len(frames) >= indices[-1] + 1:
            break
    return np.stack([x.to_ndarray(format="rgb24") for x in frames[indices]])

video_path = hf_hub_download(repo_id="raushan-testing-hf/videos-test", filename="sample_demo_1.mp4", repo_type="dataset")
container = av.open(video_path)
total_frames = container.streams.video[0].frames
indices = np.linspace(0, total_frames - 1, 32, dtype=int)  # Sampling 32 frames uniformly
video_frames = read_video_pyav(container, indices)

# Prepare the prompt
conversation = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Why is this video funny?"},
        {"type": "video", "video": video_frames},
    ],
}
prompt = processor.apply_chat_template([conversation], add_generation_prompt=True)

# Process inputs
inputs = processor(text=prompt, videos=video_frames, padding=True, return_tensors="pt").to("cuda")

# Generate response
outputs = model.generate(**inputs, max_new_tokens=100)
result = processor.decode(outputs[0], skip_special_tokens=True)

print(result)
