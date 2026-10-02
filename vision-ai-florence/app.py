import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Florence2ForConditionalGeneration

model_id = "florence-community/Florence-2-base"

# The test images live in vision-ai/images, next to this project folder.
images_dir = Path(__file__).resolve().parent.parent / "images"

# Same three tasks the Gemini app offers, so the outputs can be compared.
tasks = {
    "<MORE_DETAILED_CAPTION>": "Detailed caption",
    "<OCR>": "Read text (OCR)",
    "<OD>": "List objects",
}

print("Loading the image processor...")
processor = AutoProcessor.from_pretrained(model_id)

print("Loading the AI model. The first run downloads its files...")
model = Florence2ForConditionalGeneration.from_pretrained(
    model_id,
    dtype=torch.float32,
).to("cpu")
model.eval()

print("Florence-2 is ready!")


def run_task(image, task_prompt):
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
    )[task_prompt]

    # Object detection returns boxes too; keep just the labels for comparison.
    if task_prompt == "<OD>":
        return "\n".join(result["labels"])
    return result.strip()


image_paths = sorted(
    p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
)

for path in image_paths:
    image = Image.open(path).convert("RGB")
    print(f"\n{'=' * 60}\n{path.name}\n{'=' * 60}")

    for task_prompt, label in tasks.items():
        start = time.perf_counter()
        output = run_task(image, task_prompt)
        seconds = time.perf_counter() - start

        print(f"\n--- {label} ({seconds:.1f}s) ---")
        print(output or "(nothing found)")
