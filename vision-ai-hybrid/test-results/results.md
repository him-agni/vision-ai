# Hybrid (gemma3 + Gemini) test results

- **Date:** 2026-10-07
- **Code:** branch `hybrid-local-cloud`; the commit used for each run is in the Code column
- **Local model:** `gemma3:4b` via Ollama, running on CPU
- **Cloud model:** `gemini-2.5-flash-lite`
- **Files:** `files/health_summary.pdf` and `files/bank_statement.pdf` (fake data), `images/image_3.jpg`
- **Screenshots:** [screenshots/](screenshots/)

## Summary

| Test | Code | File | Question | Route | Scan time | Answer time | Answered by |
|---|---|---|---|---|---|---|---|
| A | d5a3d66 | health_summary.pdf | When is my follow-up appointment and with whom? | local | 134.4 s | 28.4 s | gemma3:4b (local) |
| A re-run | 9ff1507 | health_summary.pdf | When is my follow-up appointment and with whom? | local | 71.8 s | 20.9 s | gemma3:4b (local) |
| B | d5a3d66 | health_summary.pdf | Explain my lab results in simple terms and what lifestyle changes would help | local (expected cloud) | 67.1 s | not in screenshot | gemma3:4b (local) |
| B re-run | 9ff1507 | health_summary.pdf | Explain my lab results in simple terms and what lifestyle changes would help | cloud (keyword "Explain"), answered `y` | 63.3 s | 3.2 s | gemini-2.5-flash-lite (cloud, redacted text only) |
| C | 9ff1507 | health_summary.pdf | Same as B, answered `n` | cloud, answered `n` | not in screenshot | 68.5 s | gemma3:4b (local) |
| D | 9ff1507 | bank_statement.pdf | What was my closing balance? | cloud (expected local) | 72.4 s | not in screenshot | not in screenshot |
| E | | bank_statement.pdf | Group my spending by category and suggest a monthly budget | | | | |
| F | | bank_statement.pdf | Same as E, `--route local` | | | | |
| G | | bank_statement.pdf | Is account 004821937552 at risk of going overdrawn next month, and how would that affect my credit score? | | | | |
| H | | image_3.jpg | Who wrote this book and what is it about? | | | | |
| I | | image_3.jpg | Same as H, with a bad API key | | | | |

## Test A: health summary, follow-up appointment

Code: `d5a3d66`

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

Code: `d5a3d66`

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

## Test A re-run: health summary, follow-up appointment

Code: `9ff1507`

```powershell
python hybrid.py ..iles\health_summary.pdf "When is my follow-up appointment and with whom?"
```

[Screenshot](screenshots/test_a2_health_followup.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,065 chars)
Page 2: text layer (1,235 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(71.8s)
Summary: This document is an After-Visit Health Summary for a patient named Jordan Rivera. The visit
occurred on September 22, 2026, and was for an annual physical exam. The patient reported fatigue,
headaches, and sleep issues, along with several abnormal lab results including high HbA1c, fasting
glucose, total cholesterol, LDL cholesterol, and triglycerides, as well as a Vitamin D deficiency. A
follow-up appointment is scheduled for December 15, 2026, with Dr. Priya Nair.
Private info: YES. Redacted: ID NUMBER x1, PHONE x2, ADDRESS x1, EMAIL x1, DATE OF BIRTH x1, HEALTH INSURANCE x3
Route: local (The question asks for the follow-up appointment date and with whom, which is directly
found in the document.)

--- 3. Local answer (gemma3:4b) ---
(20.9s)

=== Answer from gemma3:4b (local) ===
Your follow-up appointment is on December 15, 2026 at 10:30 AM with Dr. Priya Nair, MD.
```

**Notes:**

## Test B re-run: health summary, explain lab results

Code: `9ff1507`

```powershell
python hybrid.py ..iles\health_summary.pdf "Explain my lab results in simple terms and what lifestyle changes would help"
```

Screenshots: [1](screenshots/test_b2_health_labs_1.png), [2](screenshots/test_b2_health_labs_2.png), [3](screenshots/test_b2_health_labs_3.png), [4](screenshots/test_b2_health_labs_4.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,065 chars)
Page 2: text layer (1,235 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(63.3s)
Summary: This document is an after-visit health summary for a patient named Jordan Rivera, created by
Riverside Family Clinic. The visit was for an annual physical exam, and the patient reported fatigue,
headaches, and sleep problems. Lab results revealed prediabetes, high blood pressure, high cholesterol
levels, vitamin D deficiency, and being overweight. The plan includes lifestyle changes and follow-up
appointments.
Private info: YES. Redacted: ID NUMBER x1, PHONE x2, ADDRESS x1, EMAIL x1, DATE OF BIRTH x1, HEALTH INSURANCE x3
Route: cloud (the question asks to "Explain", which always goes to the cloud)

The file has private info, so it will NOT be sent to the cloud.
Only this redacted text would be sent (2,444 chars):

Document (private details replaced with tags like [PHONE]):
--- Page 1 ---
Riverside Family Clinic
1200 Lakeview Drive, Suite 300, Springfield, IL 62701  |  [PHONE]
After-Visit Health Summary
Patient
Jordan A. Rivera
Date of birth
DOB: [DATE OF BIRTH]
Address
[ADDRESS]
Phone
[PHONE]
Email
[EMAIL]
SSN
[ID NUMBER]
Insurance
[HEALTH INSURANCE]
[HEALTH INSURANCE]
[HEALTH INSURANCE]
Visit date
September 22, 2026
Provider
Dr. Priya Nair, MD (Internal Medicine)
Reason for visit
Annual physical exam. Patient reports feeling more tired than usual over the past three months, occasional
afternoon headaches, and trouble sleeping. No chest pain or shortness of breath. Works a desk job, exercises
about once a week.
Vital signs
Measurement
[...]

Send the redacted text and question to Gemini? [y/N] y

--- 3. Cloud answer (gemini-2.5-flash-lite, redacted text only) ---
(3.2s)
```

The answer (from `gemini-2.5-flash-lite (cloud, redacted text only)`) explains HbA1c and fasting glucose
(prediabetes), total and LDL cholesterol and triglycerides, and vitamin D, then lists lifestyle changes:
diet (less added sugar and refined carbohydrates, more whole foods), 150 minutes of exercise a week, home
blood pressure checks, the nutritionist referral, and taking the prescribed vitamin D3. Full text in
screenshots 3 and 4.

**Notes:**

## Test C: health summary, explain lab results, cloud refused

Code: `9ff1507`

```powershell
python hybrid.py ..iles\health_summary.pdf "Explain my lab results in simple terms and what lifestyle changes would help"
```

Screenshots: [1](screenshots/test_c_health_labs_local_1.png), [2](screenshots/test_c_health_labs_local_2.png)

The screenshots start at the y/N prompt; the steps before it are not shown.

```
Send the redacted text and question to Gemini? [y/N] N

--- 3. Local answer (gemma3:4b) ---
(68.5s)
```

The answer (from `gemma3:4b (local)`) explains each lab value (HbA1c, fasting glucose, total, LDL and
HDL cholesterol, triglycerides, vitamin D, blood pressure), then lists lifestyle changes (diet, 150
minutes of exercise a week, home blood pressure checks, nutritionist referral, follow-up on December
15, 2026 at 10:30 AM with Dr. Nair), an "Important Note" about blood pressure, and ends with "Would you
like me to elaborate on any specific part of this explanation or the plan?". Full text in the screenshots.

**Notes:**

## Test D: bank statement, closing balance

Code: `9ff1507`

```powershell
python hybrid.py ..ilesank_statement.pdf "What was my closing balance?"
```

[Screenshot](screenshots/test_d_bank_closing_balance.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,154 chars)
Page 2: text layer (970 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(72.4s)
Summary: This document is a checking account statement for a customer. It details the opening balance,
deposits, withdrawals, and the final closing balance for the period of September 1, 2026, to September
30, 2026. The statement includes a list of transactions with dates, descriptions, amounts, and
corresponding balance adjustments. The account type is Everyday Checking, and the account number is
004821937552.
Private info: YES. Redacted: ID NUMBER x4, PHONE x2, EMAIL x1
Route: cloud (The question requires the final balance, which is not directly present in the file and
requires external knowledge to calculate.)

The file has private info, so it will NOT be sent to the cloud.
Only this redacted text would be sent (2,260 chars):

Document (private details replaced with tags like [PHONE]):
--- Page 1 ---
Northfield Community Bank
PO Box 4100, Springfield, IL 62705  |  Customer service [PHONE]
Checking Account Statement
Account holder
Jordan A. Rivera
Mailing address
[...]
```

The screenshot ends here; the y/N answer and the final answer are not shown.

**Notes:**
