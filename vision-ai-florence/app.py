import torch
from transformers import AutoProcessor, Florence2ForConditionalGeneration

model_id = "florence-community/Florence-2-base"

print("Loading the image processor...")
processor = AutoProcessor.from_pretrained(model_id)

print("Loading the AI model. The first run downloads its files...")
model = Florence2ForConditionalGeneration.from_pretrained(
    model_id,
    dtype=torch.float32,
).to("cpu")
model.eval()

print("Florence-2 is ready!")

import requests
from io import BytesIO
from PIL import Image

print("Downloading the example image...")

url = (
    "https://huggingface.co/datasets/huggingface/"
    "documentation-images/resolve/main/transformers/tasks/car.jpg"
)
response = requests.get(url, timeout=60)
response.raise_for_status()

image = Image.open(BytesIO(response.content)).convert("RGB")
image.save("example.jpg")

print("Writing a description of the image...")

task_prompt = "<MORE_DETAILED_CAPTION>"

inputs = processor(
    text=task_prompt,
    images=image,
    return_tensors="pt",
).to("cpu")

with torch.inference_mode():
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=1024,
        num_beams=3,
    )

generated_text = processor.batch_decode(
    generated_ids,
    skip_special_tokens=False,
)[0]

result = processor.post_process_generation(
    generated_text,
    task=task_prompt,
    image_size=image.size,
)

print("\nImage description:")
print(result[task_prompt])

