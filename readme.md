# 🔍 Independent Contact Validation Engine

## 📌 Project Overview
This Python-based validation engine performs a multi-dimensional audit of B2B contact records to verify their accuracy and legitimacy. It ingests structured data (CSV), evaluates it against **6 Mandatory Dimensions** (Email, Role, Account, Freshness, Geography, External), and generates an **Independent Accuracy Confidence Score (0–100)**.

The engine also performs a **Vendor Audit**, comparing its independent findings against the third-party vendor's provided score to flag if the data is "Aligned," "Overstated," or "Understated."

---

## 🚀 Features & Capabilities
* **Auto-Cleaning:** Automatically detects and removes empty/blank rows from the input CSV to ensure accurate record counts.
* **Weighted Scoring:** Calculates a 0-100 score based on a custom weighted validation logic.
* **NLP Title Classification:** Uses Regex-based Natural Language Processing to classify job titles (Executive, Director, Manager) and verify buyer personas.
* **Real-Time Validation:**
    * **Pings Websites:** Checks if the company website is live (HTTP 200).
    * **Geo-Matching:** Compares Contact State vs. Company HQ State.
* **Portable Design:** Runs anywhere without hardcoded paths; automatically finds the input file in the local directory.

---

## 📂 Project Structure
Ensure your folder contains these 4 files:

1.  **`main.py`**: The orchestrator that reads the CSV, cleans data, runs the logic, and saves the JSON report.
2.  **`validators.py`**: The logic module containing the 6 validation checks.
3.  **`engine.py`**: The scoring module that applies weights and determines confidence bands.
4.  **`sample-data.csv`**: Your input dataset.

---

## ⚙️ Setup & Installation

**1. Requirements**
* Python 3.x installed.

**2. Install Libraries**
This project uses `pandas` for data handling and `requests` for website verification. Open your terminal and run:
`pip install pandas requests`

---

## 🏃‍♂️ How to Run

1.  Place your **`sample-data.csv`** file in the same folder as the Python scripts.
2.  Open your terminal in that folder.
3.  Run the engine:
    `python main.py`
4.  Open **`validation_results.json`** to view your full audit report.

---

## 🏗️ Codebase & Function Explanation

The project uses **Clean Architecture**, separating the data processing, scoring logic, and validation rules into three modular files.

### 1. `validators.py` (The Rules Engine)
Contains the core logic for the 6 validation dimensions.

**Class: `IdentityValidator`**
* **`check_email(email, website)`**: Penalizes scores heavily if a personal provider (Gmail/Yahoo) is used. Compares the email domain to the company website, penalizing for a mismatch.
* **`check_role(title, department)`**: Uses NLP Regex patterns to scan the job title. Awards full points for senior keywords (VP, Chief, Director), confirming the individual is a plausible buyer.
* **`check_external(website, contact_name, company_name)`**: Makes a live HTTP request to ping the company website. If it returns a 200 OK status, it awards points. Includes an architectural setup to ingest a LinkedIn verification API.

**Class: `AccountValidator`**
* **`check_hierarchy(parenting_level)`**: Checks if the contact is mapped to a "Top Parent" (100 pts) or a "Child" subsidiary (90 pts).
* **`check_freshness(notice_date, phone)`**: Evaluates data staleness. If the data lacks a recent update timestamp, it assumes the data is stale and reduces the score.
* **`check_geography(person_state, company_state)`**: Normalizes and compares the state of the contact against the state of the company HQ. Matches receive 100 points; mismatches receive a caution flag.

### 2. `engine.py` (The Scoring Framework)
**Class: `ScoringEngine`**
* **`calculate_final_score(scores, vendor_score)`**: 
  1. Multiplies the raw score from each validation function by its defined weight to calculate a final **0–100 Confidence Score**.
  2. Assigns a **Confidence Band**: High (80-100), Medium (55-79), or Low (<55).
  3. Calculates **Vendor Alignment**: Compares the final score to the provided Vendor Score to flag "Overstated" or "Understated" vendor claims.

### 3. `main.py` (The Orchestrator)
* **`run_portable_audit(csv_path, json_output_path)`**: Uses Pandas `dropna()` to automatically discard empty rows at the bottom of CSV files. Iterates through every valid record, passes data to the validators, and writes the entire audited dataset into a clean JSON file.

---

## 📊 Scoring Logic (The Math)

| Dimension | Weight | Description |
| :--- | :--- | :--- |
| **Email Credibility** | **25%** | Domain match & corporate vs. personal email providers. |
| **Role Legitimacy** | **20%** | Seniority (VP/Director) matches department context. |
| **Account Consistency** | **15%** | Parent vs. Subsidiary hierarchy mapping. |
| **Freshness** | **15%** | Recent "Notice Date" and direct phone numbers. |
| **Geographic Plausibility** | **15%** | Matches Person State to Company State. |
| **External Confirmation** | **10%** | Pings website status & verifies LinkedIn logic. |

---

## 📝 Sample Output (JSON)
Each record in the output includes a human-readable **Explanation**:

```json
{
    "Contact_Name": "Aline Casanova",
    "Company_Name": "Stonal",
    "Accuracy_Score": "75/100",
    "Confidence_Band": "Medium",
    "Vendor_Alignment": "Aligned",
    "Explanation": "Risk: No email provided. Signal: Head of Customer Success recognized as Executive in Sales. Signal: Verified Ultimate Parent entity. Signal: Data is fresh with contact details. Signal: Contact location (Ile-de-France) aligns with HQ. Signal: Website is active (HTTP 200). | LinkedIn verified via assumed API for Aline Casanova at Stonal."
}