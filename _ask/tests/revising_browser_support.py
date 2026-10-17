"""Owned Streamlit and Chromium sessions for real workbench journeys."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import sys
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]


def _load_browser_dependency():
    runtime = Path(os.environ.get("ASK_TRACEABILITY_RUNTIME_ROOT", ROOT)).resolve()
    site_roots = [runtime / "_ask" / ".venv" / "lib"]
    site_roots.append(ROOT / "_ask" / ".venv" / "lib")
    for site_root in site_roots:
        for site in sorted(site_root.glob("python*/site-packages")):
            if str(site) not in sys.path:
                sys.path.insert(0, str(site))


_load_browser_dependency()

from playwright.sync_api import expect, sync_playwright  # noqa: E402

sys.path.insert(0, str(ROOT / "_ask/ui"))
from benchmark_workbench import await_http, start_server  # noqa: E402


@contextmanager
def browser_session(model_root: Path = ROOT, work_id: str = "revising-workbench", *,
                    subject: str | None = None, viewport: dict | None = None,
                    block_external: bool = False):
    """Run an owned local Streamlit server and Chromium page with teardown."""
    model_root = Path(model_root).resolve()
    process, url, _started = start_server(model_root, work_id)
    browser = context = None
    try:
        await_http(process, url)
        with sync_playwright() as playwright:
            options = {"headless": True, "args": ["--no-sandbox"]}
            channel = os.environ.get("ASK_BROWSER_CHANNEL")
            executable = (os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                          or shutil.which("google-chrome") or shutil.which("chromium"))
            if channel:
                options["channel"] = channel
            elif executable:
                options["executable_path"] = executable
            browser = playwright.chromium.launch(**options)
            context = browser.new_context(viewport=viewport or {"width": 1280, "height": 900})
            if block_external:
                context.route("**/*", lambda route: route.continue_()
                              if route.request.url.startswith(("http://127.0.0.1:", "http://localhost:"))
                              else route.abort())
            page = context.new_page()
            if subject:
                url += "?" + urlencode({"subject": subject})
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            expect(page.get_by_role("heading", name="Engineering workbench", exact=True)).to_be_visible(timeout=15000)
            yield page, browser
    finally:
        if context is not None:
            context.close()
        if browser is not None:
            browser.close()
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception:
            process.kill()
            process.wait(timeout=5)


def open_route(page, route_id: str, heading: str):
    from benchmark_workbench import _key_class
    button = page.locator(f'[class~="{_key_class("route:" + route_id)}"]').get_by_role("button")
    expect(button).to_be_visible(timeout=10000)
    button.click()
    expect(page.get_by_role("heading", name=heading, exact=False).first).to_be_visible(timeout=10000)
    return button


def git_fingerprint(root: Path) -> tuple[str, str]:
    import subprocess
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                          text=True, check=True).stdout.strip()
    refs = subprocess.run(["git", "for-each-ref", "--format=%(refname) %(objectname)"],
                          cwd=root, capture_output=True, text=True, check=True).stdout
    return head, refs


def run_existing_browser_journey(method: str):
    """Reuse a prior real browser regression as a separately named pilot case."""
    import sys
    import unittest
    sys.path.insert(0, str(ROOT / "_ask/tests"))
    from test_engineering_ui_browser import WorkbenchBrowserJourney
    suite = unittest.TestSuite([WorkbenchBrowserJourney(method)])
    result = unittest.TestResult()
    suite.run(result)
    if not result.wasSuccessful():
        messages = [str(item[1]) for item in [*result.failures, *result.errors]]
        raise AssertionError("\n".join(messages))
