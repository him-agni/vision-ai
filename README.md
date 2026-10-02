# Vision AI: API model vs local model

The aim of this project is simple: **compare a vision model called through an API with one running locally**, using the same images and the same tasks, and see how their outputs and speed differ.

| | API model | Local model |
|---|---|---|
| **Model** | Google Gemini (`gemini-2.5-flash-lite`) | Microsoft Florence-2 (`Florence-2-base`) |
| **Runs on** | Google's servers | Your own computer (CPU) |
| **Needs** | API key + internet | One-time model download |
| **Cost** | Free tier with a daily limit, then paid | Free |
| **Input** | Any text prompt | Fixed task codes |
| **Project** | [`vision-ai-next/`](vision-ai-next/) (Next.js web app) | [`vision-ai-florence/`](vision-ai-florence/) (Python script) |

## How the comparison works

Both models get the same four images from [`images/`](images/), each chosen to test something different:

| Image | What it tests |
|---|---|
| `image_1.jpg`: group of people at night | Busy scene, many people, low light |
| `image_2.jpg`: fishing boat and lighthouse | Simple scene, small objects |
| `image_3.jpg`: "Where the Wild Things Are" poster | Stylized, hand-drawn text |
| `image_4.png`: kids' learning charts | Dense small text and many objects |

Florence-2 only accepts fixed task codes, so Gemini is given prompts written to ask for the same kind of output:

| Task | Florence-2 | Gemini prompt |
|---|---|---|
| Detailed caption | `<MORE_DETAILED_CAPTION>` | "Describe this image in detail in one paragraph. Plain text only, no markdown." |
| Read text (OCR) | `<OCR>` | "Transcribe all the text in this image. Output only the text, nothing else." |
| List objects | `<OD>` | "List the objects in this image. Output only short object names, one per line." |

## Results

- **Gemini:** [`vision-ai-next-report/findings.md`](vision-ai-next-report/findings.md), with screenshots
- **Florence-2:** [`vision-ai-florence/results.txt`](vision-ai-florence/results.txt)

## Run it yourself

### Gemini (Next.js app)

Requires Node.js 18+ and a free API key from [Google AI Studio](https://aistudio.google.com/apikey).

```powershell
cd vision-ai-next
npm install
copy .env.example .env.local   # then paste your key into GEMINI_API_KEY
npm run dev
```

Open http://localhost:3000, choose an image, pick a task and click **Run**.

### Florence-2 (Python script)

Requires Python 3.10+. The first run downloads the model (about 460 MB).

```powershell
cd vision-ai-florence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py | Tee-Object results.txt
```

The script loads the model once, then runs all three tasks on every image in `images/` and prints each result with the time it took.

## Project structure

```
vision-ai/
├── images/                  test images used by both models
├── vision-ai-next/          Gemini via API
│   └── app/
│       ├── page.tsx               upload page with task picker
│       └── api/describe/route.ts  sends the image + prompt to Gemini
├── vision-ai-next-report/   Gemini findings and screenshots
└── vision-ai-florence/      Florence-2, running locally
    ├── app.py                     runs all tasks on all images
    └── results.txt                Florence-2 output
```
