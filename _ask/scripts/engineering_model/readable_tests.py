"""Read a selected test with its necessary same-revision source context."""


def read_test(root, test, source_sha, *, current_sha=None):
    """Return the selected assertion and curated setup/helper context."""
    return {"status": "unavailable", "context_status": "unavailable",
            "selector": test.get("case_id") if isinstance(test, dict) else None,
            "source_sha": None, "current_sha": None, "test_source": "",
            "context": [], "flow": None, "diagnostic": "readable test context is unavailable"}
