"""Ask a question about a PDF or an image, using a local model and a cloud model together.

The local model (Ollama) always reads the file first, on your own computer. It
looks for private details and decides whether the question needs the cloud
(Gemini). The file itself is only sent to the cloud when nothing private is found.
Otherwise you are asked first, and only a redacted text version is sent.

    python hybrid.py ../files/report.pdf "Summarise this document"
    python hybrid.py ../images/image_3.jpg "Who wrote this book and what is it about?"
"""

import argparse
import json
import mimetypes
import os
import re
import time
from pathlib import Path

import ollama
import pymupdf
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).resolve().parent / ".env")

LOCAL_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
CLOUD_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}

# Long documents are cut to this length before the local model sees them.
MAX_CHARS = 40_000
LOCAL_OPTIONS = {"temperature": 0, "num_ctx": 16384}

PRIVATE_TYPES = ["ID NUMBER", "PHONE", "ADDRESS", "BANK ACCOUNT", "HEALTH INSURANCE",
                 "EMAIL", "DATE OF BIRTH", "OTHER"]

# Patterns catch the obvious private details reliably, without relying on the model.
# Order matters: earlier patterns are replaced first, so later ones can't re-match them.
PATTERNS = [
    ("EMAIL", r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
    ("SSN", r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    ("DATE OF BIRTH", r"(?i)\b(?:dob|date of birth|birth ?date)\b\W{0,3}"
                      r"(?:\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|[a-z]+\.? \d{1,2},? \d{4}|\d{1,2} [a-z]+ \d{4})"),
    ("PHONE", r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)"),
    # 9-18 digits in a row, or card-style groups like 1234 5678 9012 3456.
    ("BANK ACCOUNT", r"(?<!\d)(?:\d{9,18}|\d{4}(?:[ -]\d{4}){2,3})(?!\d)"),
    # Capital letters mixed with digits, e.g. insurance member IDs, passport and licence numbers.
    ("ID NUMBER", r"\b(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{8,20}\b"),
]

READ_PAGE_PROMPT = "Transcribe all the text on this page. Output only the text, nothing else."

# One local call reads the whole file and does three jobs: summary, private details, route.
# The fields are filled in this order, so private details are found before the route is chosen.
SUMMARY_RULE = """- summary: 3-5 sentences on what this is and its main points. Leave out personal
  details: no names, numbers, addresses or account details."""

VISIBLE_TEXT_RULE = """- visible_text: all the text you can read in the image, or "" if none."""

PRIVATE_RULE = """- private_items: every piece of private information, copied exactly as it appears:
  ID numbers (passport, driver's licence, social security), phone numbers, home or
  mailing addresses, bank account or card numbers, health insurance numbers, emails,
  dates of birth. Use an empty list if there are none."""

ROUTE_RULE = """- route: which AI should answer the question below.
  "local" (a small model on this computer) if the answer is written in the file:
  finding a date, value, name or section, quoting or summarising it, describing
  what is visible, reading text, listing objects.
  "cloud" (a large model online) only if the question needs more than the file:
  outside knowledge (facts about places, books, products, laws, prices),
  explanations or advice, calculations across many values, or long careful writing.
- reason: one sentence explaining the route."""


def scan_prompt(question, text=None):
    if text is None:
        intro, rules = "Look at this image", [SUMMARY_RULE, VISIBLE_TEXT_RULE, PRIVATE_RULE, ROUTE_RULE]
    else:
        intro, rules = "Read this document", [SUMMARY_RULE, PRIVATE_RULE, ROUTE_RULE]
    prompt = f"{intro} and fill in the JSON fields.\n" + "\n".join(rules) + f"\n\nQuestion: {question}"
    if text is not None:
        prompt += f"\n\nDocument:\n{text}"
    return prompt


def scan_schema(with_visible_text):
    properties = {"summary": {"type": "string"}}
    if with_visible_text:
        properties["visible_text"] = {"type": "string"}
    properties["private_items"] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": PRIVATE_TYPES},
                "text": {"type": "string"},
            },
            "required": ["type", "text"],
        },
    }
    properties["route"] = {"type": "string", "enum": ["local", "cloud"]}
    properties["reason"] = {"type": "string"}
    return {"type": "object", "properties": properties, "required": list(properties)}


def ask_local(prompt, images=None, schema=None):
    message = {"role": "user", "content": prompt}
    if images:
        message["images"] = images
    response = ollama.chat(model=LOCAL_MODEL, messages=[message], format=schema, options=LOCAL_OPTIONS)
    text = response.message.content
    return json.loads(text) if schema else text.strip()


def ask_cloud(prompt, file_path=None):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    contents = [prompt]
    if file_path:
        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        contents.insert(0, types.Part.from_bytes(data=file_path.read_bytes(), mime_type=mime_type))
    # We never give Gemini tools, so turn off automatic function calling (and its warning).
    config = types.GenerateContentConfig(
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    result = client.models.generate_content(model=CLOUD_MODEL, contents=contents, config=config)
    return result.text.strip()


def read_pdf(path, max_pages):
    """Pull the text out of each page. Scanned pages with no text are read by the local model."""
    doc = pymupdf.open(path)
    pages = []
    for number, page in enumerate(doc, start=1):
        if number > max_pages:
            print(f"Stopped after {max_pages} of {doc.page_count} pages (change with --pages).")
            break
        text = page.get_text().strip()
        if len(text) >= 20:
            print(f"Page {number}: text layer ({len(text):,} chars)")
        else:
            png = page.get_pixmap(dpi=150).tobytes("png")
            text = ask_local(READ_PAGE_PROMPT, images=[png])
            print(f"Page {number}: scanned, read by {LOCAL_MODEL} ({len(text):,} chars)")
        pages.append(f"--- Page {number} ---\n{text}")

    text = "\n\n".join(pages)
    if len(text) > MAX_CHARS:
        print(f"Document is {len(text):,} chars, only the first {MAX_CHARS:,} are used.")
        text = text[:MAX_CHARS]
    return text


def redact(text, model_items):
    """Replace private details with tags like [PHONE].

    Returns the new text, what was redacted, and the model's flags that were not redacted (with why).
    """
    found, skipped = {}, []
    for item in model_items:
        value = item["text"].strip()
        if len(value) < 4 or value not in text:
            skipped.append((item, "not found word-for-word"))
            continue
        starts = [m.start() for m in re.finditer(re.escape(value), text)]
        if item["type"] == "DATE OF BIRTH":
            # The model sometimes flags any date, so only trust it right after a birth label.
            starts = [s for s in starts if re.search(r"(?i)\b(?:dob|birth|born)\b", text[max(0, s - 30):s])]
            if not starts:
                skipped.append((item, "no birth label next to it"))
                continue
        for s in reversed(starts):
            text = text[:s] + f"[{item['type']}]" + text[s + len(value):]
        found[item["type"]] = found.get(item["type"], 0) + len(starts)
    for kind, pattern in PATTERNS:
        text, count = re.subn(pattern, f"[{kind}]", text)
        if count:
            found[kind] = found.get(kind, 0) + count
    return text, found, skipped


def step(label, fn, *args, **kwargs):
    print(f"\n--- {label} ---")
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    print(f"({time.perf_counter() - start:.1f}s)")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path, help="a .pdf, .jpg, .jpeg, .png or .webp file")
    parser.add_argument("question")
    parser.add_argument("--route", choices=["auto", "local", "cloud"], default="auto",
                        help="override the route the local scan picks (default: auto)")
    parser.add_argument("--pages", type=int, default=10, help="how many PDF pages to read locally (default: 10)")
    parser.add_argument("--yes", action="store_true",
                        help="don't ask before sending redacted text of a private file to the cloud")
    args = parser.parse_args()

    kind = args.file.suffix.lower()
    if kind != ".pdf" and kind not in IMAGE_TYPES:
        parser.error(f"unsupported file type: {kind}")
    is_pdf = kind == ".pdf"

    print(f"File: {args.file.name}\nQuestion: {args.question}")
    print(f"Local model: {LOCAL_MODEL}   Cloud model: {CLOUD_MODEL}")

    # 1. Read the file, and 2. scan it, all locally.
    if is_pdf:
        text = step("1. Local read (no AI for text pages)", read_pdf, args.file, args.pages)
        scan = step(f"2. Local scan: summary, private info, route ({LOCAL_MODEL})", ask_local,
                    scan_prompt(args.question, text), schema=scan_schema(False))
    else:
        print("\n--- 1. Local read: skipped for images ---")
        scan = step(f"2. Local scan: summary, private info, route ({LOCAL_MODEL})", ask_local,
                    scan_prompt(args.question), images=[str(args.file)], schema=scan_schema(True))
        text = scan["visible_text"]
        print(f"Text in image: {text or '(none)'}")

    # Privacy is decided here in code, not by the route: patterns plus whatever the model flagged.
    redacted, found, skipped = redact(text, scan["private_items"])
    is_private = bool(found or scan["private_items"])
    print(f"Summary: {scan['summary']}")
    if is_private:
        flagged = ", ".join(f"{kind} x{count}" for kind, count in found.items()) or "none matched in text"
        print(f"Private info: YES. Redacted: {flagged}")
        for item, why in skipped:
            print(f"  {LOCAL_MODEL} also flagged {item['type']}: '{item['text']}' (not redacted: {why})")
    else:
        print("Private info: none found")

    if args.route == "auto":
        route = scan["route"]
        print(f"Route: {route} ({scan['reason']})")
    else:
        route = args.route
        print(f"Route: {route} (forced with --route)")

    # Anything typed in the question gets the same redaction before it can reach the cloud.
    cloud_question, _, _ = redact(args.question, scan["private_items"])
    if route == "cloud" and cloud_question != args.question:
        print(f"Question redacted for the cloud: {cloud_question}")

    # 3. Answer.
    answer, answered_by = None, None
    if route == "cloud":
        if not os.getenv("GEMINI_API_KEY"):
            print("\nNo GEMINI_API_KEY set, so answering locally instead.")
        elif not is_private:
            try:
                answer = step(f"3. Cloud answer ({CLOUD_MODEL}, whole file sent)",
                              ask_cloud, cloud_question, args.file)
                answered_by = f"{CLOUD_MODEL} (cloud, whole file)"
            except Exception as err:
                print(f"Cloud failed ({err}), answering locally instead.")
        else:
            if is_pdf:
                context = f"Document (private details replaced with tags like [PHONE]):\n{redacted}"
            else:
                summary, _, _ = redact(scan["summary"], scan["private_items"])
                context = (f"Description of an image: {summary}\n\n"
                           f"Text in the image (private details replaced with tags like [PHONE]):\n{redacted}")
            prompt = f"{context}\n\nAnswer this question using the information above: {cloud_question}"

            print("\nThe file has private info, so it will NOT be sent to the cloud.")
            print(f"Only this redacted text would be sent ({len(prompt):,} chars):\n")
            print(prompt[:1000] + ("\n[...]" if len(prompt) > 1000 else ""))
            send = args.yes or input("\nSend the redacted text and question to Gemini? [y/N] ").strip().lower() == "y"
            if send:
                try:
                    answer = step(f"3. Cloud answer ({CLOUD_MODEL}, redacted text only)", ask_cloud, prompt)
                    answered_by = f"{CLOUD_MODEL} (cloud, redacted text only)"
                except Exception as err:
                    print(f"Cloud failed ({err}), answering locally instead.")

    if answer is None:
        if is_pdf:
            prompt = f"Answer the question using this document.\n\nDocument:\n{text}\n\nQuestion: {args.question}"
            answer = step(f"3. Local answer ({LOCAL_MODEL})", ask_local, prompt)
        else:
            answer = step(f"3. Local answer ({LOCAL_MODEL})", ask_local, args.question, images=[str(args.file)])
        answered_by = f"{LOCAL_MODEL} (local)"

    print(f"\n=== Answer from {answered_by} ===\n{answer}")


if __name__ == "__main__":
    main()
