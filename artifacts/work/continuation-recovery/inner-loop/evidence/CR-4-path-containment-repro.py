import importlib.util
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

root = Path.cwd()
sys.path.insert(0, str(root / "_ask/scripts"))
with TemporaryDirectory() as temporary:
    parent = Path(temporary)
    source = parent / "prior_recovery.py"
    source.write_bytes(subprocess.check_output([
        "git", "show", "a2b7522d47bfcf3c26cf8b2b1923ccd2338989c8:_ask/scripts/inner_loop/recovery.py",
    ]))
    spec = importlib.util.spec_from_file_location("prior_recovery", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checkout = parent / "repo"
    checkout.mkdir()
    (parent / "outside.json").write_text('{"fixture":true}\n')
    assert module._legacy_artifact(checkout, "HEAD", "../outside.json") == (None, "missing"), \
        "legacy checkout fallback reads outside repository"
