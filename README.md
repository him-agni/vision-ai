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

## Hybrid: local + cloud together

[`vision-ai-hybrid/`](vision-ai-hybrid/) uses both kinds of model in one flow, so you don't have to pick one. The local model (Gemma 3 via Ollama) reads the file first and keeps private data on your computer. Gemini is only used when the question needs it.

```
PDF or image + question
  1. Local read     PDF text is pulled out directly; scanned pages are read by Gemma 3
  2. Local scan     One Gemma 3 call reads the whole file and the question:
                    - summarises it and flags private info (patterns also catch
                      phone, email, SSN, date of birth, account and ID numbers)
                    - picks "local" (answer is in the file: find, summarise, describe)
                      or "cloud" (outside knowledge, reasoning, advice)
                    Questions that ask to explain, suggest, advise, compare, plan
                    or budget always go to the cloud, whatever Gemma 3 picks
  3. Answer         local                  -> Gemma 3 answers
                    cloud, nothing private -> whole file goes to Gemini
                    cloud, private         -> asks first, then sends only redacted text
                    Gemini fails / no key  -> Gemma 3 answers
```

Full flow diagram: [`vision-ai-hybrid/FLOW.md`](vision-ai-hybrid/FLOW.md). Test results: [`vision-ai-hybrid/test-results/results.md`](vision-ai-hybrid/test-results/results.md).

Requires Python 3.10+, [Ollama](https://ollama.com) and optionally a Gemini API key.

```powershell
ollama pull gemma3:4b
cd vision-ai-hybrid
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then paste your key into GEMINI_API_KEY
```

Put your PDFs in `vision-ai/files/` (git-ignored, so private documents are never committed), then pass the file path and your question:

```powershell
python hybrid.py ..\files\my-doc.pdf "What is the due date and amount?"
python hybrid.py ..\images\image_3.jpg "Who wrote this book?"
python hybrid.py ..\files\my-doc.pdf "Summarise it" --route cloud   # force a route
python hybrid.py ..\files\big.pdf "Summarise it" --pages 25         # read more pages (default 10)
```

## Project structure

```
vision-ai/
├── images/                  test images used by both models
├── files/                   your test PDFs (git-ignored)
├── vision-ai-next/          Gemini via API
│   └── app/
│       ├── page.tsx               upload page with task picker
│       └── api/describe/route.ts  sends the image + prompt to Gemini
├── vision-ai-next-report/   Gemini findings and screenshots
├── vision-ai-florence/      Florence-2, running locally
│   ├── app.py                     runs all tasks on all images
│   └── results.txt                Florence-2 output
└── vision-ai-hybrid/        Gemma 3 (local) + Gemini (cloud) together
    ├── hybrid.py                  reads a PDF or image, routes the question
    ├── FLOW.md                    flow diagram
    └── test-results/              test outputs and screenshots
```
