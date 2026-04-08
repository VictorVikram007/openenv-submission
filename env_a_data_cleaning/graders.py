# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\graders.py
import pandas as pd
from io import StringIO

class NullFillingGrader:
    def score(self, cleaned_csv: str, ground_truth_csv: str) -> float:
        try:
            cleaned_df = pd.read_csv(StringIO(cleaned_csv))
            truth_df = pd.read_csv(StringIO(ground_truth_csv))
            
            # This is a simplified check. A real scenario would be more complex.
            # We assume the agent doesn't add/remove rows/columns.
            if cleaned_df.shape != truth_df.shape:
                return 0.0

            # Compare where original had nulls
            original_dirty_df, _ = pd.read_csv(StringIO(ground_truth_csv)), pd.read_csv(StringIO(ground_truth_csv)) # Rerun generator to get original state
            # This is a placeholder for a more complex logic to get the original dirty df
            # For this hackathon, we'll just compare to the final clean one.
            
            comparison = (cleaned_df == truth_df)
            return comparison.values.mean()

        except Exception:
            return 0.0

class TypeCoercionGrader:
    def score(self, cleaned_csv: str, ground_truth_csv: str) -> float:
        try:
            cleaned_df = pd.read_csv(StringIO(cleaned_csv))
            truth_df = pd.read_csv(StringIO(ground_truth_csv))

            type_score = 0.5 * (cleaned_df.dtypes.equals(truth_df.dtypes))
            
            # Drop duplicates and compare row count
            cleaned_deduped = cleaned_df.drop_duplicates()
            truth_deduped = truth_df.drop_duplicates()
            
            dedup_score = 0.0
            if len(cleaned_deduped) == len(truth_deduped):
                dedup_score = 0.5

            return type_score + dedup_score
        except Exception:
            return 0.0

class FullQAPipelineGrader:
    def score(self, cleaned_csv: str, issues_report: list[str], ground_truth_csv: str) -> float:
        try:
            cleaned_df = pd.read_csv(StringIO(cleaned_csv))
            truth_df = pd.read_csv(StringIO(ground_truth_csv))
            
            weights = {
              "nulls_fixed": 0.25,
              "types_fixed": 0.20,
              "duplicates_removed": 0.20,
              "outliers_handled": 0.20,
              "integrity_fixed": 0.15
            }
            
            total_score = 0.0
            
            # Simplified scoring for brevity
            if cleaned_df.isnull().sum().sum() == 0:
                total_score += weights["nulls_fixed"]
                
            if cleaned_df.dtypes.equals(truth_df.dtypes):
                total_score += weights["types_fixed"]
                
            if len(cleaned_df.drop_duplicates()) == len(truth_df):
                 total_score += weights["duplicates_removed"]

            # Placeholder for outlier and integrity checks
            total_score += weights["outliers_handled"] * 0.5 # Partial credit
            total_score += weights["integrity_fixed"] * 0.5 # Partial credit

            return min(total_score, 1.0)
        except Exception:
            return 0.0
