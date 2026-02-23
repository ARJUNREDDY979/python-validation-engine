class ScoringEngine:
    def __init__(self):
        # Weights for all 6 client requirements (Totals 1.0 or 100%)
        self.weights = {
            "email": 0.25, 
            "role": 0.20, 
            "account": 0.15, 
            "freshness": 0.15,
            "geo": 0.15,
            "external": 0.10
        }

    def calculate_final_score(self, scores, vendor_score):
        """Calculates 0-100 score and Vendor Alignment Status."""
        
        # 1. Calculate the math based on the weights above
        final_score = round(sum(scores[k] * self.weights[k] for k in self.weights))
        
        # 2. Assign Confidence Band based on the final score
        if final_score >= 80: 
            band = "High"
        elif final_score >= 55: 
            band = "Medium"
        else: 
            band = "Low"
        
        # 3. Perform the Vendor Audit Logic
        alignment = "Aligned"
        if vendor_score is not None and str(vendor_score).lower() != 'nan':
            try:
                v_score = float(vendor_score)
                # If vendor claims a score >15 points higher than what we calculated
                if (v_score - final_score) > 15: 
                    alignment = "Overstated"
                # If vendor claims a score >15 points lower than what we calculated
                elif (v_score - final_score) < -15: 
                    alignment = "Understated"
            except ValueError: 
                # Failsafe in case the vendor score is corrupted text instead of a number
                alignment = "Unknown"
                
        return final_score, band, alignment