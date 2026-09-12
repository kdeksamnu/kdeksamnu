from typing import Dict, Any, List

class FeatureExtractor:
    """Shared Feature Extractor for train/serve parity per Rule #32."""
    def __init__(self, feature_columns: List[str]):
        self.feature_columns = feature_columns

    def extract(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        return {col: float(raw_data.get(col, 0.0)) for col in self.feature_columns}
