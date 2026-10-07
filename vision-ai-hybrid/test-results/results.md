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
| D re-run | e26449d | bank_statement.pdf | What was my closing balance? | local (keyword "What was my") | 65.5 s | 30.3 s | gemma3:4b (local) |
| E | e26449d | bank_statement.pdf | Group my spending by category and suggest a monthly budget | cloud (keyword "suggest"), answered `y` | 64.3 s | 8.5 s | gemini-2.5-flash-lite (cloud, redacted text only) |
| F | e26449d | bank_statement.pdf | Same as E, `--route local` | local (forced with --route) | 66.1 s | 121.5 s | gemma3:4b (local) |
| G | e26449d | bank_statement.pdf | Is account 004821937552 at risk of going overdrawn next month, and how would that affect my credit score? | local (gemma3's pick) | 78.9 s | 58.0 s | gemma3:4b (local) |
| G re-run | f6275b2 | bank_statement.pdf | Same as G, `--route cloud` | cloud (forced with --route), answered `n` | 70.8 s | 73.7 s | gemma3:4b (local) |
| H | f6275b2 | image_3.jpg | Who wrote this book and what is it about? | cloud (gemma3's pick) | 167.7 s | 43.9 s | gemini-2.5-flash-lite (cloud, whole file) |
| I | f6275b2 | image_3.jpg | Same as H, with a bad API key | cloud (gemma3's pick), cloud failed | 13.4 s | 168.2 s | gemma3:4b (local, fallback) |

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

## Test D re-run: bank statement, closing balance

Code: `e26449d`

```powershell
python hybrid.py ..ilesank_statement.pdf "What was my closing balance?"
```

[Screenshot](screenshots/test_d2_bank_closing_balance.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,264 chars)
Page 2: text layer (1,102 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(65.5s)
Summary: This document is a checking account statement for the period September 1, 2026 - September 30,
2026. It details the opening balance, deposits, withdrawals, and the final closing balance. The statement
includes a list of transactions made during the period, categorized by date, description, amount, and
balance. The account holder's information, including mailing address and contact details, is also provided.
Private info: YES. Redacted: ID NUMBER x3, PHONE x2, EMAIL x1, BANK ACCOUNT x1
Route: local ("What was my" is a lookup question, which stays local)

--- 3. Local answer (gemma3:4b) ---
(30.3s)

=== Answer from gemma3:4b (local) ===
According to the document, Jordan A. Rivera's closing balance was $5,655.42.
```

The screenshot is cut off below the first line of the answer.

**Notes:**

## Test E: bank statement, spending by category and budget

Code: `e26449d`

```powershell
python hybrid.py ..ilesank_statement.pdf "Group my spending by category and suggest a monthly budget"
```

Screenshots: [1](screenshots/test_e_bank_budget_1.png), [2](screenshots/test_e_bank_budget_2.png), [3](screenshots/test_e_bank_budget_3.png), [4](screenshots/test_e_bank_budget_4.png), [5](screenshots/test_e_bank_budget_5.png), [6](screenshots/test_e_bank_budget_6.png), [7](screenshots/test_e_bank_budget_7.png), [8](screenshots/test_e_bank_budget_8.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,264 chars)
Page 2: text layer (1,102 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(64.3s)
Summary: This statement details the transactions for an Everyday Checking Account held by Jordan A. Rivera
from September 1, 2026, to September 30, 2026. The account opened with a balance of $3,482.17 and
experienced several deposits, primarily from Brightline Software Inc. and ATM withdrawals. Various
purchases were made, including groceries, subscriptions, and utilities. The statement concludes with a
closing balance of $5,655.42 and a small interest earned.
Private info: YES. Redacted: ID NUMBER x4, PHONE x2, EMAIL x1
Route: cloud (the question asks to "suggest", which always goes to the cloud)

The file has private info, so it will NOT be sent to the cloud.
Only this redacted text would be sent (2,532 chars):

Document (private details replaced with tags like [PHONE]):
--- Page 1 ---
Northfield Community Bank
PO Box 4100, Springfield, IL 62705 | Customer service [PHONE]
Checking Account Statement
Account holder   Jordan A. Rivera
Mailing address   742 Maple Grove Lane, Apt 5B, Springfield, IL 62704
Phone   [PHONE]
Email   [EMAIL]
Account type   Everyday Checking
Account number   [ID NUMBER]
Routing number   [ID NUMBER]
Debit card   [ID NUMBER]
Statement period   September 1, 2026 - September 30, 2026
Summary
Opening balance   Deposits   Withdrawals   Closing balance
$3,482.17   $5,751.92   $3,578.67   $5,655.42
Transactions
Date   Description   Amount   Balance
09/01   Opening balance   3,482.17
09/01   Rent payment - Oakwood Apartments   -1,650.00   1,832.17
09/01   Payroll deposit - Brightline Software Inc   +2,875.40   4,707.57
09/02   Whole Foods Market   -86.42   4,621.15
09/03   Starbucks   -6.75   4,614.40
09/03   Netflix subscription   -15.49   4,598.91
09/04   Shell gas station   -4
[...]

Send the redacted text and question to Gemini? [y/N] y

--- 3. Cloud answer (gemini-2.5-flash-lite, redacted text only) ---
(8.5s)
```

The answer (from `gemini-2.5-flash-lite (cloud, redacted text only)`) has two parts. "Spending by Category
(September 2026)" groups the transactions into Food & Dining, Subscriptions & Recurring Bills, Shopping &
Entertainment, Personal & Miscellaneous, Savings & Investments and Income, with totals. "Suggested Monthly
Budget" covers income, essential expenses, discretionary spending and savings, followed by "Key
Observations and Recommendations" and "How to Use This Budget". Full text in screenshots 3 to 8.

**Notes:**

## Test F: bank statement, spending by category and budget, forced local

Code: `e26449d`

```powershell
python hybrid.py ..ilesank_statement.pdf "Group my spending by category and suggest a monthly budget" --route local
```

Screenshots: [1](screenshots/test_f_bank_budget_local_1.png), [2](screenshots/test_f_bank_budget_local_2.png), [3](screenshots/test_f_bank_budget_local_3.png), [4](screenshots/test_f_bank_budget_local_4.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,264 chars)
Page 2: text layer (1,102 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(66.1s)
Summary: This statement details the transactions for an Everyday Checking Account held by Jordan A. Rivera
from September 1, 2026, to September 30, 2026. The account opened with a balance of $3,482.17 and
experienced several deposits, primarily from Brightline Software Inc. and ATM withdrawals. Various
purchases were made, including groceries, subscriptions, and utilities. The statement concludes with a
closing balance of $5,655.42 and a small interest earned.
Private info: YES. Redacted: ID NUMBER x4, PHONE x2, EMAIL x1
Route: local (forced with --route)

--- 3. Local answer (gemma3:4b) ---
(121.5s)
```

The answer (from `gemma3:4b (local)`) has a "Spending Category Breakdown (September 2026)" with Food & Drink,
Utilities & Bills, Transportation, Entertainment, Shopping and Other, listing transactions with dates; a
"Suggested Monthly Budget" with a range per category and a total estimate of $1300 - $2000; and "Important
Notes". Full text in screenshots 2 to 4.

**Notes:**

## Test G: bank statement, account number typed in the question

Code: `e26449d`

```powershell
python hybrid.py ..ilesank_statement.pdf "Is account 004821937552 at risk of going overdrawn next month, and how would that affect my credit score?"
```

Screenshots: [1](screenshots/test_g_bank_overdraft_1.png), [2](screenshots/test_g_bank_overdraft_2.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,264 chars)
Page 2: text layer (1,102 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(78.9s)
Summary: This document is a checking account statement for an Everyday Checking account. It details the
account holder's transactions and balances over the period from September 1, 2026, to September 30, 2026.
The statement shows opening and closing balances, as well as a list of deposits and withdrawals. The
account type is Everyday Checking and the account number is [ID NUMBER]. The routing number is [ID NUMBER].
Private info: YES. Redacted: ID NUMBER x2, PHONE x2, EMAIL x1, BANK ACCOUNT x2
Route: local (The question asks about the account's risk of going overdrawn and its effect on the credit
score, which can be answered by directly examining the provided transaction data.)

--- 3. Local answer (gemma3:4b) ---
(58.0s)
```

The answer (from `gemma3:4b (local)`) covers "Risk of Overdraft" (recent withdrawals, balance of $5,655.42 on
September 30, 2026, no large scheduled withdrawals shown), "How Overdraft Could Affect Credit Score", and ends
with a disclaimer that it is not financial advice. Full text in screenshot 2.

The route was local, so the question-redaction step (which only runs for the cloud) was not exercised.

**Notes:** Did not go to the cloud. The local model's answer feels right here, and it added a disclaimer.

## Test G re-run: bank statement, account number in the question, forced cloud

Code: `f6275b2`

```powershell
python hybrid.py ..ilesank_statement.pdf "Is account 004821937552 at risk of going overdrawn next month, and how would that affect my credit score?" --route cloud
```

Screenshots: [1](screenshots/test_g2_bank_overdraft_cloud_1.png), [2](screenshots/test_g2_bank_overdraft_cloud_2.png), [3](screenshots/test_g2_bank_overdraft_cloud_3.png), [4](screenshots/test_g2_bank_overdraft_cloud_4.png)

```
--- 1. Local read (no AI for text pages) ---
Page 1: text layer (1,264 chars)
Page 2: text layer (1,102 chars)
(0.0s)

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(70.8s)
Summary: This document is a checking account statement for an Everyday Checking account. It details the
account holder's transactions and balances over the period from September 1, 2026, to September 30, 2026.
The statement shows opening and closing balances, as well as a list of deposits and withdrawals. The
account type is Everyday Checking and the account number is [ID NUMBER]. The routing number is [ID NUMBER].
Private info: YES. Redacted: ID NUMBER x2, PHONE x2, EMAIL x1, BANK ACCOUNT x2, ADDRESS x2
Route: cloud (forced with --route)
Question redacted for the cloud: Is account [ID NUMBER] at risk of going overdrawn next month, and how would
that affect my credit score?

The file has private info, so it will NOT be sent to the cloud.
Only this redacted text would be sent (2,517 chars):

Document (private details replaced with tags like [PHONE]):
--- Page 1 ---
Northfield Community Bank
[ADDRESS] | Customer service [PHONE]
Checking Account Statement
Account holder   Jordan A. Rivera
Mailing address   [ADDRESS]
Phone   [PHONE]
Email   [EMAIL]
Account type   Everyday Checking
Account number   [ID NUMBER]
Routing number   [ID NUMBER]
Debit card   [BANK ACCOUNT]
Statement period   September 1, 2026 - September 30, 2026
Summary
Opening balance   Deposits   Withdrawals   Closing balance
$3,482.17   $5,751.92   $3,578.67   $5,655.42
Transactions
Date   Description   Amount   Balance
09/01   Opening balance   3,482.17
09/01   Rent payment - Oakwood Apartments   -1,650.00   1,832.17
09/01   Payroll deposit - Brightline Software Inc   +2,875.40   4,707.57
09/02   Whole Foods Market   -86.42   4,621.15
09/03   Starbucks   -6.75   4,614.40
09/03   Netflix subscription   -15.49   4,598.91
09/04   Shell gas station   -48.10   4,550.81
09/05   Amazon.com   -64.99   4,485.82
09/06   C
[...]

Send the redacted text and question to Gemini? [y/N] N

--- 3. Local answer (gemma3:4b) ---
(73.7s)
```

The answer (from `gemma3:4b (local)`) covers "Risk of Overdraft" (closing balance of $5,655.42 on September
30, 2026, recent withdrawals of $400.00, $100.00 and $129.95, no immediate red flags), "Impact on Credit
Score" (overdraft fees, late payments, credit score impact), a disclaimer that it is not a financial
advisor, and questions that would help assess the risk. Full text in screenshots 3 and 4.

**Notes:**

## Test H: image, nothing private

Code: `f6275b2`

```powershell
python hybrid.py ..\images\image_3.jpg "Who wrote this book and what is it about?"
```

[Screenshot](screenshots/test_h_image_book.png)

```
--- 1. Local read: skipped for images ---

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(167.7s)
Text in image: WHERE
THE
 WILD
THING
ARE
Summary: The image is a graphic design featuring a stylized illustration of a horned creature with the text
"Where the wild things are." The text is rendered in a textured, hand-drawn style with a teal color palette
and a distressed background. The overall aesthetic evokes a sense of fantasy and adventure. The design is
likely associated with the popular children's book of the same name.
Private info: none found
Route: cloud (Determining the author and the book's content requires external knowledge beyond what can be
extracted from the image itself.)

--- 3. Cloud answer (gemini-2.5-flash-lite, whole file sent) ---
(43.9s)

=== Answer from gemini-2.5-flash-lite (cloud, whole file) ===
The book is titled "Where the Wild Things Are" and it was written by Maurice Sendak.

The book is about a young boy named Max who is sent to his room without supper for misbehaving. In his
room, a forest grows and a sea appears, allowing him to sail to an island inhabited by creatures called
"Wild Things." Max becomes their king, but eventually, he feels lonely and homesick, and returns to his
room where he finds his supper waiting for him.
```

The screenshot starts at step 1; the File / Question / model lines are not shown.

**Notes:**

## Test I: image, bad API key (fallback)

Code: `f6275b2`

```powershell
$env:GEMINI_API_KEY = "bad-key"
python hybrid.py ..\images\image_3.jpg "Who wrote this book and what is it about?"
Remove-Item Env:GEMINI_API_KEY
```

Screenshots: [1](screenshots/test_i_image_bad_key_1.png), [2](screenshots/test_i_image_bad_key_2.png)

```
File: image_3.jpg
Question: Who wrote this book and what is it about?
Local model: gemma3:4b   Cloud model: gemini-2.5-flash-lite

--- 1. Local read: skipped for images ---

--- 2. Local scan: summary, private info, route (gemma3:4b) ---
(13.4s)
Text in image: WHERE
THE
 WILD
 THINGS
ARE
Summary: The image is a graphic design featuring a stylized illustration of a horned creature with the text
"Where the wild things are." The text is rendered in a textured, hand-drawn style with a teal color palette
and a distressed background. The overall aesthetic evokes a sense of fantasy and adventure. The design
appears to be inspired by the popular children's book of the same name.
Private info: none found
Route: cloud (Determining the author and the book's content requires external knowledge beyond the
information present in the image.)

--- 3. Cloud answer (gemini-2.5-flash-lite, whole file sent) ---
Cloud failed (400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a
valid API key.', 'status': 'INVALID_ARGUMENT', ...}}), answering locally instead.

--- 3. Local answer (gemma3:4b) ---
(168.2s)

=== Answer from gemma3:4b (local) ===
The image is a poster for the book **"Where the Wild Things Are"** by Maurice Sendak.

**About the book:**

"Where the Wild Things Are" tells the story of Max, a young boy who, after being sent to bed without supper,
sails to an island populated by monstrous Wild Things. He becomes their king, has a wild rumpus, and is
ultimately loved and adored by his new subjects. However, eventually, he longs for home and returns, finding
his supper waiting for him.

It's a beloved classic that explores themes of imagination, anger, loneliness, and the comfort of returning
home.

Would you like to know more about the book or Maurice Sendak?
```

The full error message is in screenshot 1 (shortened above with `...`).

**Notes:**
