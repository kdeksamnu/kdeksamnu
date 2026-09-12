import unittest
from src.mlaos_features.feature_extractor import FeatureExtractor
from src.mlaos_infra.skew_auditor import calculate_psi
from src.mlaos_infra.serving_logger import log_feature_serving

class TestSovereignUnit(unittest.TestCase):
    def test_feature_extractor(self):
        extractor = FeatureExtractor(["col_a", "col_b"])
        res = extractor.extract({"col_a": "10", "col_b": "20.5"})
        self.assertEqual(res["col_a"], 10.0)
        self.assertEqual(res["col_b"], 20.5)

    def test_psi_calculation(self):
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]
        actual = [1.1, 1.9, 3.2, 4.1, 5.0]
        psi = calculate_psi(expected, actual)
        self.assertIsInstance(psi, float)

    def test_serving_logger(self):
        try:
            log_feature_serving("test_feat_01", {"val": 1.0})
        except Exception as e:
            self.fail(f"log_feature_serving raised Exception: {e}")

if __name__ == "__main__":
    unittest.main()
