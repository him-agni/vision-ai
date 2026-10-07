# Hybrid (gemma3 + Gemini) test results

- **Date:** 2026-10-07
- **Code:** branch `hybrid-local-cloud`, commit `d5a3d66`
- **Local model:** `gemma3:4b` via Ollama, running on CPU
- **Cloud model:** `gemini-2.5-flash-lite`
- **Files:** `files/health_summary.pdf` and `files/bank_statement.pdf` (fake data), `images/image_3.jpg`
- **Screenshots:** [screenshots/](screenshots/)

## Summary

| Test | File | Question | Route | Scan time | Answer time | Answered by |
|---|---|---|---|---|---|---|
| A | health_summary.pdf | When is my follow-up appointment and with whom? | local | 134.4 s | 28.4 s | gemma3:4b (local) |
| B | health_summary.pdf | Explain my lab results in simple terms and what lifestyle changes would help | local (expected cloud) | 67.1 s | not in screenshot | gemma3:4b (local) |
| C | health_summary.pdf | Same as B, answered `n` | | | | |
| D | bank_statement.pdf | What was my closing balance? | | | | |
| E | bank_statement.pdf | Group my spending by category and suggest a monthly budget | | | | |
| F | bank_statement.pdf | Same as E, `--route local` | | | | |
| G | bank_statement.pdf | Is account 004821937552 at risk of going overdrawn next month, and how would that affect my credit score? | | | | |
| H | image_3.jpg | Who wrote this book and what is it about? | | | | |
| I | image_3.jpg | Same as H, with a bad API key | | | | |

## Test A: health summary, follow-up appointment

```powershell
python hybrid.py ..\files\health_summary.pdf "When is my follow-up appointment and with whom?"
```

[Screenshot](screenshots/test_a_health_followup.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,065 chars)
Page 2: text layer (1,235 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(134.4s)
Summary: This document is an After-Visit Health Summary for a patient named Jordan A. Rivera. The visit
occurred on September 22, 2026, and was for an annual physical exam. The patient reported fatigue,
headaches, and sleep issues, along with elevated blood pressure, cholesterol, and vitamin D levels. The
summary includes vital signs, lab results, a medication plan, and a follow-up appointment.
Private info: YES. Redacted: ID NUMBER x1, PHONE x2, ADDRESS x1, EMAIL x1, DATE OF BIRTH x1, HEALTH INSURANCE x3
Route: local (The question asks for the follow-up appointment date and with whom, which is directly
stated in the document.)

--- 3. Local answer (gemma3:4b) ---
(28.4s)

=== Answer from gemma3:4b (local) ===
Your follow-up appointment is on December 15, 2026 at 10:30 AM with Dr. Priya Nair, MD.
```

**Notes:**

## Test B: health summary, explain lab results

```powershell
python hybrid.py ..\files\health_summary.pdf "Explain my lab results in simple terms and what lifestyle changes would help"
```

Screenshots: [1](screenshots/test_b_health_labs_1.png), [2](screenshots/test_b_health_labs_2.png), [3](screenshots/test_b_health_labs_3.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,065 chars)
Page 2: text layer (1,235 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(67.1s)
Summary: This document is an after-visit health summary for a patient named Jordan Rivera, created by
Riverside Family Clinic. The visit was for an annual physical exam, and the patient reported fatigue,
headaches, and sleep problems. Lab results revealed prediabetes, elevated blood pressure, high cholesterol
levels, vitamin D deficiency, and being overweight. The plan includes lifestyle changes and a follow-up
appointment.
Private info: YES. Redacted: ID NUMBER x1, PHONE x3, EMAIL x1, ADDRESS x1, DATE OF BIRTH x1, HEALTH INSURANCE x1
  gemma3:4b also flagged HEALTH INSURANCE: 'Member ID BRH4829105736' (not redacted: not found word-for-word)
  gemma3:4b also flagged HEALTH INSURANCE: 'Group number 00731' (not redacted: not found word-for-word)
Route: local (The question requires extracting information from the provided document, specifically lab
results and the associated recommendations.)

--- 3. Local answer (gemma3:4b) ---
```

The answer (from `gemma3:4b (local)`) explains each lab value (HbA1c, fasting glucose, total, LDL and
HDL cholesterol, triglycerides, vitamin D, blood pressure), then lists lifestyle changes (diet, 150
minutes of exercise a week, home blood pressure checks, nutritionist referral, follow-up on December
15, 2026 at 10:30 AM with Dr. Nair). Full text in screenshots 2 and 3.

No y/N prompt was shown, because the route was local.

**Notes:**
