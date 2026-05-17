import unittest

from scripts.orchestrator.feature_catalog import (
    SUBJECT_FEATURES,
    build_subject_feature_directive,
    get_subject_features,
    total_feature_count,
)


class FeatureCatalogTests(unittest.TestCase):
    def test_subject_feature_counts_match_contract(self):
        self.assertEqual(len(SUBJECT_FEATURES["physics"]), 100)
        self.assertEqual(len(SUBJECT_FEATURES["mathematics"]), 100)
        self.assertEqual(len(SUBJECT_FEATURES["chemistry"]), 100)
        self.assertEqual(len(SUBJECT_FEATURES["economics"]), 200)

    def test_total_feature_count_is_500(self):
        self.assertEqual(total_feature_count(), 500)

    def test_get_subject_features(self):
        self.assertEqual(len(get_subject_features("physics")), 100)
        self.assertEqual(len(get_subject_features("economics")), 200)
        self.assertEqual(get_subject_features("unknown"), [])

    def test_build_subject_feature_directive(self):
        directive = build_subject_feature_directive("physics", mode="question_solving", max_items=12)
        self.assertIn("SUBJECT FEATURE PACK (PHYSICS)", directive)
        self.assertIn(f"{total_feature_count()}-feature catalog", directive)

        bullet_count = sum(1 for line in directive.splitlines() if line.strip().startswith("- "))
        self.assertLessEqual(bullet_count, 12)
        self.assertGreater(bullet_count, 0)

    def test_economics_feature_entries_are_unique(self):
        features = SUBJECT_FEATURES["economics"]
        self.assertEqual(len(features), len(set(features)))


if __name__ == "__main__":
    unittest.main()
