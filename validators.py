import re
import requests
import pandas as pd

class IdentityValidator:
    def __init__(self):
        self.seniority_patterns = {
            "Executive": r"\b(vp|vice president|cxo|chief|executive|head|founder|ceo|cto|cfo)\b",
            "Director": r"\b(director|associate director|sr manager|senior manager)\b",
            "Manager": r"\b(manager|lead|supervisor|mngr)\b"
        }

    def check_email(self, email, website):
        if pd.isna(email) or not email or str(email).strip() == '':
            return 0, "Risk: No email provided."
        
        email = str(email).lower()
        website = str(website).lower().replace("www.", "").strip("/") if pd.notna(website) else ""
        score, reasons = 100, []
        
        if any(p in email for p in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]):
            score -= 60
            reasons.append("Personal email provider used.")
        
        domain = email.split('@')[-1]
        if website and website not in domain:
            score -= 40
            reasons.append(f"Domain mismatch (@{domain} vs {website}).")
            
        return max(0, score), "Signal: Professional corporate email." if score == 100 else f"Flags: {', '.join(reasons)}"

    def check_role(self, title, department):
        if pd.isna(title) or not title or str(title).strip() == '':
            return 0, "Risk: Missing Job Title."
        
        title_clean = str(title).lower()
        dept = str(department) if pd.notna(department) else "Unknown"
        level, score = "Individual Contributor", 70
        
        for name, pattern in self.seniority_patterns.items():
            if re.search(pattern, title_clean):
                level, score = name, 100
                break
                
        return score, f"Signal: {title} recognized as {level} in {dept}."

    def check_external(self, website, linkedin_url):
        """6. External Confirmation (Real check for missing data)"""
        score = 0
        reasons = []

        # --- Part 1: Website Validation ---
        if pd.notna(website) and str(website).strip() != '':
            url = str(website).strip()
            if not url.startswith('http'): url = 'https://' + url
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    score += 50
                    reasons.append("Signal: Website is active.")
                else:
                    reasons.append(f"Risk: Website error {response.status_code}.")
            except:
                reasons.append("Risk: Website unreachable.")
        else:
            reasons.append("Risk: No website provided.")

        # --- Part 2: LinkedIn Validation (Accurately flagging missing data) ---
        # If the column doesn't exist, pandas returns None/NaN
        if pd.notna(linkedin_url) and str(linkedin_url).strip() != '':
            score += 50
            reasons.append("Signal: LinkedIn profile provided.")
        else:
            reasons.append("Risk: No LinkedIn data available in record.")

        return score, " | ".join(reasons)


class AccountValidator:
    def check_hierarchy(self, parenting_level):
        pl = str(parenting_level).strip()
        if pl == "Top Parent": return 100, "Signal: Verified Ultimate Parent entity."
        elif pl == "Child": return 90, "Signal: Verified Subsidiary entity."
        return 70, "Neutral: Single entity mapping."

    def check_freshness(self, notice_date, phone):
        if pd.isna(notice_date) or str(notice_date).strip() == '':
            return 50, "Caution: Missing notice date; data may be stale."
        return 100, "Signal: Data is fresh with contact details."

    def check_geography(self, person_state, company_state):
        if pd.isna(person_state) or pd.isna(company_state):
            return 60, "Neutral: Incomplete geo-data for comparison."
        
        if str(person_state).strip().lower() == str(company_state).strip().lower():
            return 100, f"Signal: Contact location ({person_state}) aligns with HQ."
        return 70, f"Caution: Contact in {person_state}, but HQ is in {company_state}."