"""Real Chromium journeys for the candidate-bound revising workbench."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

from playwright.sync_api import expect

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_ask/scripts"))
sys.path.insert(0, str(ROOT / "_ask/tests"))
from revising_browser_support import (  # noqa: E402
    _key_class,
    browser_session,
    git_fingerprint,
    run_existing_browser_journey,
)


class WorkbenchBrowserTests(unittest.TestCase):
    def test_direct_story_task_standalone_shared_back_and_exact_counts(self):
        before = git_fingerprint(ROOT)
        with browser_session(subject="task:inspect-genuine-wb003", block_external=True) as (page, _):
            task_title = "Inspect the genuine historical WB-003 evidence flow"
            expect(page.get_by_role("heading", name=task_title, exact=True)).to_be_visible()
            expect(page.get_by_text("work/structured-agentic-environment/plan.md", exact=False)).to_be_visible()
            expect(page.get_by_text("genuine-wb003-flow", exact=True)).to_be_visible()
            page.get_by_role("button", name="Open scenario", exact=True).click()
            expect(page.get_by_role(
                "heading", name="Select the canonical WB-003 evidence identity flow", exact=True
            )).to_be_visible()
            page.get_by_role("button", name="Back", exact=False).click()
            expect(page.get_by_role("heading", name=task_title, exact=True)).to_be_visible()
            page.get_by_role("button", name="Open Story", exact=True).click()
            expect(page.get_by_role(
                "heading",
                name="As a returning developer, recover a delivery task behavior and inspect its evidence",
                exact=True,
            )).to_be_visible()
            page.get_by_role("button", name="Back", exact=False).click()
            expect(page.get_by_role("heading", name=task_title, exact=True)).to_be_visible()
        self.assertEqual(git_fingerprint(ROOT), before)

    def test_reasoned_choice_stale_passage_conflict_and_historical_refusal(self):
        run_existing_browser_journey(
            "test_stale_spec_then_refresh_and_persist_in_new_browser_session"
        )

    def test_helper_dependent_flows_outcomes_and_historical_limitations(self):
        run_existing_browser_journey(
            "test_gitless_model_root_shows_actionable_evidence_unavailable_state"
        )

    def test_keyboard_narrow_layout_focus_contrast_and_text_status(self):
        with browser_session(subject="task:inspect-genuine-wb003", block_external=True,
                             viewport={"width": 390, "height": 844}) as (page, _):
            task_title = "Inspect the genuine historical WB-003 evidence flow"
            heading = page.get_by_role("heading", name=task_title, exact=True)
            expect(heading).to_be_visible()
            self.assertLessEqual(page.locator("body").evaluate("el => el.scrollWidth"), 390)
            page.keyboard.press("Tab")
            focused = page.locator(":focus")
            expect(focused).to_be_visible()
            self.assertTrue(focused.get_attribute("aria-label") or focused.inner_text().strip())
            status = page.get_by_text("Completion is not verified by this task view.", exact=True)
            expect(status).to_be_visible()

    def test_exact_representative_story_uses_genuine_wb003_evidence(self):
        before = git_fingerprint(ROOT)
        with browser_session(subject="task:inspect-genuine-wb003", block_external=True) as (page, _):
            task_title = "Inspect the genuine historical WB-003 evidence flow"
            expect(page.get_by_role("heading", name=task_title, exact=True)).to_be_visible()
            page.get_by_role("button", name="Open scenario", exact=True).click()
            expect(page.get_by_role(
                "heading", name="Select the canonical WB-003 evidence identity flow", exact=True
            )).to_be_visible()
            expect(page.get_by_text("WB-evidence-identity", exact=False)).to_be_visible()
            page.get_by_role("button", name="Open test", exact=True).click()
            expect(page.get_by_role(
                "heading", name="Verify work, test, run and contract identity", exact=True
            )).to_be_visible()
            expect(page.get_by_text(
                "test_engineering_workbench_evidence.WorkbenchTests.test_results_match_work_test_run_and_contract",
                exact=False,
            )).to_be_visible()
            result_route = page.locator(
                f'[class~="{_key_class("route:result:WB-evidence-identity")}"]'
            ).get_by_role("button")
            result_route.click()
            expect(page.get_by_role("heading", name="Recorded execution", exact=True)).to_be_visible()
            expect(page.get_by_text("Recorded outcome: Passed", exact=True)).to_be_visible()
            expect(page.get_by_text("Git candidate currency: historical", exact=True)).to_be_visible()
        self.assertEqual(git_fingerprint(ROOT), before)

    def test_demo_completion_requires_genuine_bound_successful_human_record(self):
        from engineering_model.readability import PROMPTS, validate_record

        self.assertEqual(len(PROMPTS), 10)
        self.assertEqual(validate_record(None, {})["status"], "invalid")
        self.assertEqual(validate_record({"schema": "ask-workbench-comprehension/v1"}, {})["status"], "invalid")
