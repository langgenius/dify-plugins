import json
import subprocess
import sys
import unittest
from pathlib import Path

from overview_guard import Policy, decide

class OverviewRules(unittest.TestCase):
    policy = Policy(12, 20, True)

    def check(self, text, status, reason, count=None, **kwargs):
        result = decide({"id": "s1", "overview": text, **kwargs}, self.policy)
        self.assertEqual((result["decision"], result["reason"]), (status, reason))
        if count is not None:
            self.assertEqual(result["visible_count"], count)
        return result

    def test_empty_and_placeholder(self):
        self.check("   **!** ", "reject", "no_visible_content", 0)
        self.check("**TBD.**", "reject", "placeholder_only", 3)
        self.check(None, "reject", "no_visible_content", 0)

    def test_name_only_even_if_long(self):
        self.check("**GitHub Issue Triage**", "reject", "plugin_name_only", plugin_name="github-issue-triage")

    def test_strict_threshold_and_borderline(self):
        self.check("hello world", "reject", "below_minimum_visible_length", 10)
        self.check("abcdefghijkl", "review", "borderline_length", 12)
        self.check("abcdefghijklmnopqrst", "pass", "passes_overview_rule_only", 20)

    def test_short_but_informative_can_pass(self):
        self.check("Search public GitHub issues by repository and label.", "pass", "passes_overview_rule_only")

    def test_unicode_threshold(self):
        self.check("按仓库和标签查找公开问题", "review", "borderline_length", 12)
        self.check("ＡＢＣＤＥＦ", "reject", "below_minimum_visible_length", 6)

    def test_urls_images_comments_and_label(self):
        self.check("![decorative badge](https://example.test) <!-- Hidden text --> https://example.test", "reject", "no_visible_content", 0)
        self.check("[Details](https://example.test/path_(a))", "reject", "below_minimum_visible_length", 7)

    def test_complex_markup_does_not_trigger_rejection(self):
        for item in ("<div>Example</div>", "~~~text\nabc\n~~~", "[ref][example]", "# Intro\nExample", "<!-- open"):
            with self.subTest(item=item):
                self.check(item, "review", "complex_markup_requires_review")

    def test_missing_data_is_not_an_empty_overview(self):
        for item in ([], {"id": "x"}, {"id": "x", "overview": 5}, {"overview": ""}):
            self.assertEqual(decide(item, self.policy)["reason"], "invalid_submission_input")

    def test_dry_run_never_emits_reject(self):
        result = decide({"id": 1, "overview": "TBD"}, Policy(12, 20))
        self.assertEqual((result["decision"], result["proposed_decision"]), ("review", "reject"))

    def test_policy_settings_validation(self):
        with self.assertRaises(ValueError):
            Policy(12, 11)

    def test_cli_keeps_processing_after_bad_row(self):
        script = str(Path(__file__).with_name("overview_guard.py"))
        completed = subprocess.run([sys.executable, script, "--min-visible", "12", "--enforce"],
            input='not json\n{"id":"ok","overview":"TBD"}\n', text=True, capture_output=True, check=True)
        first, second = map(json.loads, completed.stdout.splitlines())
        self.assertEqual((first["reason"], second["decision"]), ("invalid_json", "reject"))
        self.assertEqual((first["line"], second["line"]), (1, 2))

if __name__ == "__main__":
    unittest.main()
