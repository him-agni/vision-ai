# How hybrid.py works

Green steps run on your computer, blue steps run in Google's cloud, and orange steps are the privacy gates.

```mermaid
flowchart TD
    IN["File + question<br/>python hybrid.py file question"] --> TYPE{"PDF or image?"}

    subgraph LOCAL["Your computer: nothing leaves"]
        TYPE -->|PDF| PAGES["1. Local read<br/>PyMuPDF pulls the text from each page<br/>first 10 pages by default, change with --pages"]
        PAGES --> HASTEXT{"Page has text?"}
        HASTEXT -->|"no, scanned page"| PAGEOCR["gemma3 reads the page as an image"]
        HASTEXT -->|yes| SCAN
        PAGEOCR --> SCAN
        TYPE -->|image| SCAN["2. Local scan: one gemma3 call<br/>reads the whole file and the question<br/>returns summary, text in image, private items, route + reason"]
        SCAN --> PRIV["Privacy check, done in code<br/>patterns: phone, email, SSN, date of birth, account and ID numbers<br/>plus gemma3's flags: addresses and other IDs, matched even across line breaks<br/>gemma3's date-of-birth flags kept only next to a birth label"]
        PRIV --> ROUTE{"Route?<br/>1. --route if given<br/>2. cloud if the question says explain, suggest, recommend,<br/>advise, compare, plan, budget, why, should, what does ... mean<br/>3. otherwise gemma3's pick"}
        ROUTE -->|local| LANS["3. gemma3 answers<br/>from the full file"]
        ROUTE -->|cloud| KEY{"GEMINI_API_KEY set?"}
        KEY -->|no| LANS
        KEY -->|yes| ISPRIV{"Private info found?"}
        ISPRIV -->|yes| PREVIEW["Print the exact redacted text<br/>Send to Gemini? y/N"]
        PREVIEW -->|n| LANS
    end

    subgraph CLOUD["Cloud: Gemini"]
        FULL["3. Gemini answers<br/>gets the whole file + redacted question"]
        RED["3. Gemini answers<br/>gets only redacted text + redacted question"]
    end

    ISPRIV -->|no| FULL
    PREVIEW -->|y| RED
    FULL -.->|error| LANS
    RED -.->|error| LANS
    LANS --> OUT["Answer, labelled with which model gave it"]
    FULL --> OUT
    RED --> OUT

    classDef local fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef cloud fill:#e3f2fd,stroke:#1565c0,color:#000
    classDef gate fill:#fff3e0,stroke:#ef6c00,color:#000
    class PAGES,PAGEOCR,SCAN,LANS local
    class FULL,RED cloud
    class PRIV,PREVIEW gate
```

## What can leave your computer

| Situation | Sent to Gemini |
|---|---|
| Route is local | Nothing |
| Route is cloud, nothing private found | The whole file + the question (with any private details in it redacted) |
| Route is cloud, private info found, you answer `y` | Only the redacted text + the redacted question. The file itself is never sent. |
| Route is cloud, private info found, you answer `n` | Nothing, gemma3 answers instead |
| No API key, or Gemini returns an error | Nothing more, gemma3 answers instead |

The route only decides *who answers*. Whether something is private is decided by the code, so a wrong route can't send a private file to the cloud.
