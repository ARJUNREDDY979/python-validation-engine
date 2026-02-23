import pandas as pd
import json
import logging
import os
import sys
from validators import IdentityValidator, AccountValidator
from engine import ScoringEngine

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def run_portable_audit(csv_path, json_output_path):
    if os.path.exists(json_output_path):
        logger.info(f"Clearing previous results in {json_output_path}...")
    
    if not os.path.exists(csv_path):
        logger.error(f"Error: Could not find '{csv_path}'.")
        return

    try:
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=['First Name', 'Last Name', 'Job Title'], how='all')
        logger.info(f"Active records identified: {len(df)}")
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        return

    val_identity = IdentityValidator()
    val_account = AccountValidator()
    engine = ScoringEngine()
    final_results = []

    for index, row in df.iterrows():
        # Safely try to get LinkedIn. It will be None if the column is missing.
        linkedin_url = row.get('LinkedIn URL') 
        
        s_email, m_email = val_identity.check_email(row.get('Supplemental Email'), row.get('Website'))
        s_role, m_role = val_identity.check_role(row.get('Job Title'), row.get('Department'))
        s_acc, m_acc = val_account.check_hierarchy(row.get('Parenting Level'))
        s_fresh, m_fresh = val_account.check_freshness(row.get('Notice Provided Date'), row.get('Direct Phone Number'))
        s_geo, m_geo = val_account.check_geography(row.get('Person State'), row.get('Company State'))
        
        # Pass the (likely missing) linkedin_url to be validated
        s_ext, m_ext = val_identity.check_external(row.get('Website'), linkedin_url)
        
        scores = {
            "email": s_email, "role": s_role, "account": s_acc, 
            "freshness": s_fresh, "geo": s_geo, "external": s_ext
        }
        
        score, band, alignment = engine.calculate_final_score(scores, row.get('Contact Accuracy Score'))
        
        final_results.append({
            "Record_Row": index + 2,
            "Contact_Name": f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
            "Company_Name": str(row.get('Company Name', 'Unknown Company')),
            "Accuracy_Score": f"{score}/100",
            "Confidence_Band": band,
            "Vendor_Alignment": alignment,
            "Explanation": f"{m_email} {m_role} {m_acc} {m_fresh} {m_geo} {m_ext}"
        })

    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=4)
    
    logger.info(f"Done! {len(final_results)} records updated in {json_output_path}.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        FILE_INPUT = sys.argv[1]
    else:
        FILE_INPUT = "sample-data.csv" 
    OUTPUT_FILE = "validation_results.json"
    run_portable_audit(FILE_INPUT, OUTPUT_FILE)